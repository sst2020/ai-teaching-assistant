#!/usr/bin/env python3
import requests
import json

print("Testing ChatGLM4-6B...")

payload = {
    "model": "chatglm4-6b",
    "messages": [{"role": "user", "content": "Say 'Hello, I am working!'"}],
    "max_tokens": 30
}

try:
    print("Sending request...")
    response = requests.post(
        'http://localhost:8000/v1/chat/completions',
        headers={'Content-Type': 'application/json'},
        json=payload,
        timeout=120
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['choices'][0]['message']['content']}")
        print("✅ SUCCESS!")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

