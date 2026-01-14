# 开发指南

## 项目架构

### 技术栈

**后端**:
- FastAPI (Web 框架)
- faster-whisper (字幕生成)
- moviepy + opencv (视频处理)
- requests (API 调用，OpenAI 兼容格式)
- JSON 文件存储（无需数据库）

**前端** (待开发):
- React 18 + TypeScript
- Ant Design (UI 组件)
- video.js (视频播放器)
- Axios (HTTP 请求)

### 代码结构

```
video-learning-assistant/
├── backend/                  # Python 后端
│   ├── main.py              # FastAPI 主程序（所有路由）
│   ├── config.py            # 配置管理
│   ├── storage.py           # JSON 存储
│   │
│   ├── core/                # 核心工具类（可复用）
│   │   ├── video_processor.py    # 视频处理
│   │   ├── transcript_gen.py     # 字幕生成
│   │   ├── ai_client.py          # AI 客户端
│   │   └── prompts.py            # 提示词模板
│   │
│   └── services/            # 业务服务层（协调 core）
│       ├── video_service.py      # 视频业务逻辑
│       ├── note_service.py       # 笔记业务逻辑
│       └── ai_service.py         # AI 业务逻辑
│
├── frontend/                # React 前端（待开发）
├── uploads/                 # 视频文件存储
├── data/                    # JSON 数据存储
│   ├── videos/              # 视频信息
│   └── notes/               # 笔记信息
└── docs/                    # 文档
```

### 层次关系

```
main.py (路由层)
    ↓ 调用
services/ (业务逻辑层)
    ↓ 调用
core/ (核心工具层)
    ↓ 使用
storage.py (数据存储层)
```

## 后端核心模块

### 1. 配置管理 (`config.py`)

```python
# API 配置
API_KEY = os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")
AI_MODEL = "gpt-4o"

# 视频处理配置
KEYFRAME_INTERVAL = 30       # 关键帧间隔（秒）
MAX_KEYFRAMES = 5            # 最多提取帧数
WHISPER_MODEL_SIZE = "medium"  # 字幕模型
WHISPER_DEVICE = "cpu"       # 或 "cuda"

# 路径配置
UPLOAD_DIR = "uploads"
VIDEO_DATA_DIR = "data/videos"
NOTE_DATA_DIR = "data/notes"
```

### 2. 视频处理 (`core/video_processor.py`)

**主要功能**:
- 获取视频时长
- 提取关键帧（base64 格式）
- 提取音频（用于字幕生成）
- 获取指定时间的帧（用于 AI 问答）

**使用示例**:
```python
with VideoProcessor(video_path) as processor:
    duration = processor.get_duration()
    keyframes = processor.extract_keyframes()
    audio_path = processor.extract_audio()
```

### 3. 字幕生成 (`core/transcript_gen.py`)

**主要功能**:
- 使用 Whisper 生成字幕
- 字幕格式转换
- 获取指定时间范围的字幕

**返回格式**:
```python
[
    {"start": 0.0, "end": 5.2, "text": "大家好"},
    {"start": 5.2, "end": 10.5, "text": "今天我们讲..."}
]
```

### 4. AI 客户端 (`core/ai_client.py`)

**核心方法**:

#### analyze_video() - 视频分析
```python
def analyze_video(keyframes, transcript_text) -> dict:
    """
    分析视频内容
    返回：摘要、知识点、章节划分
    """
    # 自动回退机制：
    # 1. 先尝试视觉分析（图片+文本）
    # 2. 如果失败，切换到纯文本分析
```

#### answer_question() - 问答
```python
async def answer_question(question, frame, context) -> AsyncIterator[str]:
    """
    回答问题（流式返回）
    context: 视频摘要 + 当前章节 + 前后字幕
    """
```

### 5. 数据存储 (`storage.py`)

**存储格式**: JSON 文件

**视频数据** (`data/videos/{video_id}.json`):
```json
{
  "id": "abc-123",
  "filename": "lecture.mp4",
  "duration": 120.5,
  "file_hash": "md5_hash",
  "analysis": {
    "summary": "...",
    "topics": [...],
    "chapters": [...]
  },
  "transcript": [...]
}
```

**笔记数据** (`data/notes/{video_id}.json`):
```json
[
  {
    "id": "note-1",
    "timestamp": 10.5,
    "type": "important",
    "content": "笔记内容",
    "created_at": "2024-01-14T10:00:00"
  }
]
```

## API 接口

### 视频相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/videos/upload` | POST | 上传视频 |
| `/api/videos/{id}` | GET | 获取视频信息 |
| `/api/videos/{id}/frame?timestamp=5.0` | GET | 获取指定时间的帧 |

### 笔记相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/notes` | POST | 创建笔记 |
| `/api/notes` | PUT | 更新笔记 |
| `/api/notes/{video_id}` | GET | 获取笔记列表 |
| `/api/notes/{video_id}/{note_id}` | DELETE | 删除笔记 |
| `/api/notes/export/{video_id}` | GET | 导出 Markdown |

### AI 相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/ws/ai/chat` | WebSocket | AI 问答（流式） |

## 视频缓存机制

### 工作原理

1. **文件识别**: 计算视频文件的 MD5 hash
2. **缓存检查**: 查找是否存在相同 hash 的已处理视频
3. **结果**:
   - 命中缓存 → 直接返回已有数据（< 1 秒）
   - 未命中 → 执行完整处理（2-5 分钟）

### 实现位置

- **Hash 计算**: `storage.py` 中的 `calculate_file_hash()`
- **缓存查找**: `storage.py` 中的 `find_video_by_hash()`
- **使用**: `video_service.py` 中的 `process_upload()`

### 性能提升

| 操作 | 首次上传 | 缓存命中 |
|------|---------|---------|
| Hash 计算 | 1-2秒 | 1-2秒 |
| 视频处理 | 10-20秒 | ❌ 跳过 |
| 字幕生成 | 1-3分钟 | ❌ 跳过 |
| AI 分析 | 10-30秒 | ❌ 跳过 |
| **总耗时** | **2-5分钟** | **< 1秒** |

## 前端开发计划

### 目录结构（待创建）

```
frontend/
├── src/
│   ├── App.tsx              # 主组件（状态管理 + 布局）
│   │
│   ├── components/          # UI 组件
│   │   ├── VideoPlayer.tsx  # 视频播放器
│   │   ├── NotePanel.tsx    # 笔记面板
│   │   └── AIPanel.tsx      # AI 助手面板
│   │
│   ├── services/            # API 服务
│   │   ├── api.ts           # Axios 配置
│   │   ├── videoApi.ts      # 视频 API
│   │   ├── noteApi.ts       # 笔记 API
│   │   └── websocket.ts     # WebSocket 客户端
│   │
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useVideoPlayer.ts    # 视频播放器逻辑
│   │   └── useKeyboard.ts       # 键盘快捷键
│   │
│   └── types/               # TypeScript 类型
│       └── index.ts
│
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### 核心组件

#### VideoPlayer 组件
- 视频上传
- 播放控制（播放/暂停/进度）
- 时间跳转
- 快速标记按钮

#### NotePanel 组件
- 笔记列表显示
- 时间戳点击跳转
- Markdown 编辑器
- 笔记类型切换（重要/疑问/灵感）

#### AIPanel 组件
- 截图当前帧
- 问题输入
- WebSocket 连接
- 流式回答显示

### 开发步骤

1. **Week 1**: 前端框架搭建 + 布局
2. **Week 2**: 视频播放器 + 笔记功能
3. **Week 3**: AI 功能 + 前后端联调
4. **Week 4**: 优化 + 增强功能

## 开发规范

### 代码风格

- **后端**: 遵循 PEP 8
- **前端**: 使用 ESLint + Prettier
- **命名**:
  - 类名：PascalCase
  - 函数/变量：snake_case (Python) / camelCase (TypeScript)

### 错误处理

- 后端：使用 HTTPException
- 前端：统一的错误提示组件
- 日志：关键操作记录到控制台

### 测试

- 后端：手动测试 + API 文档测试
- 前端：浏览器测试
- 集成：完整流程测试

## 性能优化建议

### 后端优化

1. **视频处理**:
   - 减少关键帧数量：`MAX_KEYFRAMES = 3`
   - 使用更小的 Whisper 模型：`WHISPER_MODEL_SIZE = "base"`
   - 启用 GPU 加速：`WHISPER_DEVICE = "cuda"`

2. **AI 调用**:
   - 限制字幕长度：只传前 4000 字符
   - 减少关键帧：只传 3 帧
   - 启用缓存机制

3. **数据存储**:
   - JSON 文件存储已足够快
   - 如需优化可改用 SQLite

### 前端优化

1. **视频加载**:
   - 使用视频预加载
   - 分块加载大视频

2. **状态管理**:
   - 避免不必要的重渲染
   - 使用 React.memo

3. **网络请求**:
   - 请求去抖动
   - 请求缓存

## 下一步

1. 完成前端框架搭建
2. 实现视频播放器组件
3. 实现笔记编辑功能
4. 集成 AI 问答
5. 前后端联调
6. 功能增强

---

**需要帮助？** 参考 [QUICKSTART.md](QUICKSTART.md) 快速启动项目，查看 [FEATURES.md](FEATURES.md) 了解完整功能列表。
