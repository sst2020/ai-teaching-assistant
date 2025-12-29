import asyncio
from openai import AsyncOpenAI

async def test_fastchat_api():
    """测试 FastChat API"""
    
    # 创建客户端
    client = AsyncOpenAI(
        api_key="EMPTY",
        base_url="http://localhost:8000/v1"
    )
    
    print("=" * 60)
    print("FastChat API Test (Qwen2.5-7B)")
    print("=" * 60)
    print()
    
    # 测试1: 基础对话
    print("[Test 1] Basic Conversation")
    print("-" * 60)
    try:
        response = await client.chat.completions.create(
            model="qwen2.5-7b",
            messages=[
                {"role": "system", "content": "You are a programming teaching assistant."},
                {"role": "user", "content": "Explain recursion in one sentence."}
            ],
            temperature=0.7,
            max_tokens=200
        )
        print(f"Question: Explain recursion in one sentence.")
        print(f"Answer: {response.choices[0].message.content}")
        print(f"[PASS]")
    except Exception as e:
        print(f"[FAIL]: {str(e)}")
    print()
    
    # 测试2: 代码解释
    print("[Test 2] Code Explanation")
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
                {"role": "system", "content": "You are a programming teaching assistant."},
                {"role": "user", "content": f"Explain this code:\n{code}"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        print(f"Code:\n{code}")
        print(f"Explanation: {response.choices[0].message.content}")
        print(f"[PASS]")
    except Exception as e:
        print(f"[FAIL]: {str(e)}")
    print()
    
    # 测试3: 中文对话
    print("[Test 3] Chinese Conversation")
    print("-" * 60)
    try:
        response = await client.chat.completions.create(
            model="qwen2.5-7b",
            messages=[
                {"role": "system", "content": "You are a programming teaching assistant."},
                {"role": "user", "content": "用中文解释什么是变量"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        print(f"Question: What is a variable (in Chinese)?")
        print(f"Answer: {response.choices[0].message.content}")
        print(f"[PASS]")
    except Exception as e:
        print(f"[FAIL]: {str(e)}")
    print()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_fastchat_api())

