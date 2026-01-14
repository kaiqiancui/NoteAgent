"""
视频服务 - 协调视频相关的所有操作
"""
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))
from core.video_processor import VideoProcessor
from core.transcript_gen import TranscriptGenerator
from core.ai_client import AIClient
from storage import Storage

class VideoService:
    """视频服务"""

    def __init__(self):
        self.transcript_gen = TranscriptGenerator()
        self.ai_client = AIClient()

    async def process_upload(self, file_path: str, filename: str) -> dict:
        """
        处理视频上传
        包含：视频处理 + 字幕生成 + AI 分析
        支持缓存：相同的视频文件会跳过处理，直接返回缓存结果
        """
        print(f"\n========== 开始处理视频: {filename} ==========")

        # 0. 计算文件 hash，检查是否已处理过
        print("\n[0/4] 正在检查视频缓存...")
        file_hash = Storage.calculate_file_hash(file_path)
        print(f"文件 Hash: {file_hash}")

        # 查找缓存
        cached_video = Storage.find_video_by_hash(file_hash)

        if cached_video:
            # 找到缓存，直接返回
            print(f"\n========== ✅ 使用缓存，跳过处理 ==========\n")
            return {
                "video_id": cached_video["id"],
                "duration": cached_video["duration"],
                "analysis": cached_video.get("analysis", {}),
                "cached": True  # 标记这是缓存结果
            }

        # 没有缓存，执行完整处理
        print("未找到缓存，开始完整处理...\n")

        # 1. 视频处理
        print("[1/4] 正在处理视频...")
        with VideoProcessor(file_path) as processor:
            duration = processor.get_duration()
            print(f"视频时长: {duration:.2f} 秒")

            keyframes = processor.extract_keyframes()
            print(f"提取了 {len(keyframes)} 个关键帧")

            # 2. 提取音频
            print("\n[2/4] 正在提取音频...")
            audio_path = processor.extract_audio()

        # 3. 生成字幕（可能耗时较长）
        print("\n[3/4] 正在生成字幕...")
        transcript = self.transcript_gen.generate(audio_path)
        transcript_text = TranscriptGenerator.format_to_text(transcript)
        print(f"生成了 {len(transcript)} 个字幕片段")

        # 4. AI 分析视频
        print("\n[4/4] 正在进行 AI 分析...")
        analysis = self.ai_client.analyze_video(keyframes, transcript_text)

        # 5. 保存到存储（包含 file_hash）
        video_data = {
            "filename": filename,
            "path": file_path,
            "duration": duration,
            "file_hash": file_hash,  # 保存 hash 用于缓存
            "analysis": analysis,
            "transcript": transcript
        }

        video_id = Storage.save_video(video_data)
        print(f"\n========== 视频处理完成，ID: {video_id} ==========\n")

        return {
            "video_id": video_id,
            "duration": duration,
            "analysis": analysis,
            "cached": False  # 标记这是新处理的结果
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
