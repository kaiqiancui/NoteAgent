# 视频学习辅助智能体

基于 AI 的视频学习辅助工具，帮助学生更高效地学习视频课程。通过智能分析、时间戳笔记和 AI 问答，提升视频学习体验。

## 项目概述

这是一个集视频播放、智能笔记、AI 助手、知识库管理于一体的学习辅助系统。核心目标是减少学习时的注意力分散，让用户保持沉浸式学习。

### 核心特性

- **视频智能分析**: 自动提取关键帧、生成字幕、AI 分析内容
- **时间戳笔记**: 快速标记、时间戳关联、Markdown 导出、多截图插入
- **AI 智能助手**: 上下文感知问答、截图提问、流式回答、知识库增强
- **知识库管理**: 上传文档、RAG 检索增强、多模态检索
- **视频缓存**: 相同视频自动识别，秒级响应

## 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **faster-whisper** - 字幕生成
- **moviepy + opencv** - 视频处理
- **自定义 API** - OpenAI 兼容格式，支持视觉分析
- **JSON 文件存储** - 轻量级数据持久化

### 前端
- **React 18 + TypeScript** - 现代化前端框架
- **Ant Design** - 企业级 UI 组件库
- **ReactMarkdown** - Markdown 渲染
- **Vite** - 快速构建工具
- **HTML5 Video API** - 视频播放控制

## 项目结构

```
video-learning-assistant/
├── backend/                    # Python 后端服务
│   ├── main.py                # FastAPI 主程序和路由
│   ├── config.py              # 配置管理（API、模型、路径）
│   ├── storage.py             # JSON 数据存储
│   ├── core/                  # 核心工具类（可复用）
│   │   ├── video_processor.py    # 视频处理（提取帧、音频）
│   │   ├── transcript_gen.py     # Whisper 字幕生成
│   │   ├── ai_client.py          # AI 客户端（分析、问答）
│   │   └── prompts.py            # 提示词模板
│   ├── services/              # 业务服务层
│   │   ├── video_service.py      # 视频上传、分析、缓存
│   │   ├── note_service.py       # 笔记 CRUD
│   │   └── ai_service.py         # AI 问答、上下文构建
│   └── utils/                 # 工具函数
│
├── frontend/                   # React 前端应用
│   ├── src/
│   │   ├── App.tsx            # 根组件
│   │   ├── components/        # UI 组件
│   │   │   ├── Layout/            # 主布局（左右分栏）
│   │   │   ├── VideoPlayer/       # 视频播放器
│   │   │   ├── NotePanel/         # 笔记管理面板
│   │   │   ├── AIPanel/           # AI 助手面板
│   │   │   └── KnowledgePanel/    # 知识库管理
│   │   ├── services/          # API 服务
│   │   │   ├── api.ts             # Axios 配置
│   │   │   ├── videoApi.ts        # 视频 API
│   │   │   ├── noteApi.ts         # 笔记 API
│   │   │   └── websocket.ts       # WebSocket 客户端
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── types/             # TypeScript 类型定义
│   │   └── utils/             # 工具函数
│   └── package.json
│
├── uploads/                    # 视频文件存储
├── data/                       # JSON 数据存储
│   ├── videos/                    # 视频信息和分析结果
│   └── notes/                     # 笔记数据
├── docs/                       # 文档
│   └── archive/                   # 历史文档归档
├── .gitignore
└── README.md
```

### 架构设计

```
前端 (React)
    ↓ HTTP/WebSocket
后端 main.py (路由层)
    ↓
services/ (业务逻辑层)
    ↓
core/ (核心工具层)
    ↓
storage.py (数据存储层)
```

## 环境配置

### 前置要求

- **Python** 3.10+
- **Node.js** 18+
- **Conda** 环境管理器（推荐）
- **ffmpeg** 视频处理依赖

### 后端配置

1. 创建并激活 conda 环境：
```bash
conda create -n video-learning python=3.10
conda activate video-learning
```

2. 安装依赖：
```bash
cd backend
pip install -r requirements.txt
```

3. 配置 API（创建 `backend/.env` 文件）：
```bash
# AI API 配置（支持 OpenAI 兼容格式）
API_KEY=your_api_key_here
API_BASE_URL=https://api.example.com/v1/chat/completions
AI_MODEL=gpt-4o  # 需要支持视觉分析
```

4. 修改配置（可选，编辑 `backend/config.py`）：
```python
# 视频处理配置
KEYFRAME_INTERVAL = 30        # 关键帧间隔（秒）
MAX_KEYFRAMES = 5             # 最多提取帧数
WHISPER_MODEL_SIZE = "medium" # 字幕模型大小
WHISPER_DEVICE = "cpu"        # 或 "cuda"（GPU加速）

# 路径配置
UPLOAD_DIR = "uploads"
VIDEO_DATA_DIR = "data/videos"
NOTE_DATA_DIR = "data/notes"
```

### 前端配置

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 配置代理（可选，编辑 `frontend/vite.config.ts`）：
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
```

## 快速启动

### 方法 1：使用启动脚本

```bash
./start.sh
```

### 方法 2：手动启动

#### 启动后端
```bash
conda activate video-learning  # 或你的环境名
cd backend
python main.py
```

后端默认运行在 http://localhost:8000

#### 启动前端
```bash
cd frontend
npm run dev
```

前端默认运行在 http://localhost:5173

### 验证服务

访问以下地址确认服务正常：
- **前端应用**: http://localhost:5173
- **后端健康检查**: http://localhost:8000/
- **API 文档**: http://localhost:8000/docs

## 主要功能

详细功能说明请查看 [FEATURES.md](FEATURES.md)

### 视频管理
- 视频上传与播放控制
- 自动生成字幕和关键帧
- AI 分析视频内容（摘要、知识点、章节）
- 视频缓存机制（MD5识别，秒级复用）

### 智能笔记
- 快速标记（重要/疑问/灵感）
- 时间戳自动关联
- Markdown 编辑器
- 多截图插入
- 点击跳转播放
- 一键导出 Markdown

### AI 助手
- 截图当前画面提问
- 上下文感知（画面+字幕+笔记+视频摘要）
- WebSocket 流式回答
- AI 生成结构化笔记
- 答案插入到笔记

### 知识库
- 上传文档（PDF、TXT、Markdown、Word）
- 知识库管理（查看、删除）
- RAG 检索增强（模拟）
- AI 回答标注来源

## 核心技术亮点

### 1. 视频缓存机制
- 基于 MD5 hash 识别相同视频
- 首次上传：完整处理（2-5 分钟）
- 再次上传：使用缓存（< 1 秒）
- 即使文件名不同也能命中缓存

### 2. AI 智能回退
- 优先使用视觉分析（图片 + 文本）
- 视觉失败自动切换到纯文本分析
- 确保 AI 功能始终可用

### 3. 前端实时同步
- 自定义事件机制实现跨组件通信
- 笔记更新自动刷新列表
- 知识库更新自动同步选择器

### 4. 多模态笔记
- 文字 + 多张截图
- Markdown 格式存储和渲染
- Base64 内嵌图片，导出即可用

## 使用示例

### API 测试（通过 FastAPI Docs）

1. 访问 http://localhost:8000/docs
2. 测试上传视频：
   - 找到 `POST /api/videos/upload`
   - 点击 "Try it out"
   - 选择测试视频（建议 < 2 分钟）
   - 执行并获取 `video_id`

3. 创建笔记：
   - 使用 `POST /api/notes`
   - 提供 `video_id`、`timestamp`、`type`、`content`

4. 导出笔记：
   - 使用 `GET /api/notes/export/{video_id}`
   - 下载 Markdown 文件

### 前端使用流程

1. **上传视频** → 等待分析完成
2. **观看视频** → 快速标记重点
3. **编辑笔记** → 补充文字、插入截图
4. **AI 提问** → 选择知识库、截图提问
5. **生成笔记** → AI 提炼回答为结构化笔记
6. **导出笔记** → 下载 Markdown 文件

## 性能优化建议

### 加快视频处理速度

编辑 `backend/config.py`：
```python
WHISPER_MODEL_SIZE = "base"  # 使用更小的模型（medium → base）
MAX_KEYFRAMES = 3            # 减少关键帧数量（5 → 3）
```

### 启用 GPU 加速

如果有 NVIDIA GPU：
```python
WHISPER_DEVICE = "cuda"  # 从 cpu 改为 cuda
```

### 前端优化

- 视频文件建议 < 500MB
- 首次运行 Whisper 需要下载模型（约 1GB）
- 使用生产环境构建：`npm run build`

## 常见问题

### 1. conda 环境未激活
**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**:
```bash
conda activate video-learning
```

### 2. 端口被占用
**错误**: `Address already in use`

**解决**:
```bash
# 查找并杀死占用进程
lsof -i :8000
kill -9 <PID>
```

或修改 `backend/main.py` 中的端口号。

### 3. 视频处理超时
**原因**: 视频文件较大或首次运行需要下载模型

**解决**:
- 使用更短的测试视频（< 1 分钟）
- 等待 Whisper 模型下载完成
- 使用更小的模型（见性能优化）

### 4. AI 分析返回错误
**现象**: 视觉分析失败

**原因**: API 的视觉模型可能不可用

**解决**: 系统已内置智能回退机制，会自动切换到纯文本分析

## 项目状态

- ✅ 后端核心功能（100%）
- ✅ 前端完整界面（100%）
- ✅ 视频缓存（100%）
- ✅ AI 智能回退（100%）
- ✅ 知识库功能（100%）
- ✅ 笔记编辑器（100%）
- ✅ AI 生成笔记（100%）

## 文档

- **[FEATURES.md](FEATURES.md)** - 完整功能列表和使用说明
- **[docs/archive/](docs/archive/)** - 历史开发文档归档

## 开发规范

### 代码风格
- **后端**: 遵循 PEP 8
- **前端**: 使用 ESLint + Prettier
- **命名**:
  - 类名：PascalCase
  - 函数/变量：snake_case (Python) / camelCase (TypeScript)

### 提交规范
```bash
git commit -m "feat: 添加知识库功能"
git commit -m "fix: 修复笔记同步问题"
git commit -m "docs: 更新 README"
```

## License

MIT License

---

**准备好了吗？** 运行 `./start.sh` 开始使用！
