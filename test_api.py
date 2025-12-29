#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FastChat API 测试脚本"""
import sys
import asyncio
import time
from openai import AsyncOpenAI

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_fastchat_api():
    """测试FastChat API"""
    client = AsyncOpenAI(
        api_key="EMPTY",
        base_url="http://localhost:8000/v1"
    )
    
    print("=" * 60)
    print("FastChat API 测试")
    print("=" * 60)
    
    # 测试1: 基本对话
    print("\n【测试1: 基本对话】")
    start_time = time.time()
    try:
        response = await client.chat.completions.create(
            model="chatglm4-6b",
            messages=[
                {"role": "system", "content": "你是一位编程教学助手。"},
                {"role": "user", "content": "请用一句话解释什么是递归？"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        elapsed = time.time() - start_time
        print(f"回答: {response.choices[0].message.content}")
        print(f"耗时: {elapsed:.2f}秒")
        print(f"Token使用: {response.usage.total_tokens if response.usage else 'N/A'}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试2: 代码解释
    print("\n【测试2: 代码解释】")
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    start_time = time.time()
    try:
        response = await client.chat.completions.create(
            model="chatglm4-6b",
            messages=[
                {"role": "user", "content": f"请解释以下Python代码:\n{code}"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        elapsed = time.time() - start_time
        print(f"回答: {response.choices[0].message.content}")
        print(f"耗时: {elapsed:.2f}秒")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试3: 中文教学场景
    print("\n【测试3: 中文教学场景】")
    start_time = time.time()
    try:
        response = await client.chat.completions.create(
            model="chatglm4-6b",
            messages=[
                {"role": "system", "content": "你是一位耐心的编程老师。"},
                {"role": "user", "content": "我是编程初学者，什么是变量？请用简单的语言解释。"}
            ],
            temperature=0.7,
            max_tokens=250
        )
        elapsed = time.time() - start_time
        print(f"回答: {response.choices[0].message.content}")
        print(f"耗时: {elapsed:.2f}秒")
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")

if __name__ == "__main__":
    asyncio.run(test_fastchat_api())

