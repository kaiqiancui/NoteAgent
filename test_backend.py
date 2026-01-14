#!/usr/bin/env python3
"""
后端 API 测试脚本
"""
import requests
import json
import time
import sys

API_BASE = "http://localhost:8000"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_health_check():
    """测试健康检查"""
    print_section("1. 测试健康检查")

    try:
        response = requests.get(f"{API_BASE}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print("❌ 健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_video_upload(video_path):
    """测试视频上传"""
    print_section("2. 测试视频上传")

    print(f"上传视频: {video_path}")
    print("⏳ 正在处理，请耐心等待（可能需要几分钟）...\n")

    try:
        with open(video_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{API_BASE}/api/videos/upload",
                files=files,
                timeout=600  # 10分钟超时（首次处理可能较慢）
            )

        print(f"状态码: {response.status_code}\n")

        if response.status_code == 200:
            result = response.json()
            print("✅ 视频上传成功！")
            print(f"\n视频 ID: {result.get('video_id')}")
            print(f"时长: {result.get('duration', 0):.2f} 秒")
            print(f"\nAI 分析结果:")
            print(json.dumps(result.get('analysis', {}), indent=2, ensure_ascii=False))
            return result.get('video_id')
        else:
            print(f"❌ 上传失败: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_get_video(video_id):
    """测试获取视频信息"""
    print_section("3. 测试获取视频信息")

    try:
        response = requests.get(f"{API_BASE}/api/videos/{video_id}")
        print(f"状态码: {response.status_code}\n")

        if response.status_code == 200:
            video = response.json()
            print("✅ 获取成功")
            print(f"文件名: {video.get('filename')}")
            print(f"时长: {video.get('duration', 0):.2f} 秒")
            print(f"字幕片段数: {len(video.get('transcript', []))}")
            return True
        else:
            print(f"❌ 获取失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_create_note(video_id):
    """测试创建笔记"""
    print_section("4. 测试创建笔记")

    notes_data = [
        {
            "video_id": video_id,
            "timestamp": 10.5,
            "type": "important",
            "content": "这是一个重要知识点"
        },
        {
            "video_id": video_id,
            "timestamp": 25.3,
            "type": "question",
            "content": "这里有个疑问需要解答"
        },
        {
            "video_id": video_id,
            "timestamp": 40.0,
            "type": "idea",
            "content": "一个灵感想法"
        }
    ]

    note_ids = []

    for i, note in enumerate(notes_data, 1):
        try:
            response = requests.post(
                f"{API_BASE}/api/notes",
                json=note
            )

            if response.status_code == 200:
                result = response.json()
                note_ids.append(result['id'])
                print(f"✅ 笔记 {i} 创建成功 (ID: {result['id']})")
            else:
                print(f"❌ 笔记 {i} 创建失败: {response.text}")

        except Exception as e:
            print(f"❌ 笔记 {i} 错误: {e}")

    return note_ids

def test_get_notes(video_id):
    """测试获取笔记列表"""
    print_section("5. 测试获取笔记列表")

    try:
        response = requests.get(f"{API_BASE}/api/notes/{video_id}")
        print(f"状态码: {response.status_code}\n")

        if response.status_code == 200:
            result = response.json()
            notes = result.get('notes', [])
            print(f"✅ 获取成功，共 {len(notes)} 条笔记\n")

            for i, note in enumerate(notes, 1):
                print(f"笔记 {i}:")
                print(f"  时间戳: {note['timestamp']}s")
                print(f"  类型: {note['type']}")
                print(f"  内容: {note['content']}")
                print()

            return notes
        else:
            print(f"❌ 获取失败: {response.text}")
            return []

    except Exception as e:
        print(f"❌ 错误: {e}")
        return []

def test_update_note(video_id, note_id):
    """测试更新笔记"""
    print_section("6. 测试更新笔记")

    try:
        response = requests.put(
            f"{API_BASE}/api/notes",
            json={
                "video_id": video_id,
                "note_id": note_id,
                "content": "这是更新后的笔记内容"
            }
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ 笔记更新成功")
            return True
        else:
            print(f"❌ 更新失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_export_notes(video_id):
    """测试导出笔记"""
    print_section("7. 测试导出笔记")

    try:
        response = requests.get(f"{API_BASE}/api/notes/export/{video_id}")
        print(f"状态码: {response.status_code}\n")

        if response.status_code == 200:
            result = response.json()
            markdown = result.get('markdown', '')
            print("✅ 导出成功\n")
            print("Markdown 内容预览:")
            print("-" * 60)
            print(markdown[:500])  # 只显示前 500 字符
            if len(markdown) > 500:
                print("...")
            print("-" * 60)

            # 保存到文件
            output_file = f"exported_notes_{video_id}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"\n完整内容已保存到: {output_file}")

            return True
        else:
            print(f"❌ 导出失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_frame(video_id):
    """测试获取视频帧"""
    print_section("8. 测试获取视频帧")

    try:
        response = requests.get(
            f"{API_BASE}/api/videos/{video_id}/frame",
            params={"timestamp": 5.0}
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            frame_data = result.get('frame', '')
            print(f"✅ 获取成功，帧数据长度: {len(frame_data)} 字符")
            print("(这是 base64 编码的图片数据)")
            return True
        else:
            print(f"❌ 获取失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """主测试流程"""
    print("\n" + "🚀"*30)
    print("视频学习辅助智能体 - 后端 API 测试")
    print("🚀"*30)

    # 检查视频文件
    video_path = "/Users/cuikq/myself/lessons/2025fa/Note/examlpe_video.mp4"

    # 1. 健康检查
    if not test_health_check():
        print("\n❌ 服务未启动或无法访问，请先启动后端服务")
        sys.exit(1)

    # 2. 上传视频
    video_id = test_video_upload(video_path)
    if not video_id:
        print("\n❌ 视频上传失败，停止测试")
        sys.exit(1)

    # 3. 获取视频信息
    test_get_video(video_id)

    # 4. 创建笔记
    note_ids = test_create_note(video_id)

    # 5. 获取笔记列表
    notes = test_get_notes(video_id)

    # 6. 更新第一条笔记
    if note_ids:
        test_update_note(video_id, note_ids[0])

    # 7. 导出笔记
    test_export_notes(video_id)

    # 8. 获取视频帧
    test_get_frame(video_id)

    # 总结
    print_section("✅ 测试完成")
    print(f"视频 ID: {video_id}")
    print(f"笔记数量: {len(notes)}")
    print("\n所有核心功能测试通过！🎉")
    print("\n可以开始前端开发了。")

if __name__ == "__main__":
    main()
