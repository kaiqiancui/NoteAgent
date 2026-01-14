"""
字幕生成器 - 使用 Whisper 生成字幕
注意：这是简化版，用于快速搭建框架
"""
import sys
from pathlib import Path
from typing import List, Dict

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))
import config

class TranscriptGenerator:
    """字幕生成器"""

    def __init__(self):
        self.model = None
        self._init_model()

    def _init_model(self):
        """初始化 Whisper 模型"""
        try:
            from faster_whisper import WhisperModel
            print(f"正在加载 Whisper 模型 ({config.WHISPER_MODEL_SIZE})...")
            self.model = WhisperModel(
                config.WHISPER_MODEL_SIZE,
                device=config.WHISPER_DEVICE
            )
            print("Whisper 模型加载完成")
        except Exception as e:
            print(f"Whisper 模型加载失败: {e}")
            self.model = None

    def generate(self, audio_path: str) -> List[Dict]:
        """
        生成字幕
        返回：[{"start": 0.0, "end": 5.2, "text": "..."}, ...]
        """
        if not self.model:
            print("警告: Whisper 模型未加载，返回空字幕")
            return []

        try:
            print(f"正在生成字幕: {audio_path}")
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
                print(f"[{segment.start:.1f}s - {segment.end:.1f}s] {segment.text}")

            print(f"字幕生成完成，共 {len(transcript)} 个片段")
            return transcript
        except Exception as e:
            print(f"字幕生成失败: {e}")
            return []

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