"""
Quick FastChat Integration Test
快速测试FastChat集成是否正常工作
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService
from core.config import settings


async def test_basic_response():
    """测试基本响应功能"""
    print("\n" + "=" * 60)
    print("快速测试: FastChat基本响应")
    print("=" * 60)
    print(f"配置: USE_FASTCHAT={settings.USE_FASTCHAT}")
    print(f"API地址: {settings.FASTCHAT_API_BASE}")
    print(f"模型: {settings.FASTCHAT_MODEL_NAME}")
    print(f"超时: {settings.FASTCHAT_TIMEOUT}秒")
    
    ai_service = AIService()
    
    try:
        print("\n发送测试请求...")
        response = await ai_service.generate_response(
            prompt="用一句话解释什么是Python",
            system_prompt="你是一位编程教学助手"
        )
        
        print(f"\n[SUCCESS] 收到响应:")
        print(f"{response}")
        print(f"\n响应长度: {len(response)} 字符")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_code_feedback_simple():
    """测试简单代码反馈"""
    print("\n" + "=" * 60)
    print("快速测试: 代码反馈")
    print("=" * 60)
    
    ai_service = AIService()
    
    code = "def add(a, b):\n    return a + b"
    analysis = {"style_score": 90, "complexity": 1, "issues": []}
    
    try:
        print(f"\n测试代码:\n{code}")
        print("\n生成反馈...")
        
        feedback = await ai_service.generate_code_feedback(code, analysis)
        
        print(f"\n[SUCCESS] 反馈:")
        print(feedback[:300] + "..." if len(feedback) > 300 else feedback)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 失败: {str(e)}")
        return False


async def main():
    """运行快速测试"""
    print("\n" + "=" * 60)
    print("FastChat 快速集成测试")
    print("=" * 60)
    
    results = []
    
    # Test 1: Basic response
    results.append(("基本响应", await test_basic_response()))
    
    # Test 2: Code feedback
    results.append(("代码反馈", await test_code_feedback_simple()))
    
    # Summary
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    print(f"\n总计: {passed_count}/{total} 测试通过")
    
    if passed_count == total:
        print("\n[SUCCESS] FastChat集成测试通过!")
    else:
        print(f"\n[WARNING] {total - passed_count} 个测试失败")


if __name__ == "__main__":
    asyncio.run(main())

