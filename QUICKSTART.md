# 快速启动指南

> 从零到运行，5分钟搞定！

## 前置要求

- Python 3.10+
- Conda 环境管理器（已安装 `map` 环境）
- ffmpeg（视频处理，conda 环境中已安装）

## 一键启动

### 方法 1：使用启动脚本

```bash
./start.sh
```

### 方法 2：手动启动

```bash
conda activate map
cd backend
python main.py
```

## 验证服务

启动成功后访问：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/

期望输出：
```json
{
  "status": "ok",
  "message": "Video Learning Assistant API",
  "version": "1.0.0"
}
```

## 配置说明

### 当前 API 配置

系统已配置为使用自定义 API：

```bash
# backend/.env
API_KEY=sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6
API_BASE_URL=https://api.qingyuntop.top/v1/chat/completions
```

**使用的模型**: `gpt-4o`（支持视觉分析）

### 测试 API 连接

```bash
cd backend
python test_ai_analysis.py
```

期望看到：
```
✅ AI 分析成功！
✅ 所有测试通过！AI 功能正常工作
```

## 快速测试流程

### 1. 上传视频（API 文档页面）

1. 访问 http://localhost:8000/docs
2. 找到 `POST /api/videos/upload`
3. 点击 "Try it out"
4. 选择测试视频（建议 < 2 分钟）
5. 点击 "Execute"

**注意**：首次上传会进行完整处理（2-5 分钟），之后会使用缓存（<1 秒）

### 2. 查看结果

上传成功后会返回：
```json
{
  "video_id": "972cb1ad-88dd-4b58-ae8f-362ce84e6419",
  "duration": 120.5,
  "analysis": {
    "summary": "视频内容摘要...",
    "topics": ["知识点1", "知识点2"],
    "chapters": [{"time": 0, "title": "章节1"}]
  },
  "cached": false
}
```

### 3. 创建笔记

使用 `POST /api/notes` 接口：
```json
{
  "video_id": "你的video_id",
  "timestamp": 10.5,
  "type": "important",
  "content": "这是一个重要知识点"
}
```

### 4. 导出笔记

使用 `GET /api/notes/export/{video_id}` 导出 Markdown 格式笔记。

## 常见问题

### 问题 1：conda 环境未激活

**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**:
```bash
conda activate map
```

### 问题 2：端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查找并杀死占用进程
lsof -i :8000
kill -9 <PID>
```

或修改 `backend/main.py` 中的端口号。

### 问题 3：视频处理超时

**原因**: 视频文件较大或首次运行 Whisper 需要下载模型

**解决**:
- 使用更短的测试视频（< 1 分钟）
- 等待 Whisper 模型下载完成（首次约 1GB）
- 或临时使用更小的模型：修改 `config.py` 中的 `WHISPER_MODEL_SIZE = "base"`

### 问题 4：AI 分析返回错误

**现象**: 视觉分析失败，提示无法分析图片

**原因**: API 的视觉模型可能不可用

**解决**: 系统已内置智能回退机制，会自动切换到纯文本分析（基于字幕）

## 性能优化

### 加快处理速度

编辑 `backend/config.py`:
```python
WHISPER_MODEL_SIZE = "base"  # 使用更小的模型（medium -> base）
MAX_KEYFRAMES = 3             # 减少关键帧数量（5 -> 3）
```

### 使用 GPU 加速（如果有 NVIDIA GPU）

```python
WHISPER_DEVICE = "cuda"  # 从 cpu 改为 cuda
```

## 视频缓存功能

系统会自动缓存已处理的视频（通过 MD5 hash 识别）：
- **首次上传**: 完整处理（2-5 分钟）
- **再次上传相同视频**: 使用缓存（< 1 秒）

**缓存命中条件**: 视频文件内容完全相同（即使文件名不同也会命中）

## 下一步

服务启动成功后：
1. 查看完整功能列表：[FEATURES.md](FEATURES.md)
2. 了解开发架构：[DEVELOPMENT.md](DEVELOPMENT.md)
3. 开始前端开发

---

**遇到问题？** 检查终端输出的错误信息，或运行 `python backend/test_ai_analysis.py` 测试 AI 功能。
