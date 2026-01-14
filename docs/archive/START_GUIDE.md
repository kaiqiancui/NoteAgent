# 🚀 启动服务 - 跟我一步步来

## 第一步：确认环境

### 1. 打开终端

在项目根目录 `/Users/cuikq/myself/lessons/2025fa/Note` 打开终端。

### 2. 检查 conda 环境

```bash
conda env list
```

你应该看到 `map` 环境：

```
# conda environments:
#
base                     /Users/xxx/anaconda3
map                   *  /Users/xxx/anaconda3/envs/map
```

### 3. 激活 map 环境

```bash
conda activate map
```

激活成功后，终端提示符会变为：

```
(map) ➜  Note
```

## 第二步：测试 API

在启动完整服务前，先确认 API 可用。

```bash
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
你好！我是一个AI助手，很高兴为你服务...
```

✅ 如果看到这个，说明 API 配置正确！

❌ 如果失败，检查：
- 网络连接是否正常
- API Key 是否正确（查看 `backend/.env`）

## 第三步：启动后端服务

### 方式 A：使用启动脚本（推荐）

回到项目根目录：

```bash
cd ..  # 回到 Note 目录
./start.sh
```

### 方式 B：手动启动

```bash
cd backend
python main.py
```

## 第四步：确认服务启动

启动后你会看到：

```
============================================================
🚀 视频学习辅助智能体后端服务启动中...
============================================================
📁 上传目录: /Users/cuikq/myself/lessons/2025fa/Note/uploads
📁 数据目录: /Users/cuikq/myself/lessons/2025fa/Note/data
🤖 AI 模型: gpt-4o
🎬 Whisper 模型: medium
============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ 看到这些信息说明服务启动成功！

## 第五步：测试服务

### 1. 打开浏览器

访问：http://localhost:8000

你应该看到：

```json
{
  "status": "ok",
  "message": "Video Learning Assistant API",
  "version": "1.0.0"
}
```

### 2. 查看 API 文档

访问：http://localhost:8000/docs

你会看到一个漂亮的 API 文档页面（Swagger UI），列出了所有可用的接口。

### 3. 测试上传接口（可选）

在 API 文档页面：

1. 找到 `POST /api/videos/upload` 接口
2. 点击 "Try it out"
3. 点击 "Choose File" 上传一个小视频（< 1 分钟）
4. 点击 "Execute"
5. 等待处理完成（会显示进度）

## 完整操作流程示例

假设你现在在 `/Users/cuikq/myself/lessons/2025fa/Note` 目录：

```bash
# 1. 激活环境
conda activate map

# 2. 测试 API（确保 API 可用）
cd backend
python test_api.py

# 3. 返回根目录
cd ..

# 4. 启动服务
./start.sh
```

等待几秒钟后，服务就启动了！

然后打开浏览器访问：
- http://localhost:8000 - 健康检查
- http://localhost:8000/docs - API 文档

## 常见启动问题

### 问题 1：conda: command not found

**原因**：conda 未安装或未添加到 PATH

**解决**：
```bash
# 检查 conda 是否安装
which conda

# 如果没有，需要初始化 conda
conda init bash  # 或 zsh
```

重新打开终端后再试。

### 问题 2：No module named 'fastapi'

**原因**：环境未激活或依赖未安装

**解决**：
```bash
# 确认环境已激活
conda activate map

# 如果仍然报错，重新安装依赖
cd backend
pip install -r requirements.txt
```

### 问题 3：Address already in use

**原因**：8000 端口被占用

**解决**：

方法 1 - 杀死占用端口的进程：
```bash
lsof -i :8000
kill -9 <PID>
```

方法 2 - 使用其他端口：

编辑 `backend/main.py` 最后一行：
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # 改为 8001
```

### 问题 4：视频处理时报错

**原因**：缺少 ffmpeg

**解决**：
```bash
conda install -c conda-forge ffmpeg
```

### 问题 5：Whisper 模型下载慢

**说明**：首次运行会下载模型（约 1GB），需要耐心等待。

**加速方法**：

1. 使用更小的模型：

编辑 `backend/config.py`：
```python
WHISPER_MODEL_SIZE = "base"  # 从 medium 改为 base
```

2. 或者跳过字幕功能（临时）：

可以先注释掉字幕生成的代码测试其他功能。

## 停止服务

在运行服务的终端按 `Ctrl+C` 即可停止。

## 查看日志

所有日志都会输出到终端。如果需要保存日志：

```bash
python main.py 2>&1 | tee app.log
```

日志会同时输出到终端和 `app.log` 文件。

## 下一步

服务启动成功后，你可以：

1. 在 API 文档页面测试各个接口
2. 准备一个测试视频上传
3. 查看视频分析结果
4. 测试笔记功能
5. 测试 AI 问答（需要前端配合）

---

**有问题？**

- 查看终端输出的错误信息
- 查看 [SETUP.md](SETUP.md) 中的常见问题
- 运行 `python backend/test_api.py` 测试 API

**准备好了？开始吧！** 🚀
