"""Direct API test"""
import requests
import json

url = "http://localhost:8000/v1/chat/completions"
data = {
    "model": "qwen2.5-7b",
    "messages": [{"role": "user", "content": "Hello, who are you?"}],
    "max_tokens": 100
}

print("Testing FastChat API...")
print(f"URL: {url}")
print(f"Request: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, timeout=120)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nMessage: {result['choices'][0]['message']['content']}")
        print("\n[SUCCESS] API is working!")
    else:
        print(f"\n[FAIL] API returned error: {response.status_code}")
except Exception as e:
    print(f"\n[FAIL] Error: {e}")

