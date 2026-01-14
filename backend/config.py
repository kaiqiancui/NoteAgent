"""
配置管理 - 所有配置集中在这里
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ===== 项目根目录 =====
BASE_DIR = Path(__file__).parent.parent

# ===== API 配置 =====
# 使用自定义 API 接口（OpenAI 兼容格式）
API_KEY = os.getenv("API_KEY", "sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.qingyuntop.top/v1/chat/completions")

if not API_KEY:
    print("警告: 未设置 API_KEY，AI 功能将无法使用")

# ===== AI 配置 =====
AI_MODEL = "gpt-4o"  # 使用 gpt-4o 模型（支持视觉）
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
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
VIDEO_DATA_DIR = DATA_DIR / "videos"
NOTE_DATA_DIR = DATA_DIR / "notes"

# 确保目录存在
for dir_path in [UPLOAD_DIR, VIDEO_DATA_DIR, NOTE_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ===== 标记类型配置 =====
NOTE_TYPES = {
    "important": "🔴",
    "question": "🟡",
    "idea": "🟢"
}
