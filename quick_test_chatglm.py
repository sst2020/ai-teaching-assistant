#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick ChatGLM Model Test"""
import sys
import requests
import json

# Set UTF-8 output for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 70)
print("ChatGLM4-6B Quick Test")
print("=" * 70)

# Test 1: Check available models
print("\n[Test 1] Checking available models...")
try:
    response = requests.get('http://localhost:8000/v1/models')
    if response.status_code == 200:
        models = response.json()
        print("✅ API is accessible!")
        print(f"Available models: {json.dumps(models, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Failed: Status code {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure FastChat services are running!")
    sys.exit(1)

# Test 2: Simple chat completion
print("\n[Test 2] Testing chat completion...")
try:
    payload = {
        "model": "chatglm4-6b",
        "messages": [
            {"role": "user", "content": "Hello! Please respond with 'ChatGLM is working!' if you can read this."}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    response = requests.post(
        'http://localhost:8000/v1/chat/completions',
        headers={'Content-Type': 'application/json'},
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        answer = result['choices'][0]['message']['content']
        print(f"✅ Model Response: {answer}")
        print(f"   Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
    else:
        print(f"❌ Failed: Status code {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Chinese language test
print("\n[Test 3] Testing Chinese language support...")
try:
    payload = {
        "model": "chatglm4-6b",
        "messages": [
            {"role": "user", "content": "用中文回答：什么是人工智能？（请用一句话回答）"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    response = requests.post(
        'http://localhost:8000/v1/chat/completions',
        headers={'Content-Type': 'application/json'},
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        answer = result['choices'][0]['message']['content']
        print(f"✅ Model Response: {answer}")
    else:
        print(f"❌ Failed: Status code {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 4: Code explanation test
print("\n[Test 4] Testing code explanation...")
try:
    code = """def hello():
    print("Hello, World!")"""
    
    payload = {
        "model": "chatglm4-6b",
        "messages": [
            {"role": "user", "content": f"Explain this Python code in one sentence:\n{code}"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    response = requests.post(
        'http://localhost:8000/v1/chat/completions',
        headers={'Content-Type': 'application/json'},
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        answer = result['choices'][0]['message']['content']
        print(f"✅ Model Response: {answer}")
    else:
        print(f"❌ Failed: Status code {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ All tests passed! ChatGLM4-6B is working correctly!")
print("=" * 70)

