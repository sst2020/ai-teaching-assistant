"""测试登录 API"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试教师账号登录"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "student_id": "1000000001",
        "password": "teacher123"
    }
    
    print(f"请求 URL: {url}")
    print(f"请求数据: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== 登录成功 ===")
            print(f"用户信息: {json.dumps(result['user'], indent=2, ensure_ascii=False)}")
            print(f"Access Token: {result['tokens']['access_token'][:50]}...")
            print(f"Token 类型: {result['tokens']['token_type']}")
            print(f"过期时间: {result['tokens']['expires_in']} 秒")
        else:
            print(f"\n=== 登录失败 ===")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"\n请求失败: {e}")


if __name__ == '__main__':
    test_login()

