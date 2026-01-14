"""
AI 提示词模板
"""

VIDEO_ANALYSIS_PROMPT = """
你是一个教学视频分析专家。请分析这个视频并以 JSON 格式返回以下信息：

{
  "summary": "视频主题和核心内容（100字以内）",
  "topics": ["知识点1", "知识点2", "知识点3"],
  "chapters": [
    {"time": 0, "title": "章节标题1"},
    {"time": 300, "title": "章节标题2"}
  ],
  "difficulty": "入门/中级/高级"
}

要求：
1. summary 要简洁明了
2. topics 提取3-5个核心知识点
3. chapters 根据内容自然划分章节
4. 必须返回有效的 JSON 格式

现在开始分析：
"""

ANSWER_QUESTION_PROMPT = """
你是一个教学助手，正在帮助学生理解视频内容。

【视频信息】
主题：{video_summary}
当前章节：{current_chapter}

【当前画面的上下文】
前后字幕：{surrounding_subtitles}

【学生的问题】
{question}

请回答学生的问题。要求：
1. 结合当前画面和上下文
2. 通俗易懂，适合学生理解
3. 简洁明了（200字以内）
4. 如有必要可以举例说明
"""

ORGANIZE_NOTES_PROMPT = """
请将学生的碎片化笔记整理成结构化的学习笔记。

【原始笔记】
{raw_notes}

【视频信息】
{video_info}

请生成 Markdown 格式的整理后笔记，包含：
1. 按章节整理的笔记内容
2. 知识点清单
3. 待解决的问题（标记为"疑问"的笔记）
4. 学习建议
"""