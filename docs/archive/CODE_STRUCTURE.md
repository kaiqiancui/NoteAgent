# 简化版代码封装结构

> **设计原则**：职责清晰、层次简单、快速实现

---

## 📁 一、项目目录结构

```
video-learning-assistant/
│
├── backend/                          # Python 后端
│   ├── main.py                       # 【入口】FastAPI 应用 + 所有路由
│   ├── config.py                     # 【配置】环境变量 + 常量配置
│   ├── storage.py                    # 【存储】JSON 文件读写
│   │
│   ├── core/                         # 【核心工具类】可复用的底层能力
│   │   ├── __init__.py
│   │   ├── video_processor.py       # 视频处理（帧提取、音频提取）
│   │   ├── transcript_gen.py        # 字幕生成（Whisper）
│   │   ├── ai_client.py             # AI 客户端（Claude）
│   │   └── prompts.py               # 提示词模板
│   │
│   ├── services/                     # 【业务服务层】协调 core 完成业务
│   │   ├── __init__.py
│   │   ├── video_service.py         # 视频业务逻辑
│   │   ├── note_service.py          # 笔记业务逻辑
│   │   └── ai_service.py            # AI 业务逻辑
│   │
│   ├── utils/                        # 【工具函数】
│   │   ├── __init__.py
│   │   ├── time_utils.py            # 时间格式转换
│   │   └── file_utils.py            # 文件操作
│   │
│   ├── requirements.txt              # Python 依赖
│   └── .env.example                  # 环境变量示例
│
├── frontend/                         # React 前端
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── main.tsx                  # 【入口】React 应用入口
│   │   ├── App.tsx                   # 【主组件】状态管理 + 布局
│   │   │
│   │   ├── components/               # 【UI 组件】
│   │   │   ├── VideoPlayer.tsx      # 视频播放器
│   │   │   ├── NotePanel.tsx        # 笔记面板（Tab1）
│   │   │   ├── AIPanel.tsx          # AI 助手面板（Tab2）
│   │   │   └── QuickMark.tsx        # 快速标记组件
│   │   │
│   │   ├── services/                 # 【API 服务】
│   │   │   ├── api.ts               # Axios 配置
│   │   │   ├── videoApi.ts          # 视频相关 API
│   │   │   ├── noteApi.ts           # 笔记相关 API
│   │   │   └── websocket.ts         # WebSocket 客户端
│   │   │
│   │   ├── hooks/                    # 【自定义 Hooks】
│   │   │   ├── useVideoPlayer.ts    # 视频播放器逻辑
│   │   │   └── useKeyboard.ts       # 键盘快捷键
│   │   │
│   │   ├── types/                    # 【类型定义】
│   │   │   └── index.ts             # 所有 TypeScript 类型
│   │   │
│   │   └── utils/                    # 【工具函数】
│   │       ├── timeFormat.ts        # 时间格式化
│   │       └── markdown.ts          # Markdown 处理
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── uploads/                          # 【数据目录】视频文件
├── data/                             # 【数据目录】JSON 数据
│   ├── videos/                       # 视频信息 JSON
│   └── notes/                        # 笔记信息 JSON
│
├── .env                              # 环境变量（不提交）
├── .gitignore
└── README.md
```

**文件统计**：
- 后端：11 个核心文件
- 前端：12 个核心文件
- **总计：23 个文件**（非常精简）

---

## 🏗️ 二、后端代码结构详解

### 2.1 目录职责划分

```
backend/
├── main.py              ← 【API 路由层】处理 HTTP 请求
├── config.py            ← 【配置层】所有配置常量
├── storage.py           ← 【数据层】JSON 文件存储
│
├── services/            ← 【业务逻辑层】协调多个 core 类
│   ├── video_service.py
│   ├── note_service.py
│   └── ai_service.py
│
└── core/                ← 【核心工具层】单一职责的工具类
    ├── video_processor.py
    ├── transcript_gen.py
    ├── ai_client.py
    └── prompts.py
```

**层次关系**：
```
main.py (路由)
    ↓ 调用
services/ (业务层)
    ↓ 调用
core/ (工具层)
    ↓ 使用
storage.py (数据层)
```

---

### 2.2 核心类设计

#### **📄 config.py** - 配置管理

```python
"""
配置管理 - 所有配置集中在这里
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ===== API 密钥 =====
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("请在 .env 中设置 CLAUDE_API_KEY")

# ===== AI 配置 =====
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# ===== 视频处理配置 =====
KEYFRAME_INTERVAL = 30      # 关键帧提取间隔（秒）
MAX_KEYFRAMES = 5           # 最多提取几帧（节省成本）
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# ===== 字幕配置 =====
WHISPER_MODEL_SIZE = "medium"  # tiny | base | small | medium | large
WHISPER_DEVICE = "cpu"         # cpu | cuda

# ===== 上下文配置 =====
CONTEXT_WINDOW = 30         # AI 问答时前后几秒的字幕

# ===== 路径配置 =====
UPLOAD_DIR = "uploads"
DATA_DIR = "data"
VIDEO_DATA_DIR = f"{DATA_DIR}/videos"
NOTE_DATA_DIR = f"{DATA_DIR}/notes"

# 确保目录存在
for dir_path in [UPLOAD_DIR, VIDEO_DATA_DIR, NOTE_DATA_DIR]:
    os.makedirs(dir_path, exist_ok=True)
```

---

#### **📄 storage.py** - JSON 存储

```python
"""
简单的 JSON 文件存储系统
每个视频一个 JSON 文件，每个视频的笔记一个 JSON 文件
"""
import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import config

class Storage:
    """JSON 文件存储"""

    @staticmethod
    def generate_id() -> str:
        """生成唯一 ID"""
        return str(uuid.uuid4())

    # ===== 视频相关 =====

    @staticmethod
    def save_video(video_data: dict) -> str:
        """保存视频信息"""
        video_id = video_data.get("id") or Storage.generate_id()
        video_data["id"] = video_id
        video_data["created_at"] = datetime.now().isoformat()

        file_path = f"{config.VIDEO_DATA_DIR}/{video_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)

        return video_id

    @staticmethod
    def get_video(video_id: str) -> Optional[dict]:
        """获取视频信息"""
        file_path = f"{config.VIDEO_DATA_DIR}/{video_id}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    @staticmethod
    def update_video(video_id: str, updates: dict) -> bool:
        """更新视频信息"""
        video = Storage.get_video(video_id)
        if not video:
            return False

        video.update(updates)
        video["updated_at"] = datetime.now().isoformat()
        Storage.save_video(video)
        return True

    # ===== 笔记相关 =====

    @staticmethod
    def save_notes(video_id: str, notes: List[dict]) -> bool:
        """保存笔记列表（覆盖式）"""
        file_path = f"{config.NOTE_DATA_DIR}/{video_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        return True

    @staticmethod
    def get_notes(video_id: str) -> List[dict]:
        """获取笔记列表"""
        file_path = f"{config.NOTE_DATA_DIR}/{video_id}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    @staticmethod
    def add_note(video_id: str, note: dict) -> dict:
        """添加一条笔记"""
        notes = Storage.get_notes(video_id)

        note["id"] = Storage.generate_id()
        note["created_at"] = datetime.now().isoformat()
        notes.append(note)

        Storage.save_notes(video_id, notes)
        return note

    @staticmethod
    def update_note(video_id: str, note_id: str, updates: dict) -> bool:
        """更新笔记"""
        notes = Storage.get_notes(video_id)

        for note in notes:
            if note["id"] == note_id:
                note.update(updates)
                note["updated_at"] = datetime.now().isoformat()
                Storage.save_notes(video_id, notes)
                return True

        return False

    @staticmethod
    def delete_note(video_id: str, note_id: str) -> bool:
        """删除笔记"""
        notes = Storage.get_notes(video_id)
        original_length = len(notes)

        notes = [n for n in notes if n["id"] != note_id]

        if len(notes) < original_length:
            Storage.save_notes(video_id, notes)
            return True
        return False
```

**数据格式示例**：

```json
// data/videos/{video_id}.json
{
  "id": "abc-123-def",
  "filename": "lecture.mp4",
  "path": "uploads/lecture.mp4",
  "duration": 1234.5,
  "created_at": "2024-01-14T10:00:00",
  "analysis": {
    "summary": "这是一节关于动态规划的课程...",
    "topics": ["动态规划", "最长公共子序列"],
    "chapters": [
      {"time": 0, "title": "引入"},
      {"time": 300, "title": "原理讲解"}
    ]
  },
  "transcript": [
    {"start": 0.0, "end": 5.2, "text": "大家好，今天我们讲动态规划", "keywords": []}
  ]
}

// data/notes/{video_id}.json
[
  {
    "id": "note-1",
    "timestamp": 120.5,
    "type": "important",
    "content": "这里的时间复杂度是 O(n^2)",
    "created_at": "2024-01-14T10:05:00"
  }
]
```

---

#### **📄 core/video_processor.py** - 视频处理

```python
"""
视频处理器 - 负责视频帧提取、音频提取等
"""
import base64
from io import BytesIO
from moviepy.editor import VideoFileClip
from PIL import Image
import config

class VideoProcessor:
    """视频处理器"""

    def __init__(self, video_path: str):
        self.video_path = video_path
        self.clip = VideoFileClip(video_path)

    def get_duration(self) -> float:
        """获取视频时长（秒）"""
        return self.clip.duration

    def extract_frame_at(self, timestamp: float) -> str:
        """
        提取指定时间的帧
        返回：base64 编码的 PNG 图片
        """
        frame = self.clip.get_frame(timestamp)

        # 转换为 PIL Image
        image = Image.fromarray(frame)

        # 转为 base64
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return img_base64

    def extract_keyframes(self) -> list:
        """
        提取关键帧
        返回：base64 列表
        """
        duration = self.get_duration()
        interval = config.KEYFRAME_INTERVAL
        max_frames = config.MAX_KEYFRAMES

        keyframes = []
        timestamps = []

        # 计算时间戳
        current = 0
        while current < duration and len(timestamps) < max_frames:
            timestamps.append(current)
            current += interval

        # 提取帧
        for ts in timestamps:
            frame_base64 = self.extract_frame_at(ts)
            keyframes.append({
                "timestamp": ts,
                "data": frame_base64
            })

        return keyframes

    def extract_audio(self, output_path: str = None) -> str:
        """
        提取音频
        返回：音频文件路径
        """
        if output_path is None:
            output_path = self.video_path.replace(".mp4", ".mp3")

        self.clip.audio.write_audiofile(output_path, logger=None)
        return output_path

    def close(self):
        """释放资源"""
        if self.clip:
            self.clip.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

---

#### **📄 core/transcript_gen.py** - 字幕生成

```python
"""
字幕生成器 - 使用 Whisper 生成字幕
"""
from faster_whisper import WhisperModel
from typing import List, Dict
import config

class TranscriptGenerator:
    """字幕生成器"""

    def __init__(self):
        self.model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE
        )

    def generate(self, audio_path: str) -> List[Dict]:
        """
        生成字幕
        返回：[{"start": 0.0, "end": 5.2, "text": "..."}, ...]
        """
        segments, info = self.model.transcribe(
            audio_path,
            language="zh"  # 可改为自动检测
        )

        transcript = []
        for segment in segments:
            transcript.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })

        return transcript

    @staticmethod
    def format_to_text(transcript: List[Dict]) -> str:
        """
        将字幕转为纯文本
        用于传给 AI
        """
        return " ".join([s["text"] for s in transcript])

    @staticmethod
    def get_surrounding_text(
        transcript: List[Dict],
        timestamp: float,
        window: int = None
    ) -> str:
        """
        获取指定时间前后的字幕文本
        window: 时间窗口（秒）
        """
        if window is None:
            window = config.CONTEXT_WINDOW

        relevant_segments = [
            s for s in transcript
            if abs(s["start"] - timestamp) <= window
        ]

        return " ".join([s["text"] for s in relevant_segments])
```

---

#### **📄 core/ai_client.py** - AI 客户端

```python
"""
AI 客户端 - 封装 Claude API 调用
"""
from anthropic import Anthropic
from typing import AsyncIterator, List, Dict
import config
from .prompts import VIDEO_ANALYSIS_PROMPT, ANSWER_QUESTION_PROMPT

class AIClient:
    """Claude AI 客户端"""

    def __init__(self):
        self.client = Anthropic(api_key=config.CLAUDE_API_KEY)
        self.model = config.CLAUDE_MODEL

    def analyze_video(
        self,
        keyframes: List[Dict],
        transcript_text: str
    ) -> Dict:
        """
        分析视频内容
        返回：{"summary": "...", "topics": [...], "chapters": [...]}
        """
        # 构建消息内容
        content = [
            {"type": "text", "text": VIDEO_ANALYSIS_PROMPT}
        ]

        # 添加关键帧图片
        for frame in keyframes:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": frame["data"]
                }
            })

        # 添加字幕（限制长度）
        content.append({
            "type": "text",
            "text": f"视频字幕内容：\n{transcript_text[:3000]}"
        })

        # 调用 API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            messages=[{"role": "user", "content": content}]
        )

        # 解析响应
        import json
        result_text = response.content[0].text

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # 如果不是 JSON，返回简单格式
            return {
                "summary": result_text[:200],
                "topics": [],
                "chapters": []
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
        # 构建提示词
        prompt = ANSWER_QUESTION_PROMPT.format(
            video_summary=context.get("summary", "无"),
            current_chapter=context.get("chapter", "无"),
            surrounding_subtitles=context.get("subtitles", "无"),
            question=question
        )

        # 构建消息
        content = [
            {"type": "text", "text": prompt},
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": frame_base64
                }
            }
        ]

        # 流式调用
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": content}]
        ) as stream:
            async for text in stream.text_stream:
                yield text
```

---

#### **📄 core/prompts.py** - 提示词模板

```python
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
```

---

#### **📄 services/video_service.py** - 视频业务逻辑

```python
"""
视频服务 - 协调视频相关的所有操作
"""
from core.video_processor import VideoProcessor
from core.transcript_gen import TranscriptGenerator
from core.ai_client import AIClient
from storage import Storage
import asyncio

class VideoService:
    """视频服务"""

    def __init__(self):
        self.transcript_gen = TranscriptGenerator()
        self.ai_client = AIClient()

    async def process_upload(self, file_path: str, filename: str) -> dict:
        """
        处理视频上传
        包含：视频处理 + 字幕生成 + AI 分析
        """
        # 1. 视频处理
        with VideoProcessor(file_path) as processor:
            duration = processor.get_duration()
            keyframes = processor.extract_keyframes()

            # 2. 提取音频
            audio_path = processor.extract_audio()

        # 3. 生成字幕（可能耗时较长）
        transcript = self.transcript_gen.generate(audio_path)
        transcript_text = TranscriptGenerator.format_to_text(transcript)

        # 4. AI 分析视频
        analysis = self.ai_client.analyze_video(keyframes, transcript_text)

        # 5. 保存到存储
        video_data = {
            "filename": filename,
            "path": file_path,
            "duration": duration,
            "analysis": analysis,
            "transcript": transcript
        }

        video_id = Storage.save_video(video_data)

        return {
            "video_id": video_id,
            "duration": duration,
            "analysis": analysis
        }

    def get_video(self, video_id: str) -> dict:
        """获取视频信息"""
        return Storage.get_video(video_id)

    def get_frame_at(self, video_id: str, timestamp: float) -> str:
        """获取指定时间的帧"""
        video = Storage.get_video(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        with VideoProcessor(video["path"]) as processor:
            return processor.extract_frame_at(timestamp)
```

---

#### **📄 services/note_service.py** - 笔记业务逻辑

```python
"""
笔记服务 - 处理笔记相关操作
"""
from storage import Storage
from typing import List, Dict

class NoteService:
    """笔记服务"""

    def create_note(
        self,
        video_id: str,
        timestamp: float,
        note_type: str,
        content: str = ""
    ) -> dict:
        """创建笔记"""
        note = {
            "timestamp": timestamp,
            "type": note_type,  # important | question | idea
            "content": content
        }
        return Storage.add_note(video_id, note)

    def update_note(
        self,
        video_id: str,
        note_id: str,
        content: str
    ) -> bool:
        """更新笔记内容"""
        return Storage.update_note(video_id, note_id, {"content": content})

    def get_notes(self, video_id: str) -> List[dict]:
        """获取所有笔记"""
        notes = Storage.get_notes(video_id)
        # 按时间戳排序
        return sorted(notes, key=lambda x: x["timestamp"])

    def delete_note(self, video_id: str, note_id: str) -> bool:
        """删除笔记"""
        return Storage.delete_note(video_id, note_id)

    def export_markdown(self, video_id: str) -> str:
        """导出为 Markdown"""
        video = Storage.get_video(video_id)
        notes = self.get_notes(video_id)

        if not video:
            raise ValueError(f"Video {video_id} not found")

        # 构建 Markdown
        md_lines = [
            f"# {video['filename']}",
            "",
            "## 📊 视频信息",
            f"- 时长：{self._format_duration(video['duration'])}",
            f"- 主题：{video.get('analysis', {}).get('summary', '无')}",
            "",
            "## 📚 知识点",
        ]

        topics = video.get('analysis', {}).get('topics', [])
        for topic in topics:
            md_lines.append(f"- {topic}")

        md_lines.extend(["", "## 📝 详细笔记", ""])

        # 按类型分组
        important_notes = [n for n in notes if n["type"] == "important"]
        question_notes = [n for n in notes if n["type"] == "question"]
        idea_notes = [n for n in notes if n["type"] == "idea"]

        if important_notes:
            md_lines.append("### 🔴 重要知识点")
            for note in important_notes:
                ts = self._format_timestamp(note["timestamp"])
                md_lines.append(f"\n**[{ts}]**\n{note['content']}\n")

        if question_notes:
            md_lines.append("### 🟡 疑问")
            for note in question_notes:
                ts = self._format_timestamp(note["timestamp"])
                md_lines.append(f"\n**[{ts}]**\n{note['content']}\n")

        if idea_notes:
            md_lines.append("### 🟢 灵感与补充")
            for note in idea_notes:
                ts = self._format_timestamp(note["timestamp"])
                md_lines.append(f"\n**[{ts}]**\n{note['content']}\n")

        return "\n".join(md_lines)

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """格式化时长：123.5 -> "02:03" """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """格式化时间戳：125.5 -> "02:05" """
        return NoteService._format_duration(seconds)
```

---

#### **📄 services/ai_service.py** - AI 业务逻辑

```python
"""
AI 服务 - 处理 AI 相关业务
"""
from core.ai_client import AIClient
from core.transcript_gen import TranscriptGenerator
from storage import Storage
from typing import AsyncIterator, Dict

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
            raise ValueError(f"Video {video_id} not found")

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

    async def organize_notes(self, video_id: str) -> str:
        """
        自动整理笔记
        （可选功能，时间紧可以不实现）
        """
        video = Storage.get_video(video_id)
        notes = Storage.get_notes(video_id)

        # TODO: 调用 AI 整理笔记
        pass
```

---

#### **📄 main.py** - FastAPI 主程序

```python
"""
FastAPI 主程序 - 所有路由和 WebSocket
"""
from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import config
from services.video_service import VideoService
from services.note_service import NoteService
from services.ai_service import AIService

# 创建 FastAPI 应用
app = FastAPI(title="Video Learning Assistant")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
video_service = VideoService()
note_service = NoteService()
ai_service = AIService()

# ===== Pydantic 模型 =====

class NoteCreate(BaseModel):
    video_id: str
    timestamp: float
    type: str
    content: str = ""

class NoteUpdate(BaseModel):
    video_id: str
    note_id: str
    content: str

class AIQuestion(BaseModel):
    video_id: str
    timestamp: float
    question: str
    frame: str  # base64

# ===== 视频相关路由 =====

@app.post("/api/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    """上传视频"""
    # 检查文件大小
    file_size = 0
    content = await file.read()
    file_size = len(content)

    if file_size > config.MAX_FILE_SIZE:
        raise HTTPException(400, "文件过大")

    # 保存文件
    file_path = os.path.join(config.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 处理视频（异步）
    try:
        result = await video_service.process_upload(file_path, file.filename)
        return result
    except Exception as e:
        raise HTTPException(500, f"视频处理失败: {str(e)}")

@app.get("/api/videos/{video_id}")
def get_video(video_id: str):
    """获取视频信息"""
    video = video_service.get_video(video_id)
    if not video:
        raise HTTPException(404, "视频不存在")
    return video

@app.get("/api/videos/{video_id}/frame")
def get_frame(video_id: str, timestamp: float):
    """获取指定时间的帧"""
    try:
        frame_base64 = video_service.get_frame_at(video_id, timestamp)
        return {"frame": frame_base64}
    except Exception as e:
        raise HTTPException(500, f"获取帧失败: {str(e)}")

# ===== 笔记相关路由 =====

@app.post("/api/notes")
def create_note(note: NoteCreate):
    """创建笔记"""
    result = note_service.create_note(
        note.video_id,
        note.timestamp,
        note.type,
        note.content
    )
    return result

@app.put("/api/notes")
def update_note(note: NoteUpdate):
    """更新笔记"""
    success = note_service.update_note(
        note.video_id,
        note.note_id,
        note.content
    )
    if not success:
        raise HTTPException(404, "笔记不存在")
    return {"success": True}

@app.get("/api/notes/{video_id}")
def get_notes(video_id: str):
    """获取所有笔记"""
    notes = note_service.get_notes(video_id)
    return {"notes": notes}

@app.delete("/api/notes/{video_id}/{note_id}")
def delete_note(video_id: str, note_id: str):
    """删除笔记"""
    success = note_service.delete_note(video_id, note_id)
    if not success:
        raise HTTPException(404, "笔记不存在")
    return {"success": True}

@app.get("/api/notes/export/{video_id}")
def export_notes(video_id: str):
    """导出笔记为 Markdown"""
    try:
        markdown = note_service.export_markdown(video_id)
        return {"markdown": markdown}
    except Exception as e:
        raise HTTPException(500, f"导出失败: {str(e)}")

# ===== AI 相关路由 =====

@app.websocket("/ws/ai/chat")
async def ai_chat(websocket: WebSocket):
    """AI 问答（WebSocket 流式）"""
    await websocket.accept()

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()

            question = data.get("question")
            video_id = data.get("video_id")
            timestamp = data.get("timestamp")
            frame = data.get("frame")

            # 流式返回
            async for chunk in ai_service.answer_question(
                video_id, timestamp, question, frame
            ):
                await websocket.send_text(chunk)

            # 发送结束标记
            await websocket.send_text("[DONE]")

    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()

# ===== 健康检查 =====

@app.get("/")
def root():
    """健康检查"""
    return {"status": "ok", "message": "Video Learning Assistant API"}

# ===== 启动 =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

---

## 🎨 三、前端代码结构详解

### 3.1 目录职责划分

```
frontend/src/
├── App.tsx              ← 【根组件】状态管理 + 布局
├── main.tsx             ← 【入口】React 挂载
│
├── components/          ← 【UI 组件】独立的视图组件
│   ├── VideoPlayer.tsx
│   ├── NotePanel.tsx
│   └── AIPanel.tsx
│
├── services/            ← 【API 层】与后端通信
│   ├── api.ts
│   ├── videoApi.ts
│   ├── noteApi.ts
│   └── websocket.ts
│
├── hooks/               ← 【业务逻辑 Hooks】可复用的逻辑
│   ├── useVideoPlayer.ts
│   └── useKeyboard.ts
│
├── types/               ← 【类型定义】
│   └── index.ts
│
└── utils/               ← 【工具函数】
    ├── timeFormat.ts
    └── markdown.ts
```

---

### 3.2 核心文件设计

#### **📄 types/index.ts** - 类型定义

```typescript
// 视频类型
export interface Video {
  id: string;
  filename: string;
  path: string;
  duration: number;
  analysis: VideoAnalysis;
  transcript: Subtitle[];
  created_at: string;
}

export interface VideoAnalysis {
  summary: string;
  topics: string[];
  chapters: Chapter[];
  difficulty?: string;
}

export interface Chapter {
  time: number;
  title: string;
}

export interface Subtitle {
  start: number;
  end: number;
  text: string;
}

// 笔记类型
export interface Note {
  id: string;
  timestamp: number;
  type: 'important' | 'question' | 'idea';
  content: string;
  created_at: string;
  updated_at?: string;
}

// UI 状态
export interface AppState {
  currentVideo: Video | null;
  notes: Note[];
  currentTime: number;
  isPlaying: boolean;
  isFocusMode: boolean;
  activeTab: 'notes' | 'ai';
}
```

---

#### **📄 services/api.ts** - Axios 配置

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟（视频上传可能较长）
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

---

#### **📄 services/videoApi.ts** - 视频 API

```typescript
import { api } from './api';
import { Video } from '../types';

export const videoApi = {
  // 上传视频
  upload: async (file: File): Promise<{ video_id: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  },

  // 获取视频信息
  get: async (videoId: string): Promise<Video> => {
    const response = await api.get(`/videos/${videoId}`);
    return response.data;
  },

  // 获取帧
  getFrame: async (videoId: string, timestamp: number): Promise<string> => {
    const response = await api.get(`/videos/${videoId}/frame`, {
      params: { timestamp },
    });
    return response.data.frame;
  },
};
```

---

#### **📄 services/noteApi.ts** - 笔记 API

```typescript
import { api } from './api';
import { Note } from '../types';

export const noteApi = {
  // 创建笔记
  create: async (
    videoId: string,
    timestamp: number,
    type: string,
    content = ''
  ): Promise<Note> => {
    const response = await api.post('/notes', {
      video_id: videoId,
      timestamp,
      type,
      content,
    });
    return response.data;
  },

  // 更新笔记
  update: async (
    videoId: string,
    noteId: string,
    content: string
  ): Promise<void> => {
    await api.put('/notes', {
      video_id: videoId,
      note_id: noteId,
      content,
    });
  },

  // 获取所有笔记
  getAll: async (videoId: string): Promise<Note[]> => {
    const response = await api.get(`/notes/${videoId}`);
    return response.data.notes;
  },

  // 删除笔记
  delete: async (videoId: string, noteId: string): Promise<void> => {
    await api.delete(`/notes/${videoId}/${noteId}`);
  },

  // 导出笔记
  export: async (videoId: string): Promise<string> => {
    const response = await api.get(`/notes/export/${videoId}`);
    return response.data.markdown;
  },
};
```

---

#### **📄 services/websocket.ts** - WebSocket 客户端

```typescript
export class AIWebSocket {
  private ws: WebSocket | null = null;
  private url = 'ws://localhost:8000/ws/ai/chat';

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => resolve();
      this.ws.onerror = (error) => reject(error);
    });
  }

  async askQuestion(
    videoId: string,
    timestamp: number,
    question: string,
    frame: string,
    onChunk: (text: string) => void
  ): Promise<void> {
    if (!this.ws) {
      await this.connect();
    }

    // 发送问题
    this.ws!.send(
      JSON.stringify({
        video_id: videoId,
        timestamp,
        question,
        frame,
      })
    );

    // 监听响应
    this.ws!.onmessage = (event) => {
      const text = event.data;
      if (text === '[DONE]') {
        return;
      }
      onChunk(text);
    };
  }

  close() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
```

---

#### **📄 App.tsx** - 主组件

```typescript
import React, { useState } from 'react';
import { Layout } from 'antd';
import VideoPlayer from './components/VideoPlayer';
import NotePanel from './components/NotePanel';
import AIPanel from './components/AIPanel';
import { Video, Note } from './types';
import './App.css';

const { Content, Sider } = Layout;

function App() {
  // ===== 状态管理 =====
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeTab, setActiveTab] = useState<'notes' | 'ai'>('notes');
  const [isFocusMode, setIsFocusMode] = useState(false);

  // ===== 回调函数 =====
  const handleVideoUploaded = (video: Video) => {
    setCurrentVideo(video);
  };

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time);
  };

  const handleNoteAdded = (note: Note) => {
    setNotes([...notes, note]);
  };

  const handleJumpTo = (timestamp: number) => {
    setCurrentTime(timestamp);
  };

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 左侧：视频播放器 */}
      <Content style={{ width: isFocusMode ? '100%' : '70%' }}>
        <VideoPlayer
          video={currentVideo}
          currentTime={currentTime}
          onVideoUploaded={handleVideoUploaded}
          onTimeUpdate={handleTimeUpdate}
          isFocusMode={isFocusMode}
        />
      </Content>

      {/* 右侧：笔记/AI 面板 */}
      {!isFocusMode && (
        <Sider width="30%" theme="light">
          {activeTab === 'notes' ? (
            <NotePanel
              videoId={currentVideo?.id}
              notes={notes}
              currentTime={currentTime}
              onNoteAdded={handleNoteAdded}
              onJumpTo={handleJumpTo}
            />
          ) : (
            <AIPanel
              videoId={currentVideo?.id}
              currentTime={currentTime}
            />
          )}
        </Sider>
      )}
    </Layout>
  );
}

export default App;
```

---

## 📊 四、数据流动关系

```
前端 App.tsx (状态中心)
    ↓
┌───┴────┬─────────┬────────┐
│        │         │        │
Video   Note      AI     Keyboard
Player  Panel    Panel    Hook
│        │         │        │
└───┬────┴─────────┴────┬───┘
    ↓                   ↓
  API Services    WebSocket
    ↓                   ↓
═══════════════════════════════
    ↓                   ↓
FastAPI main.py (路由层)
    ↓
┌───┴────┬────────┐
│        │        │
Video   Note     AI
Service Service Service
│        │        │
└───┬────┴────┬───┘
    ↓         ↓
Core 工具类 + Storage
```

---

## ✅ 五、总结

### 设计特点
1. **层次清晰**：路由 → 服务 → 核心 → 存储
2. **职责单一**：每个类只做一件事
3. **依赖简单**：没有复杂的依赖注入
4. **易于测试**：每层可独立测试
5. **快速开发**：代码量少，结构简单

### 文件统计
- **后端核心文件**：11 个
- **前端核心文件**：12 个
- **配置文件**：2 个（.env + requirements.txt）
- **总计**：25 个文件

### 代码量预估
- 后端：~1200 行
- 前端：~1400 行
- **总计：~2600 行**

这是一个**精简但完整**的架构，可以支撑所有核心功能的实现！
