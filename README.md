# 视频学习辅助智能体

基于 AI 的视频学习辅助工具，帮助学生更高效地学习视频课程。

## 核心功能

- **视频处理**: 自动提取关键帧、生成字幕、AI 分析内容
- **智能笔记**: 快速标记、时间戳关联、Markdown 导出
- **AI 助手**: 上下文感知问答、截图提问、流式回答
- **视频缓存**: 相同视频自动识别，秒级响应

## 快速开始

```bash
# 一键启动
./start.sh

# 或手动启动
conda activate map
cd backend
python main.py
```

访问：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/

## 技术栈

**后端**:
- FastAPI + faster-whisper + moviepy
- 自定义 API（OpenAI 兼容格式）
- JSON 文件存储

**前端** (待开发):
- React 18 + TypeScript + Ant Design

## 项目结构

```
video-learning-assistant/
├── backend/              # Python 后端
│   ├── main.py          # FastAPI 主程序
│   ├── core/            # 核心工具类
│   └── services/        # 业务服务层
├── frontend/            # React 前端（待开发）
├── uploads/             # 视频文件存储
└── data/                # JSON 数据存储
```

## 文档

- **[快速启动指南](QUICKSTART.md)** - 从零到运行，5分钟搞定
- **[开发指南](DEVELOPMENT.md)** - 架构设计、API 说明、前端开发
- **[功能清单](FEATURES.md)** - 完整功能列表和实现细节

## 特色功能

### 视频缓存

- **首次上传**: 完整处理（2-5 分钟）
- **再次上传**: 使用缓存（< 1 秒）
- 基于 MD5 hash 识别相同视频

### AI 智能回退

- 优先使用视觉分析（图片 + 文本）
- 视觉失败自动切换到纯文本分析
- 确保 AI 功能始终可用

## 使用示例

### 上传视频

```bash
curl -X POST "http://localhost:8000/api/videos/upload" \
  -F "file=@lecture.mp4"
```

### 创建笔记

```bash
curl -X POST "http://localhost:8000/api/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "abc-123",
    "timestamp": 120.5,
    "type": "important",
    "content": "重要知识点"
  }'
```

### 导出笔记

```bash
curl "http://localhost:8000/api/notes/export/abc-123"
```

## 常见问题

### conda 环境未激活

```bash
conda activate map
```

### 端口被占用

```bash
lsof -i :8000
kill -9 <PID>
```

### 视频处理慢

修改 `backend/config.py`:
```python
WHISPER_MODEL_SIZE = "base"  # 使用更小的模型
MAX_KEYFRAMES = 3             # 减少关键帧数量
```

## 项目状态

- ✅ 后端核心功能（100%）
- ✅ API 接口（100%）
- ✅ 视频缓存（100%）
- ✅ AI 智能回退（100%）
- ⏳ 前端界面（0%）

## 下一步计划

1. 开发前端界面（React + TypeScript）
2. 实现视频播放器
3. 实现笔记编辑器
4. 实现 AI 助手界面
5. 前后端联调

## License

MIT License

---

**准备好了吗？** 查看 [快速启动指南](QUICKSTART.md) 开始使用！
