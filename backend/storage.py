"""
简单的 JSON 文件存储系统
每个视频一个 JSON 文件，每个视频的笔记一个 JSON 文件
"""
import json
import uuid
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import config

class Storage:
    """JSON 文件存储"""

    @staticmethod
    def generate_id() -> str:
        """生成唯一 ID"""
        return str(uuid.uuid4())

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        计算文件的 MD5 hash
        用于识别相同的视频文件
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # 分块读取，避免大文件占用过多内存
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    # ===== 视频相关 =====

    @staticmethod
    def save_video(video_data: dict) -> str:
        """保存视频信息"""
        video_id = video_data.get("id") or Storage.generate_id()
        video_data["id"] = video_id
        video_data["created_at"] = datetime.now().isoformat()

        file_path = config.VIDEO_DATA_DIR / f"{video_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)

        return video_id

    @staticmethod
    def get_video(video_id: str) -> Optional[dict]:
        """获取视频信息"""
        file_path = config.VIDEO_DATA_DIR / f"{video_id}.json"
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

    @staticmethod
    def find_video_by_hash(file_hash: str) -> Optional[dict]:
        """
        通过文件 hash 查找已存在的视频
        遍历所有视频文件，查找匹配的 hash
        """
        video_dir = config.VIDEO_DATA_DIR

        # 遍历所有视频 JSON 文件
        for json_file in video_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)

                    # 检查是否有 file_hash 字段且匹配
                    if video_data.get("file_hash") == file_hash:
                        print(f"✅ 找到缓存视频: {video_data.get('filename')}")
                        print(f"   视频 ID: {video_data.get('id')}")
                        print(f"   跳过处理，直接使用缓存结果")
                        return video_data
            except Exception as e:
                print(f"读取视频文件失败 {json_file}: {e}")
                continue

        return None

    # ===== 笔记相关 =====

    @staticmethod
    def save_notes(video_id: str, notes: List[dict]) -> bool:
        """保存笔记列表（覆盖式）"""
        file_path = config.NOTE_DATA_DIR / f"{video_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        return True

    @staticmethod
    def get_notes(video_id: str) -> List[dict]:
        """获取笔记列表"""
        file_path = config.NOTE_DATA_DIR / f"{video_id}.json"
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