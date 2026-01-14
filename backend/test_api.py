"""
测试 API 连接
"""
import requests
import json

API_KEY = "sk-1cateP6imWaaQemPGQv2Q4BHwt7jt2ULTZf9DHs4P0jMIsD6"
API_URL = "https://api.qingyuntop.top/v1/chat/completions"

def test_api():
    """测试 API 是否可用"""
    print("测试 API 连接...")
    print(f"API URL: {API_URL}")
    print(f"API KEY: {API_KEY[:20]}...")
    print()

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": "你好，请用一句话介绍你自己。"
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            },
            timeout=30
        )

        print(f"状态码: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("✅ API 调用成功！")
            print()
            print("AI 回复:")
            print(result['choices'][0]['message']['content'])
            print()
            return True
        else:
            print(f"❌ API 调用失败: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    test_api()
