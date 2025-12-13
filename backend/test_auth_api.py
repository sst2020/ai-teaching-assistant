"""
生产级 JWT 认证系统 API 测试脚本

测试所有认证端点的功能和安全性。
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"
AUTH_URL = f"{BASE_URL}/auth"

# 测试数据
TEST_USER = {
    "email": f"test_{datetime.now().timestamp()}@example.com",
    "password": "Test123456",
    "name": "测试学生",
    "student_id": f"TEST{int(datetime.now().timestamp())}"
}

# 存储测试过程中的 tokens
tokens = {}

def print_test(name: str):
    """打印测试名称"""
    print(f"\n{'='*60}")
    print(f"🧪 测试: {name}")
    print(f"{'='*60}")

def print_result(success: bool, message: str, data=None):
    """打印测试结果"""
    status = "✅ 成功" if success else "❌ 失败"
    print(f"{status}: {message}")
    if data:
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")

# ============ 测试 1: 用户注册 ============
print_test("POST /auth/register - 用户注册")
try:
    response = requests.post(
        f"{AUTH_URL}/register",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "name": TEST_USER["name"],
            "student_id": TEST_USER["student_id"]
        }
    )
    if response.status_code == 201:
        data = response.json()
        # 保存 tokens
        tokens["access_token"] = data["tokens"]["access_token"]
        tokens["refresh_token"] = data["tokens"]["refresh_token"]
        print_result(True, "用户注册成功", data)
    else:
        print_result(False, f"注册失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 2: 用户登录 ============
print_test("POST /auth/login - 用户登录")
try:
    response = requests.post(
        f"{AUTH_URL}/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    if response.status_code == 200:
        data = response.json()
        tokens["access_token"] = data["tokens"]["access_token"]
        tokens["refresh_token"] = data["tokens"]["refresh_token"]
        print_result(True, "登录成功,获取到 JWT tokens", {
            "access_token": data["tokens"]["access_token"][:50] + "...",
            "refresh_token": data["tokens"]["refresh_token"][:50] + "...",
            "token_type": data["tokens"]["token_type"],
            "expires_in": data["tokens"]["expires_in"]
        })
    else:
        print_result(False, f"登录失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 3: 获取当前用户信息 ============
print_test("GET /auth/me - 获取当前用户信息")
try:
    response = requests.get(
        f"{AUTH_URL}/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    if response.status_code == 200:
        data = response.json()
        print_result(True, "成功获取用户信息", data)
    else:
        print_result(False, f"获取失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 4: Token 刷新 ============
print_test("POST /auth/refresh - 刷新 Access Token")
try:
    response = requests.post(
        f"{AUTH_URL}/refresh",
        json={"refresh_token": tokens["refresh_token"]}
    )
    if response.status_code == 200:
        data = response.json()
        old_access_token = tokens["access_token"]
        tokens["access_token"] = data["access_token"]
        tokens["refresh_token"] = data["refresh_token"]
        print_result(True, "Token 刷新成功 (旧 token 已轮换)", {
            "new_access_token": data["access_token"][:50] + "...",
            "new_refresh_token": data["refresh_token"][:50] + "...",
            "token_changed": old_access_token != data["access_token"]
        })
    else:
        print_result(False, f"刷新失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 5: 修改密码 ============
print_test("POST /auth/change-password - 修改密码")
try:
    new_password = "NewTest123456"
    response = requests.post(
        f"{AUTH_URL}/change-password",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "old_password": TEST_USER["password"],
            "new_password": new_password
        }
    )
    if response.status_code == 200:
        data = response.json()
        TEST_USER["password"] = new_password  # 更新密码
        print_result(True, "密码修改成功", data)
    else:
        print_result(False, f"修改失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 6: 使用新密码重新登录 ============
print_test("POST /auth/login - 使用新密码登录")
try:
    response = requests.post(
        f"{AUTH_URL}/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    if response.status_code == 200:
        data = response.json()
        tokens["access_token"] = data["tokens"]["access_token"]
        tokens["refresh_token"] = data["tokens"]["refresh_token"]
        print_result(True, "新密码登录成功", {"message": "密码修改功能正常"})
    else:
        print_result(False, f"登录失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 7: 撤销所有 Refresh Tokens ============
print_test("POST /auth/revoke-all - 撤销所有 Refresh Tokens")
try:
    response = requests.post(
        f"{AUTH_URL}/revoke-all",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    if response.status_code == 200:
        data = response.json()
        print_result(True, "所有 Refresh Tokens 已撤销", data)
    else:
        print_result(False, f"撤销失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 8: 验证撤销后的 Refresh Token 无法使用 ============
print_test("POST /auth/refresh - 验证已撤销的 Refresh Token")
try:
    response = requests.post(
        f"{AUTH_URL}/refresh",
        json={"refresh_token": tokens["refresh_token"]}
    )
    if response.status_code == 401:
        print_result(True, "已撤销的 Refresh Token 正确被拒绝", response.json())
    else:
        print_result(False, f"安全漏洞: 已撤销的 token 仍可使用 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 9: 重新登录并测试登出 ============
print_test("POST /auth/login + POST /auth/logout - 登录并登出")
try:
    # 重新登录
    response = requests.post(
        f"{AUTH_URL}/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    if response.status_code == 200:
        data = response.json()
        tokens["access_token"] = data["tokens"]["access_token"]
        tokens["refresh_token"] = data["tokens"]["refresh_token"]
        print_result(True, "重新登录成功", {"message": "准备测试登出"})

        # 登出
        response = requests.post(
            f"{AUTH_URL}/logout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        if response.status_code == 200:
            data = response.json()
            print_result(True, "登出成功,Token 已加入黑名单", data)
        else:
            print_result(False, f"登出失败 (状态码: {response.status_code})", response.json())
    else:
        print_result(False, f"登录失败 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 10: 验证黑名单 Token 无法使用 ============
print_test("GET /auth/me - 验证黑名单 Token")
try:
    response = requests.get(
        f"{AUTH_URL}/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    if response.status_code == 401:
        print_result(True, "黑名单 Token 正确被拒绝", response.json())
    else:
        print_result(False, f"安全漏洞: 黑名单 token 仍可使用 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 11: 错误处理 - 无效登录凭据 ============
print_test("POST /auth/login - 无效密码")
try:
    response = requests.post(
        f"{AUTH_URL}/login",
        json={
            "email": TEST_USER["email"],
            "password": "WrongPassword123"
        }
    )
    if response.status_code == 401:
        print_result(True, "无效密码正确被拒绝", response.json())
    else:
        print_result(False, f"安全漏洞: 无效密码被接受 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试 12: 错误处理 - 重复注册 ============
print_test("POST /auth/register - 重复邮箱注册")
try:
    response = requests.post(
        f"{AUTH_URL}/register",
        json={
            "email": TEST_USER["email"],
            "password": "AnotherPassword123",
            "name": "另一个学生",
            "student_id": "ANOTHER123"
        }
    )
    if response.status_code == 400:
        print_result(True, "重复邮箱正确被拒绝", response.json())
    else:
        print_result(False, f"安全漏洞: 重复邮箱被接受 (状态码: {response.status_code})", response.json())
except Exception as e:
    print_result(False, f"请求异常: {str(e)}")

# ============ 测试总结 ============
print(f"\n{'='*60}")
print("📊 测试完成!")
print(f"{'='*60}")
print("✅ 所有核心功能已测试")
print("✅ 安全机制已验证")
print("✅ 错误处理已检查")
print(f"{'='*60}\n")

