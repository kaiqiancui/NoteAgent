"""
AI 客户端 - 使用 requests 调用自定义 API（OpenAI 兼容格式）
"""
import sys
from pathlib import Path
from typing import AsyncIterator, List, Dict
import json
import requests

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))
import config
from core.prompts import VIDEO_ANALYSIS_PROMPT, ANSWER_QUESTION_PROMPT

class AIClient:
    """AI 客户端 - 使用 requests 调用"""

    def __init__(self):
        self.api_key = config.API_KEY
        self.api_url = config.API_BASE_URL
        self.model = config.AI_MODEL

        if not self.api_key:
            print("警告: API_KEY 未设置，AI 功能将无法使用")

    def analyze_video(
        self,
        keyframes: List[Dict],
        transcript_text: str
    ) -> Dict:
        """
        分析视频内容
        返回：{"summary": "...", "topics": [...], "chapters": [...]}
        """
        if not self.api_key:
            return self._get_mock_analysis()

        # 先尝试使用视觉分析（带图片）
        try:
            print("正在尝试使用视觉分析（图片+文本）...")
            result = self._analyze_with_vision(keyframes, transcript_text)

            # 检查结果是否有效
            if result and "summary" in result and len(result["summary"]) > 20:
                # 检查是否是错误消息
                if "抱歉" not in result["summary"] and "无法" not in result["summary"]:
                    print("✅ 视觉分析成功")
                    return result
                else:
                    print("⚠️ 视觉分析返回错误消息，切换到文本分析")
            else:
                print("⚠️ 视觉分析结果无效，切换到文本分析")

        except Exception as e:
            print(f"⚠️ 视觉分析失败: {e}，切换到文本分析")

        # 回退：仅使用文本分析
        try:
            print("正在使用纯文本分析...")
            return self._analyze_with_text_only(transcript_text)

        except Exception as e:
            print(f"❌ 文本分析也失败: {e}")
            return self._get_mock_analysis()

    def _analyze_with_vision(
        self,
        keyframes: List[Dict],
        transcript_text: str
    ) -> Dict:
        """使用视觉模型分析（图片+文本）"""
        # 构建消息内容
        content = [
            {"type": "text", "text": VIDEO_ANALYSIS_PROMPT}
        ]

        # 添加关键帧图片（base64 格式）
        for frame in keyframes:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{frame['data']}"
                }
            })

        # 添加字幕（限制长度）
        content.append({
            "type": "text",
            "text": f"视频字幕内容：\n{transcript_text[:3000]}"
        })

        # 调用 API
        response = requests.post(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.TEMPERATURE
            },
            timeout=60
        )

        if response.status_code != 200:
            print(f"API 调用失败: {response.status_code} - {response.text}")
            raise Exception(f"API error: {response.status_code}")

        # 解析响应
        result = response.json()
        result_text = result['choices'][0]['message']['content']
        print(f"API 返回: {result_text[:200]}...")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # 如果不是 JSON，返回简单格式
            return {
                "summary": result_text[:500],
                "topics": [],
                "chapters": []
            }

    def _analyze_with_text_only(self, transcript_text: str) -> Dict:
        """仅使用文本分析（不包含图片）"""

        # 构建纯文本提示词
        text_prompt = f"""请分析以下视频的字幕内容，并返回 JSON 格式的分析结果：

字幕内容：
{transcript_text[:4000]}

请返回以下格式的 JSON（必须是有效的 JSON 格式）：
{{
    "summary": "视频内容的简短总结（2-3句话）",
    "topics": ["知识点1", "知识点2", "知识点3"],
    "chapters": [
        {{"time": 0, "title": "章节标题"}}
    ],
    "difficulty": "基础/中级/高级"
}}"""

        # 调用 API
        response = requests.post(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": text_prompt
                    }
                ],
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.TEMPERATURE
            },
            timeout=60
        )

        if response.status_code != 200:
            print(f"API 调用失败: {response.status_code} - {response.text}")
            raise Exception(f"API error: {response.status_code}")

        # 解析响应
        result = response.json()
        result_text = result['choices'][0]['message']['content']
        print(f"API 返回: {result_text[:200]}...")

        try:
            # 尝试提取 JSON（可能被包裹在 ```json 代码块中）
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()

            return json.loads(result_text)
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            # 如果还是失败，返回基本格式
            return {
                "summary": result_text[:500] if len(result_text) > 0 else "无法解析视频内容",
                "topics": ["需要人工查看"],
                "chapters": [{"time": 0, "title": "视频内容"}],
                "difficulty": "未知"
            }

    async def answer_question(
        self,
        question: str,
        frame_base64: str,
        context: Dict
    ) -> AsyncIterator[str]:
        """
        回答问题（流式返回）
        context: {"summary": "...", "chapter": "...", "subtitles": "..."}
        """
        if not self.api_key:
            yield "AI 功能需要配置 API_KEY"
            return

        try:
            # 构建提示词
            prompt = ANSWER_QUESTION_PROMPT.format(
                video_summary=context.get("summary", "无"),
                current_chapter=context.get("chapter", "无"),
                surrounding_subtitles=context.get("subtitles", "无"),
                question=question
            )

            # 构建消息内容（区分是否有截图）
            if frame_base64:
                # 有截图：使用视觉模型
                content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{frame_base64}"  # 发送完整数据
                        }
                    }
                ]
                print(f"[DEBUG] 正在回答问题（带截图）: {question}")
                print(f"[DEBUG] 截图数据长度: {len(frame_base64)} 字符")
            else:
                # 无截图：纯文本模式
                content = prompt
                print(f"[DEBUG] 正在回答问题（纯文本）: {question}")

            print(f"[DEBUG] 提示词前100字符: {prompt[:100]}...")

            # 调用 API（流式）
            print(f"[DEBUG] 开始调用 API: {self.api_url}")
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": content
                        }
                    ],
                    "max_tokens": 1024,
                    "temperature": config.TEMPERATURE,
                    "stream": True  # 启用流式返回
                },
                stream=True,
                timeout=60
            )

            print(f"[DEBUG] API 响应状态码: {response.status_code}")
            print(f"[DEBUG] API 响应头: {dict(response.headers)}")

            if response.status_code != 200:
                error_msg = f"API 调用失败: {response.status_code}\n响应内容: {response.text[:500]}"
                print(f"[ERROR] {error_msg}")
                yield error_msg
                return

            # 流式解析响应
            chunk_count = 0
            total_text = ""
            print("[DEBUG] 开始接收流式响应...")

            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    print(f"[DEBUG] 原始行 #{chunk_count}: {line_text[:100]}")

                    if line_text.startswith('data: '):
                        data_text = line_text[6:]  # 去掉 "data: " 前缀

                        if data_text == '[DONE]':
                            print(f"[DEBUG] 收到结束标记，总共 {chunk_count} 个 chunk")
                            print(f"[DEBUG] 完整响应文本: {total_text}")
                            break

                        try:
                            data = json.loads(data_text)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content_chunk = delta['content']
                                    total_text += content_chunk
                                    chunk_count += 1
                                    print(f"[DEBUG] Chunk #{chunk_count}: {content_chunk}")
                                    yield content_chunk
                                else:
                                    print(f"[DEBUG] Delta 中没有 content: {delta}")
                            else:
                                print(f"[DEBUG] 响应中没有 choices: {data}")
                        except json.JSONDecodeError as e:
                            print(f"[ERROR] JSON 解析失败: {e}, 原始数据: {data_text[:200]}")
                            continue

            print(f"[DEBUG] AI 回答完成，总字符数: {len(total_text)}")

        except Exception as e:
            print(f"[ERROR] AI 回答失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"回答失败: {str(e)}"

    def _get_mock_analysis(self) -> Dict:
        """返回模拟数据"""
        return {
            "summary": "视频分析功能需要配置 API_KEY",
            "topics": ["示例知识点1", "示例知识点2"],
            "chapters": [{"time": 0, "title": "开始"}],
            "difficulty": "未知"
        }
