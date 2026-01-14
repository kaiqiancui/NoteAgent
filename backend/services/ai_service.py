"""
AI 服务 - 处理 AI 相关业务
"""
import sys
from pathlib import Path
from typing import AsyncIterator, Dict

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))
from core.ai_client import AIClient
from core.transcript_gen import TranscriptGenerator
from storage import Storage

class AIService:
    """AI 服务"""

    def __init__(self):
        self.ai_client = AIClient()

    async def answer_question(
        self,
        video_id: str,
        timestamp: float,
        question: str,
        frame_base64: str
    ) -> AsyncIterator[str]:
        """
        回答用户问题（流式）
        """
        # 1. 获取视频信息
        video = Storage.get_video(video_id)
        if not video:
            yield "错误：视频不存在"
            return

        # 2. 构建上下文
        context = self._build_context(video, timestamp)

        # 3. 调用 AI（流式返回）
        async for chunk in self.ai_client.answer_question(
            question, frame_base64, context
        ):
            yield chunk

    def _build_context(self, video: dict, timestamp: float) -> Dict:
        """构建上下文信息"""
        analysis = video.get("analysis", {})
        transcript = video.get("transcript", [])

        # 获取前后字幕
        surrounding_subtitles = TranscriptGenerator.get_surrounding_text(
            transcript, timestamp
        )

        # 判断当前章节
        current_chapter = self._get_current_chapter(analysis, timestamp)

        return {
            "summary": analysis.get("summary", ""),
            "chapter": current_chapter,
            "subtitles": surrounding_subtitles
        }

    @staticmethod
    def _get_current_chapter(analysis: dict, timestamp: float) -> str:
        """根据时间戳判断当前章节"""
        chapters = analysis.get("chapters", [])
        if not chapters:
            return "无"

        # 找到最近的章节
        current = "无"
        for chapter in chapters:
            if chapter["time"] <= timestamp:
                current = chapter["title"]
            else:
                break

        return current
