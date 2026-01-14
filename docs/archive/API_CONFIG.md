# API 配置说明

## ✅ 已完成的修改

### 1. 更新了配置文件 (config.py)

- ❌ 移除：Claude API 配置
- ✅ 添加：自定义 API 配置

```python
API_KEY = "sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6"
API_BASE_URL = "https://api.qingyuntop.top/v1/chat/completions"
AI_MODEL = "gpt-4o"
```

### 2. 重写了 AI 客户端 (ai_client.py)

- ❌ 移除：anthropic 库
- ✅ 添加：使用 requests 库调用 API
- ✅ 支持：OpenAI 兼容格式
- ✅ 支持：流式返回

### 3. 更新了依赖 (requirements.txt)

- ❌ 移除：anthropic==0.18.1
- ✅ 添加：requests==2.31.0

### 4. 配置了环境变量 (.env)

```bash
API_KEY=sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6
API_BASE_URL=https://api.qingyuntop.top/v1/chat/completions
```

## 🧪 测试 API

### 方法一：使用测试脚本

```bash
cd backend
python test_api.py
```

如果看到 "✅ API 调用成功！" 说明配置正确。

### 方法二：使用 curl

```bash
curl -X POST https://api.qingyuntop.top/v1/chat/completions \
  -H "Authorization: Bearer sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

## 📝 API 调用格式

### 文本消息

```python
response = requests.post(
    "https://api.qingyuntop.top/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 100
    }
)

result = response.json()
answer = result['choices'][0]['message']['content']
```

### 图片 + 文本消息

```python
response = requests.post(
    "https://api.qingyuntop.top/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "这张图片里有什么？"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64,iVBORw0KGgoAAAANS..."
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }
)
```

### 流式返回

```python
response = requests.post(
    "https://api.qingyuntop.top/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 100,
        "stream": True  # 启用流式
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line_text = line.decode('utf-8')
        if line_text.startswith('data: '):
            data_text = line_text[6:]
            if data_text == '[DONE]':
                break
            data = json.loads(data_text)
            if 'choices' in data:
                delta = data['choices'][0].get('delta', {})
                if 'content' in delta:
                    print(delta['content'], end='')
```

## 🚀 启动服务

现在可以启动后端服务了：

```bash
cd backend
python main.py
```

访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/

## ✨ 功能说明

### 1. 视频分析

上传视频后，系统会：
1. 提取 5 个关键帧（base64 格式）
2. 生成字幕（前 3000 字）
3. 调用你的 API 分析视频内容
4. 返回摘要、知识点、章节划分

### 2. AI 问答

截图提问时，系统会：
1. 获取当前帧（base64 格式）
2. 获取前后 30 秒的字幕
3. 获取视频分析信息
4. 调用你的 API（流式返回）
5. 实时显示回答

## 🐛 常见问题

### 1. API 调用失败

**错误**：`API 调用失败: 401`

**原因**：API Key 错误

**解决**：检查 `.env` 文件中的 `API_KEY` 是否正确

### 2. 超时错误

**错误**：`timeout`

**原因**：网络问题或 API 响应慢

**解决**：增加 `timeout` 参数（当前设置为 60 秒）

### 3. 模型不支持视觉

**错误**：API 返回错误，提示不支持图片

**原因**：模型不支持 vision 功能

**解决**：确认使用 `gpt-4o` 或其他支持视觉的模型

## 📞 需要帮助？

如果遇到问题：
1. 先运行 `python test_api.py` 测试 API 是否可用
2. 查看后端控制台的错误信息
3. 检查 API 配置是否正确
