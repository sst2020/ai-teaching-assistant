#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目完整性检查和 DeepSeek API 测试脚本
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 测试用的 DeepSeek API Key
TEST_DEEPSEEK_API_KEY = "sk-abf377836ab548169bf609f6ba675e2b"


def check_project_structure() -> Tuple[bool, List[str]]:
    """检查项目文件结构完整性"""
    print("=" * 60)
    print("📁 检查项目文件结构")
    print("=" * 60)
    
    required_files = [
        # 后端核心文件
        ("backend/app/main.py", "后端主应用文件"),
        ("backend/core/config.py", "后端配置文件"),
        ("backend/services/ai_service.py", "AI 服务文件"),
        ("backend/requirements.txt", "后端依赖文件"),
        
        # 前端核心文件
        ("frontend/package.json", "前端 package.json"),
        ("frontend/src/App.tsx", "前端主应用文件 (TypeScript)"),
        ("frontend/src/App.js", "前端主应用文件 (JavaScript)"),
        
        # 配置文件
        ("backend/.env", "后端环境配置"),
        
        # 测试文件
        ("test_deepseek_api.py", "DeepSeek API 测试脚本"),
        ("verify_deepseek_config.py", "DeepSeek 配置验证脚本"),
    ]
    
    missing_files = []
    all_good = True
    
    for file_path, description in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} (缺失)")
            missing_files.append(file_path)
            all_good = False
    
    print()
    if all_good:
        print("✅ 所有必需文件都存在")
    else:
        print(f"❌ 缺失 {len(missing_files)} 个文件")
    
    return all_good, missing_files


def check_backend_dependencies() -> bool:
    """检查后端依赖是否安装"""
    print("=" * 60)
    print("📦 检查后端依赖")
    print("=" * 60)
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "openai",
        "aiofiles",
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            all_installed = False
    
    print()
    if all_installed:
        print("✅ 所有必需的后端依赖都已安装")
    else:
        print("❌ 部分后端依赖未安装，请运行: pip install -r backend/requirements.txt")
    
    return all_installed


async def test_deepseek_api_connection() -> bool:
    """测试 DeepSeek API 连接"""
    print("=" * 60)
    print("🔌 测试 DeepSeek API 连接")
    print("=" * 60)
    print(f"API Key: {TEST_DEEPSEEK_API_KEY[:20]}...")
    print()
    
    try:
        from openai import AsyncOpenAI
        
        # 创建 DeepSeek 客户端
        client = AsyncOpenAI(
            api_key=TEST_DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        print("📡 发送测试请求...")
        
        # 发送简单的测试请求
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的AI助手。"},
                {"role": "user", "content": "请用一句话介绍你自己。"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        print(f"✅ API 响应成功")
        print(f"📝 回答: {answer}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ API 连接失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_deepseek_provider() -> bool:
    """测试 DeepSeek Provider 集成"""
    print("=" * 60)
    print("🤖 测试 DeepSeek Provider 集成")
    print("=" * 60)

    try:
        # 临时设置环境变量
        os.environ["DEEPSEEK_API_KEY"] = TEST_DEEPSEEK_API_KEY
        os.environ["USE_DEEPSEEK"] = "true"

        # 添加 backend 目录到路径
        backend_dir = project_root / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from services.ai_service import DeepSeekProvider, AIConfig, AIProvider

        # 创建配置
        config = AIConfig(
            provider=AIProvider.DEEPSEEK,
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=100,
            api_key=TEST_DEEPSEEK_API_KEY
        )

        # 创建 Provider
        provider = DeepSeekProvider(config)
        print("✅ DeepSeekProvider 创建成功")

        # 测试基本对话
        print("\n📡 测试基本对话功能...")
        response = await provider.generate_response(
            prompt="什么是Python?",
            system_prompt="你是一位专业的编程教学助手。请用简短的一句话回答。"
        )
        print(f"✅ 回答: {response[:100]}...")

        return True

    except Exception as e:
        print(f"❌ DeepSeek Provider 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🚀 AI 教学助手 - 项目完整性检查")
    print("=" * 60)
    print()
    
    results = {}
    
    # 1. 检查项目结构
    structure_ok, missing = check_project_structure()
    results["项目结构"] = structure_ok
    print()
    
    # 2. 检查后端依赖
    deps_ok = check_backend_dependencies()
    results["后端依赖"] = deps_ok
    print()
    
    # 3. 测试 DeepSeek API 连接
    api_ok = await test_deepseek_api_connection()
    results["DeepSeek API 连接"] = api_ok
    print()
    
    # 4. 测试 DeepSeek Provider
    provider_ok = await test_deepseek_provider()
    results["DeepSeek Provider"] = provider_ok
    print()
    
    # 总结
    print("=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print()
    if all_passed:
        print("🎉 所有测试通过！项目完整性良好，DeepSeek API 通信正常。")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

