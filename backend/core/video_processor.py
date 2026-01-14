"""
视频处理器 - 负责视频帧提取、音频提取等
注意：这是简化版，用于快速搭建框架
"""
import base64
from io import BytesIO
from pathlib import Path
import sys
import os

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))
import config

class VideoProcessor:
    """视频处理器"""

    def __init__(self, video_path: str):
        self.video_path = video_path
        self.clip = None
        self._load_video()

    def _load_video(self):
        """加载视频（延迟导入以加快启动速度）"""
        try:
            from moviepy.editor import VideoFileClip
            self.clip = VideoFileClip(self.video_path)
        except Exception as e:
            print(f"加载视频失败: {e}")
            self.clip = None

    def get_duration(self) -> float:
        """获取视频时长（秒）"""
        if self.clip:
            return self.clip.duration
        return 0.0

    def extract_frame_at(self, timestamp: float) -> str:
        """
        提取指定时间的帧
        返回：base64 编码的 PNG 图片
        """
        if not self.clip:
            raise ValueError("视频未加载")

        try:
            from PIL import Image

            frame = self.clip.get_frame(timestamp)

            # 转换为 PIL Image
            image = Image.fromarray(frame)

            # 转为 base64
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

            return img_base64
        except Exception as e:
            print(f"提取帧失败: {e}")
            raise

    def extract_keyframes(self) -> list:
        """
        提取关键帧
        返回：[{"timestamp": 0, "data": "base64..."}, ...]
        """
        if not self.clip:
            return []

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
        print(f"开始提取关键帧，共 {len(timestamps)} 帧...")
        for i, ts in enumerate(timestamps):
            try:
                frame_base64 = self.extract_frame_at(ts)
                keyframes.append({
                    "timestamp": ts,
                    "data": frame_base64
                })
                print(f"已提取第 {i+1}/{len(timestamps)} 帧")
            except Exception as e:
                print(f"提取第 {i+1} 帧失败: {e}")

        return keyframes

    def extract_audio(self, output_path: str = None) -> str:
        """
        提取音频
        返回：音频文件路径
        """
        if not self.clip:
            raise ValueError("视频未加载")

        if output_path is None:
            output_path = str(Path(self.video_path).with_suffix('.mp3'))

        try:
            print(f"正在提取音频到 {output_path}...")
            self.clip.audio.write_audiofile(output_path, logger=None)
            print("音频提取完成")
            return output_path
        except Exception as e:
            print(f"提取音频失败: {e}")
            raise

    def close(self):
        """释放资源"""
        if self.clip:
            self.clip.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()