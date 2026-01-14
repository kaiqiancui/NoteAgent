"""
笔记服务 - 处理笔记相关操作
"""
import sys
from pathlib import Path
from typing import List, Dict

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))
from storage import Storage

class NoteService:
    """笔记服务"""

    def create_note(
        self,
        video_id: str,
        timestamp: float,
        note_type: str,
        content: str = "",
        frame: str = ""
    ) -> dict:
        """创建笔记"""
        note = {
            "timestamp": timestamp,
            "type": note_type,  # important | question | idea
            "content": content,
            "frame": frame  # base64 截图（可选）
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
                md_lines.append(f"\n**[{ts}]**")
                if note.get("frame"):
                    md_lines.append(f"![Screenshot](data:image/jpeg;base64,{note['frame']})")
                md_lines.append(f"{note['content']}\n")

        if question_notes:
            md_lines.append("### 🟡 疑问")
            for note in question_notes:
                ts = self._format_timestamp(note["timestamp"])
                md_lines.append(f"\n**[{ts}]**")
                if note.get("frame"):
                    md_lines.append(f"![Screenshot](data:image/jpeg;base64,{note['frame']})")
                md_lines.append(f"{note['content']}\n")

        if idea_notes:
            md_lines.append("### 🟢 灵感与补充")
            for note in idea_notes:
                ts = self._format_timestamp(note["timestamp"])
                md_lines.append(f"\n**[{ts}]**")
                if note.get("frame"):
                    md_lines.append(f"![Screenshot](data:image/jpeg;base64,{note['frame']})")
                md_lines.append(f"{note['content']}\n")

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