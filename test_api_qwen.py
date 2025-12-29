import asyncio
from openai import AsyncOpenAI

async def test_fastchat_api():
    """测试 FastChat API"""
    
    # 创建客户端
    client = AsyncOpenAI(
        api_key="EMPTY",  # FastChat 不需要真实的 API key
        base_url="http://localhost:8000/v1"
    )
    
    print("=" * 60)
    print("FastChat API 功能测试 (Qwen2.5-7B)")
    print("=" * 60)
    print()
    
    # 测试1: 基础对话
    print("[测试1] 基础对话测试")
    print("-" * 60)
    try:
        response = await client.chat.completions.create(
            model="qwen2.5-7b",
            messages=[
                {"role": "system", "content": "你是一位编程教学助手。"},
                {"role": "user", "content": "请用一句话解释什么是递归？"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        print(f"问题: 请用一句话解释什么是递归？")
        print(f"回答: {response.choices[0].message.content}")
        print(f"✓ 测试通过")
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
    print()
    
    # 测试2: 代码解释
    print("[测试2] 代码解释测试")
    print("-" * 60)
    try:
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        response = await client.chat.completions.create(
            model="qwen2.5-7b",
            messages=[
                {"role": "system", "content": "你是一位编程教学助手。"},
                {"role": "user", "content": f"请解释这段代码的功能：\n{code}"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        print(f"代码:\n{code}")
        print(f"解释: {response.choices[0].message.content}")
        print(f"✓ 测试通过")
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
    print()
    
    # 测试3: 中文教学场景
    print("[测试3] 中文教学场景测试")
    print("-" * 60)
    try:
        response = await client.chat.completions.create(
            model="qwen2.5-7b",
            messages=[
                {"role": "system", "content": "你是一位编程教学助手，擅长用简单易懂的方式解释编程概念。"},
                {"role": "user", "content": "我是编程初学者，能否用生活中的例子解释什么是'变量'？"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        print(f"问题: 我是编程初学者，能否用生活中的例子解释什么是'变量'？")
        print(f"回答: {response.choices[0].message.content}")
        print(f"✓ 测试通过")
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
    print()
    
    print("=" * 60)
    print("所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_fastchat_api())

