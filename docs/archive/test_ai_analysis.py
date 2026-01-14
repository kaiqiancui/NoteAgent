#!/usr/bin/env python3
"""
测试 AI 分析功能（不需要处理视频）
"""
import sys
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from core.ai_client import AIClient

def test_text_only_analysis():
    """测试纯文本分析"""
    print("=" * 60)
    print("测试 AI 文本分析功能")
    print("=" * 60)

    # 创建 AI 客户端
    client = AIClient()

    # 测试用的字幕文本
    sample_transcript = """
    大家好，今天我们来学习 Python 编程的基础知识。
    首先，我们要了解什么是变量。变量就像是一个容器，可以存储数据。
    比如说，我们可以创建一个变量 x，并给它赋值为 10。
    在 Python 中，我们使用等号来进行赋值操作。
    接下来，我们学习条件语句。if 语句可以让程序根据条件做出不同的判断。
    当条件为真时，执行 if 代码块中的内容。
    最后，我们来看看循环。for 循环可以重复执行某段代码。
    这对于处理列表等数据结构非常有用。
    好的，今天的课程就到这里，谢谢大家。
    """

    print("\n📝 测试字幕内容:")
    print("-" * 60)
    print(sample_transcript[:200] + "...")
    print("-" * 60)

    print("\n🤖 正在调用 AI 分析...")

    try:
        # 直接调用文本分析方法
        result = client._analyze_with_text_only(sample_transcript)

        print("\n✅ AI 分析成功！\n")
        print("=" * 60)
        print("分析结果:")
        print("=" * 60)

        print(f"\n📊 内容摘要:")
        print(f"  {result.get('summary', '无')}")

        print(f"\n📚 知识点列表:")
        for i, topic in enumerate(result.get('topics', []), 1):
            print(f"  {i}. {topic}")

        print(f"\n📖 章节划分:")
        for chapter in result.get('chapters', []):
            print(f"  {chapter.get('time', 0)}秒 - {chapter.get('title', '无标题')}")

        print(f"\n🎯 难度等级: {result.get('difficulty', '未知')}")

        print("\n" + "=" * 60)
        print("✅ 测试完成！AI 分析功能正常工作")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_vision_fallback():
    """测试带回退机制的完整分析"""
    print("\n\n" + "=" * 60)
    print("测试完整分析流程（带视觉分析回退）")
    print("=" * 60)

    client = AIClient()

    sample_transcript = "这是一个测试视频的字幕内容。"

    # 使用空的关键帧列表（模拟视觉分析失败的情况）
    keyframes = []

    print("\n🤖 正在调用 analyze_video()...")
    print("（应该会自动从视觉分析回退到文本分析）\n")

    try:
        result = client.analyze_video(keyframes, sample_transcript)

        print("\n✅ 分析完成！")
        print(f"摘要: {result.get('summary', '无')[:100]}...")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 开始测试 AI 分析功能\n")

    # 测试 1：纯文本分析
    success1 = test_text_only_analysis()

    # 测试 2：带回退的完整分析
    success2 = test_with_vision_fallback()

    # 总结
    print("\n\n" + "🎉" * 30)
    print("测试总结:")
    print(f"  文本分析: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"  回退机制: {'✅ 通过' if success2 else '❌ 失败'}")

    if success1 and success2:
        print("\n✅ 所有测试通过！AI 功能正常工作")
        print("现在可以重新启动后端服务，缓存的视频会直接使用")
    else:
        print("\n⚠️ 部分测试失败，请检查 API 配置")

    print("🎉" * 30)
