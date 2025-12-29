"""
FastChat Integration Test Script
测试FastChat与AI教学助手系统的集成
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService, AIConfig, AIProvider
from core.config import settings


async def test_code_feedback():
    """测试代码反馈生成功能"""
    print("\n" + "=" * 60)
    print("测试1: 代码反馈生成")
    print("=" * 60)
    
    ai_service = AIService()
    
    test_code = """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total
"""
    
    analysis_results = {
        "style_score": 75,
        "complexity": 3,
        "issues": [
            "可以使用更简洁的for循环方式",
            "变量命名可以更具描述性"
        ]
    }
    
    try:
        feedback = await ai_service.generate_code_feedback(test_code, analysis_results)
        print(f"\n代码:\n{test_code}")
        print(f"\n分析结果: {analysis_results}")
        print(f"\nAI反馈:\n{feedback}")
        print("\n[PASS] 测试通过")
        return True
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {str(e)}")
        return False


async def test_answer_question():
    """测试学生问答功能"""
    print("\n" + "=" * 60)
    print("测试2: 学生问答")
    print("=" * 60)
    
    ai_service = AIService()
    
    questions = [
        "什么是递归？请用简单的例子说明。",
        "Python中的列表和元组有什么区别？",
        "如何优化一个包含嵌套循环的代码？"
    ]
    
    all_passed = True
    for i, question in enumerate(questions, 1):
        try:
            print(f"\n问题{i}: {question}")
            result = await ai_service.answer_question(question)
            print(f"回答: {result['answer'][:200]}...")
            print(f"置信度: {result['confidence']}")
            print(f"需要教师审核: {result['needs_teacher_review']}")
            print("[PASS] 通过")
        except Exception as e:
            print(f"[FAIL] 失败: {str(e)}")
            all_passed = False
    
    return all_passed


async def test_categorize_question():
    """测试问题智能分类功能"""
    print("\n" + "=" * 60)
    print("测试3: 问题智能分类")
    print("=" * 60)
    
    ai_service = AIService()
    
    test_questions = [
        ("什么是变量？", "basic"),
        ("如何设计一个高性能的缓存系统？", "advanced"),
        ("作业的截止时间是什么时候？", "administrative"),
        ("如何使用装饰器优化代码？", "intermediate")
    ]
    
    all_passed = True
    for question, expected_category in test_questions:
        try:
            category = await ai_service.categorize_question(question)
            status = "[PASS]" if category == expected_category else "[FAIL]"
            print(f"\n问题: {question}")
            print(f"预期分类: {expected_category}")
            print(f"实际分类: {category}")
            print(f"{status} {'通过' if category == expected_category else '未通过'}")

            if category != expected_category:
                all_passed = False
        except Exception as e:
            print(f"[FAIL] 失败: {str(e)}")
            all_passed = False
    
    return all_passed


async def test_chinese_teaching_scenario():
    """测试中文教学场景适配"""
    print("\n" + "=" * 60)
    print("测试4: 中文教学场景适配")
    print("=" * 60)
    
    ai_service = AIService()
    
    # Test code explanation in Chinese
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    try:
        result = await ai_service.explain_code(
            code=code,
            language="python",
            detail_level="medium",
            student_level="beginner"
        )
        
        print(f"\n代码:\n{code}")
        print(f"\n解释:\n{result['explanation'][:300]}...")
        print(f"\n关键概念: {result['key_concepts']}")
        print(f"响应时间: {result['latency_ms']:.2f}ms")
        print("\n[PASS] 测试通过")
        return True
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {str(e)}")
        return False


async def test_api_compatibility():
    """测试与现有前端接口的兼容性"""
    print("\n" + "=" * 60)
    print("测试5: 前端接口兼容性")
    print("=" * 60)
    
    ai_service = AIService()
    
    # Test all main API methods
    tests = []
    
    # Test generate_response
    try:
        response = await ai_service.generate_response(
            "解释Python中的列表推导式",
            "你是一位编程教学助手"
        )
        tests.append(("generate_response", len(response) > 0))
    except Exception as e:
        tests.append(("generate_response", False))
        print(f"generate_response error: {e}")
    
    # Test suggest_improvements
    try:
        result = await ai_service.suggest_improvements(
            "x = []\nfor i in range(10):\n    x.append(i*2)",
            language="python"
        )
        tests.append(("suggest_improvements", result['success']))
    except Exception as e:
        tests.append(("suggest_improvements", False))
        print(f"suggest_improvements error: {e}")
    
    print("\n接口兼容性测试结果:")
    for method, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {method}: {'通过' if passed else '失败'}")

    return all(passed for _, passed in tests)


async def main():
    """运行所有集成测试"""
    print("\n" + "=" * 60)
    print("FastChat 集成测试")
    print("=" * 60)
    print(f"\n配置信息:")
    print(f"- USE_FASTCHAT: {settings.USE_FASTCHAT}")
    print(f"- FASTCHAT_API_BASE: {settings.FASTCHAT_API_BASE}")
    print(f"- FASTCHAT_MODEL_NAME: {settings.FASTCHAT_MODEL_NAME}")
    
    results = []
    
    # Run all tests
    results.append(("代码反馈生成", await test_code_feedback()))
    results.append(("学生问答", await test_answer_question()))
    results.append(("问题分类", await test_categorize_question()))
    results.append(("中文教学场景", await test_chinese_teaching_scenario()))
    results.append(("接口兼容性", await test_api_compatibility()))
    
    # Summary
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS] 通过" if passed else "[FAIL] 失败"
        print(f"{status}: {test_name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    print(f"\n总计: {passed_count}/{total} 测试通过")

    if passed_count == total:
        print("\n[SUCCESS] 所有测试通过! FastChat集成成功!")
    else:
        print(f"\n[WARNING] {total - passed_count} 个测试失败，请检查配置和服务状态")


if __name__ == "__main__":
    asyncio.run(main())

