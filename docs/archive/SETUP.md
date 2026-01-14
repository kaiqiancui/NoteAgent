# 项目启动指南

## 📁 项目结构

```
video-learning-assistant/
├── backend/              # Python 后端
│   ├── main.py          # FastAPI 主程序（启动这个）
│   ├── config.py        # 配置管理
│   ├── storage.py       # JSON 存储
│   ├── test_api.py      # API 测试脚本
│   ├── .env             # 环境变量（已配置）
│   ├── core/            # 核心工具类
│   │   ├── video_processor.py
│   │   ├── transcript_gen.py
│   │   ├── ai_client.py
│   │   └── prompts.py
│   └── services/        # 业务服务层
│       ├── video_service.py
│       ├── note_service.py
│       └── ai_service.py
├── frontend/            # React 前端（待创建）
├── uploads/             # 视频文件存储
├── data/                # JSON 数据存储
│   ├── videos/          # 视频信息
│   └── notes/           # 笔记信息
└── start.sh             # 一键启动脚本
```

## 🚀 快速启动

### 方式一：使用启动脚本（推荐）

```bash
./start.sh
```

脚本会自动：
1. 检查 conda 环境
2. 激活 map 环境
3. 启动后端服务

### 方式二：手动启动

```bash
# 1. 激活 conda 环境
conda activate map

# 2. 进入后端目录
cd backend

# 3. 启动服务
python main.py
```

## ⚙️ 环境配置

### 当前配置

- **Conda 环境**: `map`
- **Python 版本**: 3.10+
- **API 配置**:
  - API Key: `sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6`
  - API URL: `https://api.qingyuntop.top/v1/chat/completions`
  - 模型: `gpt-4o`

### 依赖已安装

所有依赖已在 `map` 环境中安装：
- ✅ fastapi
- ✅ uvicorn
- ✅ requests (用于 API 调用)
- ✅ moviepy (视频处理)
- ✅ faster-whisper (字幕生成)
- ✅ opencv-python (图像处理)
- ✅ python-dotenv (环境变量)

## 🧪 测试

### 1. 测试 API 连接

```bash
conda activate map
cd backend
python test_api.py
```

**期望输出**：
```
测试 API 连接...
API URL: https://api.qingyuntop.top/v1/chat/completions
API KEY: sk-1cateP6imWaaQemP...

状态码: 200

✅ API 调用成功！

AI 回复:
你好！我是一个AI助手...
```

### 2. 测试后端服务

启动服务后，访问：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/

### 3. 测试视频上传

准备一个测试视频（建议 < 1 分钟），然后：

```bash
curl -X POST "http://localhost:8000/api/videos/upload" \
  -F "file=@test_video.mp4"
```

**期望输出**：
```json
{
  "video_id": "abc-123-def-456",
  "duration": 45.2,
  "analysis": {
    "summary": "这是一个关于...的视频",
    "topics": ["知识点1", "知识点2"],
    "chapters": [...]
  }
}
```

## 📝 使用说明

### 1. 启动服务

```bash
./start.sh
```

或

```bash
conda activate map
cd backend
python main.py
```

### 2. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

你会看到所有可用的 API 接口，可以直接在页面上测试。

### 3. 上传视频

通过 API 文档的 `/api/videos/upload` 接口上传视频，或使用 curl：

```bash
curl -X POST "http://localhost:8000/api/videos/upload" \
  -F "file=@你的视频.mp4"
```

### 4. 创建笔记

```bash
curl -X POST "http://localhost:8000/api/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "视频ID",
    "timestamp": 120.5,
    "type": "important",
    "content": "这是一个重要知识点"
  }'
```

### 5. 查看笔记

```bash
curl "http://localhost:8000/api/notes/视频ID"
```

### 6. 导出笔记

```bash
curl "http://localhost:8000/api/notes/export/视频ID"
```

## 🐛 常见问题

### 1. conda 环境未激活

**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**:
```bash
conda activate map
```

### 2. 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

或修改端口（在 `main.py` 最后一行）：
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # 改为 8001
```

### 3. 视频处理失败

**错误**: 上传视频后处理失败

**原因**:
- 视频格式不支持
- 视频损坏
- ffmpeg 未安装

**解决**:
```bash
# 安装 ffmpeg（如果未安装）
conda install -c conda-forge ffmpeg
```

### 4. Whisper 模型加载慢

**说明**: 首次运行时，Whisper 会下载模型文件（约 1GB），需要等待几分钟。

**加速方法**: 使用更小的模型
```python
# 在 config.py 中修改
WHISPER_MODEL_SIZE = "base"  # 从 medium 改为 base
```

### 5. API 调用失败

**错误**: `API 调用失败: 401`

**原因**: API Key 错误或过期

**解决**:
1. 检查 `backend/.env` 文件中的 `API_KEY`
2. 确认 API Key 是否有效
3. 运行测试脚本：`python test_api.py`

## 📊 性能优化建议

### 1. 使用更小的模型

如果处理速度慢，可以调整配置：

```python
# config.py
WHISPER_MODEL_SIZE = "base"  # tiny < base < small < medium < large
MAX_KEYFRAMES = 3            # 减少关键帧数量
```

### 2. 使用 GPU 加速

如果有 NVIDIA GPU：

```python
# config.py
WHISPER_DEVICE = "cuda"  # 从 cpu 改为 cuda
```

### 3. 限制视频大小

```python
# config.py
MAX_FILE_SIZE = 100 * 1024 * 1024  # 限制为 100MB
```

## 🎯 下一步

1. ✅ 后端服务已就绪
2. ⏳ 开发前端界面
3. ⏳ 前后端联调
4. ⏳ 功能增强

## 📞 需要帮助？

如果遇到问题：
1. 检查 conda 环境是否激活：`conda info --envs`
2. 查看后端控制台输出
3. 运行 API 测试：`python backend/test_api.py`
4. 查看日志文件（如果有）

---

**准备好了？开始启动吧！**

```bash
./start.sh
```
