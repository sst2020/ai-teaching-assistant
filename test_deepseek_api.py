#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API 测试脚本
用于验证 DeepSeek API 集成是否正常工作
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.ai_service import DeepSeekProvider, AIConfig, AIProvider
from backend.core.config import settings

async def test_deepseek_api():
    """测试 DeepSeek API 集成"""
    print("=" * 60)
    print("DeepSeek API 集成测试")
    print("=" * 60)
    
    # 检查 API 密钥是否配置
    if not settings.DEEPSEEK_API_KEY:
        print("⚠️  警告: 未配置 DEEPSEEK_API_KEY")
        print("请在环境变量或 .env 文件中设置 DEEPSEEK_API_KEY")
        print("跳过 API 测试...")
        return False
    
    try:
        # 创建 DeepSeek 配置
        config = AIConfig(
            provider=AIProvider.DEEPSEEK,
            model=settings.DEEPSEEK_MODEL,
            temperature=settings.DEEPSEEK_TEMPERATURE,
            max_tokens=settings.DEEPSEEK_MAX_TOKENS,
            api_key=settings.DEEPSEEK_API_KEY
        )
        
        # 创建 DeepSeek 提供者
        provider = DeepSeekProvider(config)
        print(f"✅ DeepSeekProvider 创建成功")
        print(f"   - 模型: {settings.DEEPSEEK_MODEL}")
        print(f"   - 温度: {settings.DEEPSEEK_TEMPERATURE}")
        print(f"   - 最大 Token: {settings.DEEPSEEK_MAX_TOKENS}")
        
        # 测试1: 基本对话
        print("\n【测试1: 基本对话】")
        try:
            response = await provider.generate_response(
                prompt="请用一句话解释什么是人工智能？",
                system_prompt="你是一位专业的AI教学助手。"
            )
            print(f"✅ 回答: {response[:100]}...")
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
        
        # 测试2: 代码解释
        print("\n【测试2: 代码解释】")
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        try:
            response = await provider.generate_response(
                prompt=f"请解释以下Python代码:\n{code}",
                system_prompt="你是一位编程教学助手。"
            )
            print(f"✅ 回答: {response[:100]}...")
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
        
        # 测试3: 代码反馈
        print("\n【测试3: 代码反馈】")
        test_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
        analysis_results = {
            "style_score": 85,
            "complexity": 7,
            "issues": ["时间复杂度较高 O(n²)", "可以考虑优化算法"]
        }
        try:
            response = await provider.generate_code_feedback(test_code, analysis_results)
            print(f"✅ 反馈: {response[:100]}...")
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
        
        # 测试4: 问题回答
        print("\n【测试4: 问题回答】")
        try:
            result = await provider.answer_question("什么是递归？")
            print(f"✅ 答案: {result['answer'][:100]}...")
            print(f"   - 置信度: {result['confidence']:.2f}")
            print(f"   - 需要教师审核: {result['needs_teacher_review']}")
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ DeepSeek API 集成测试通过！")
        print("所有功能正常工作。")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek API 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_service_with_deepseek():
    """测试 AI 服务与 DeepSeek 集成"""
    print("\n" + "=" * 60)
    print("AI 服务与 DeepSeek 集成测试")
    print("=" * 60)
    
    if not settings.DEEPSEEK_API_KEY:
        print("⚠️  警告: 未配置 DEEPSEEK_API_KEY，跳过测试...")
        return False
    
    try:
        from backend.services.ai_service import AIService, AIConfig, AIProvider
        
        # 创建使用 DeepSeek 的 AI 服务配置
        config = AIConfig(provider=AIProvider.DEEPSEEK)
        ai_service = AIService(config)
        
        print("✅ AI 服务创建成功")
        
        # 测试代码解释功能
        print("\n【测试: 代码解释功能】")
        result = await ai_service.explain_code(
            code="print('Hello, World!')",
            language="python",
            detail_level="basic",
            student_level="beginner"
        )
        if result.get("success"):
            print("✅ 代码解释功能正常")
        else:
            print("❌ 代码解释功能失败")
            return False
        
        # 测试改进建议功能
        print("\n【测试: 改进建议功能】")
        result = await ai_service.suggest_improvements(
            code="def add(a, b): return a + b + 0  # unnecessary addition",
            language="python"
        )
        if result.get("success"):
            print("✅ 改进建议功能正常")
        else:
            print("❌ 改进建议功能失败")
            return False
        
        print("\n" + "=" * 60)
        print("✅ AI 服务与 DeepSeek 集成测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ AI 服务集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("AI 教学助手 - DeepSeek API 迁移测试")
    print(f"配置文件: {settings.Config.env_file}")
    print(f"DeepSeek API 基础 URL: {settings.DEEPSEEK_API_BASE}")
    print(f"DeepSeek 模型: {settings.DEEPSEEK_MODEL}")
    print(f"DeepSeek API 配置状态: {'已配置' if settings.DEEPSEEK_API_KEY else '未配置'}")
    print(f"DeepSeek 启用状态: {'启用' if settings.USE_DEEPSEEK else '禁用'}")
    
    # 运行测试
    success1 = await test_deepseek_api()
    success2 = await test_ai_service_with_deepseek()
    
    print(f"\n测试结果:")
    print(f"- DeepSeek API 测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"- AI 服务集成测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！DeepSeek API 迁移成功完成。")
        return True
    else:
        print(f"\n⚠️  部分测试失败。请检查配置并重试。")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)