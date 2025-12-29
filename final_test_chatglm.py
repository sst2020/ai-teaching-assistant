#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive ChatGLM4-6B Test Suite"""
import requests
import json
import time

def test_model(test_name, prompt, max_tokens=100):
    """Run a single test"""
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")
    print(f"Prompt: {prompt}")
    
    payload = {
        "model": "chatglm4-6b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/v1/chat/completions',
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=120
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            tokens = result.get('usage', {}).get('total_tokens', 'N/A')
            
            print(f"\n[SUCCESS]")
            print(f"Response: {answer}")
            print(f"Time: {elapsed:.2f}s | Tokens: {tokens}")
            return True
        else:
            print(f"\n[FAILED] Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

def main():
    print("="*70)
    print("ChatGLM4-6B Comprehensive Test Suite")
    print("="*70)
    
    # Check API availability
    print("\n[Step 1] Checking API availability...")
    try:
        response = requests.get('http://localhost:8000/v1/models', timeout=10)
        if response.status_code == 200:
            models = response.json()
            model_ids = [m['id'] for m in models['data']]
            print(f"[OK] Available models: {', '.join(model_ids)}")
        else:
            print(f"[FAILED] Cannot connect to API")
            return
    except Exception as e:
        print(f"[ERROR] {e}")
        print("Make sure FastChat services are running!")
        return
    
    # Run tests
    tests = [
        ("Basic Response", "Say 'Hello, I am ChatGLM4!'", 30),
        ("Simple Math", "What is 15 + 27?", 50),
        ("Code Explanation", "Explain what this does: print('Hello')", 80),
        ("Chinese Support", "用中文回答：什么是编程？", 100),
        ("Teaching Scenario", "Explain variables to a beginner programmer in one sentence.", 100),
    ]
    
    results = []
    for test_name, prompt, max_tokens in tests:
        success = test_model(test_name, prompt, max_tokens)
        results.append((test_name, success))
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n*** ALL TESTS PASSED! ChatGLM4-6B is fully operational! ***")
    else:
        print(f"\n*** {total - passed} test(s) failed. Check the output above. ***")

if __name__ == "__main__":
    main()

