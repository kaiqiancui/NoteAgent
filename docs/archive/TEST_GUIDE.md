# 🧪 阶段 A：后端功能测试指南

## 前置准备

### 1. 启动后端服务

**在终端窗口 1**（保持运行）：

```bash
conda activate map
cd /Users/cuikq/myself/lessons/2025fa/Note/backend
python main.py
```

**确认服务启动成功**：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. 运行自动化测试

**在终端窗口 2**（新开一个终端）：

```bash
conda activate map
cd /Users/cuikq/myself/lessons/2025fa/Note
python test_backend.py
```

## 测试内容

测试脚本会自动执行以下测试：

### ✅ 测试 1：健康检查
验证服务是否正常运行

### ✅ 测试 2：视频上传
- 上传 `examlpe_video.mp4`
- 提取关键帧
- 生成字幕
- AI 分析视频
- **预计耗时：2-5 分钟**

### ✅ 测试 3：获取视频信息
验证视频数据是否正确存储

### ✅ 测试 4：创建笔记
创建 3 条不同类型的笔记：
- 重要知识点
- 疑问
- 灵感

### ✅ 测试 5：获取笔记列表
查询所有笔记

### ✅ 测试 6：更新笔记
修改第一条笔记的内容

### ✅ 测试 7：导出笔记
导出为 Markdown 文件

### ✅ 测试 8：获取视频帧
截取第 5 秒的视频帧

## 预期输出

### 成功时的输出示例：

```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
视频学习辅助智能体 - 后端 API 测试
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

============================================================
  1. 测试健康检查
============================================================

状态码: 200
响应: {
  "status": "ok",
  "message": "Video Learning Assistant API",
  "version": "1.0.0"
}
✅ 健康检查通过

============================================================
  2. 测试视频上传
============================================================

上传视频: /Users/cuikq/myself/lessons/2025fa/Note/examlpe_video.mp4
⏳ 正在处理，请耐心等待（可能需要几分钟）...

状态码: 200

✅ 视频上传成功！

视频 ID: 12345678-1234-1234-1234-123456789abc
时长: 120.50 秒

AI 分析结果:
{
  "summary": "这是一个关于...的视频",
  "topics": ["知识点1", "知识点2", "知识点3"],
  "chapters": [
    {"time": 0, "title": "开始"},
    {"time": 30, "title": "第一部分"}
  ]
}

============================================================
  3. 测试获取视频信息
============================================================

状态码: 200

✅ 获取成功
文件名: examlpe_video.mp4
时长: 120.50 秒
字幕片段数: 45

...（后续测试输出）

============================================================
  ✅ 测试完成
============================================================

视频 ID: 12345678-1234-1234-1234-123456789abc
笔记数量: 3

所有核心功能测试通过！🎉

可以开始前端开发了。
```

## 测试过程中可能出现的问题

### 问题 1：连接失败

**错误**：
```
curl: (7) Failed to connect to localhost port 8000
```

**原因**：后端服务未启动

**解决**：
在终端窗口 1 启动后端服务

### 问题 2：视频处理超时

**错误**：
```
Timeout error
```

**原因**：视频太大或处理时间过长

**解决**：
- 等待更长时间
- 或使用更短的测试视频（< 1 分钟）

### 问题 3：Whisper 模型下载

**现象**：第一次运行时卡在字幕生成

**原因**：Whisper 正在下载模型（约 1GB）

**解决**：
- 耐心等待（只需要下载一次）
- 或者临时使用更小的模型：

编辑 `backend/config.py`：
```python
WHISPER_MODEL_SIZE = "base"  # 从 medium 改为 base
```

### 问题 4：API 调用失败

**错误**：
```
API 调用失败: 401
```

**原因**：API Key 失效

**解决**：
检查 `backend/.env` 中的 API_KEY

## 测试后的文件

测试完成后会生成：

- `exported_notes_{video_id}.md` - 导出的笔记文件
- `data/videos/{video_id}.json` - 视频信息
- `data/notes/{video_id}.json` - 笔记数据

## 手动测试（可选）

如果自动化测试失败，可以手动测试：

### 方法 1：使用 API 文档页面

1. 访问 http://localhost:8000/docs
2. 找到相应的接口
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"

### 方法 2：使用 curl

```bash
# 上传视频
curl -X POST "http://localhost:8000/api/videos/upload" \
  -F "file=@examlpe_video.mp4"

# 创建笔记
curl -X POST "http://localhost:8000/api/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "你的video_id",
    "timestamp": 10.5,
    "type": "important",
    "content": "测试笔记"
  }'
```

## 下一步

测试通过后，进入 **阶段 B：创建简单测试页面**

---

**立即开始测试**：

```bash
# 终端 1
conda activate map
cd backend
python main.py

# 终端 2（新开）
conda activate map
python test_backend.py
```
