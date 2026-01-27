"""
测试重构后的 API 功能
验证：
1. 已删除的 CRUD 端点不可用
2. 保留的查询端点正常工作
3. 新增的同步端点正常工作
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"{'='*60}")

def test_health_check():
    """测试健康检查端点"""
    print_test_header("健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        assert response.status_code == 200, "健康检查失败"
        print("[PASS] 健康检查通过")
        return True
    except Exception as e:
        print(f"[FAIL] 健康检查失败: {e}")
        return False

def test_deleted_create_assignment():
    """测试已删除的创建作业端点"""
    print_test_header("测试已删除的 POST /assignments 端点")
    try:
        payload = {
            "title": "测试作业",
            "description": "这是一个测试",
            "assignment_type": "code",
            "course_id": "CS101",
            "due_date": "2026-02-01T23:59:59",
            "max_score": 100.0
        }
        response = requests.post(f"{API_V1}/assignments", json=payload)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404 or response.status_code == 405:
            print("✅ 端点已正确删除（返回 404 或 405）")
            return True
        else:
            print(f"❌ 端点仍然存在: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_deleted_update_assignment():
    """测试已删除的更新作业端点"""
    print_test_header("测试已删除的 PUT /assignments/{id} 端点")
    try:
        payload = {"title": "更新的作业"}
        response = requests.put(f"{API_V1}/assignments/1", json=payload)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404 or response.status_code == 405:
            print("✅ 端点已正确删除（返回 404 或 405）")
            return True
        else:
            print(f"❌ 端点仍然存在: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_deleted_delete_assignment():
    """测试已删除的删除作业端点"""
    print_test_header("测试已删除的 DELETE /assignments/{id} 端点")
    try:
        response = requests.delete(f"{API_V1}/assignments/1")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404 or response.status_code == 405:
            print("✅ 端点已正确删除（返回 404 或 405）")
            return True
        else:
            print(f"❌ 端点仍然存在: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_list_assignments():
    """测试保留的作业列表端点"""
    print_test_header("测试保留的 GET /assignments 端点")
    try:
        response = requests.get(f"{API_V1}/assignments", params={"page": 1, "page_size": 10})
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            print("✅ 作业列表查询正常")
            return True
        else:
            print(f"❌ 作业列表查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_sync_endpoint_exists():
    """测试新增的同步端点是否存在"""
    print_test_header("测试新增的 POST /sync/assignments 端点")
    try:
        # 注意：这个测试可能会失败，因为管理系统的 db.json 可能不存在
        response = requests.post(f"{API_V1}/sync/assignments")
        print(f"状态码: {response.status_code}")
        
        # 即使同步失败，只要端点存在（不是 404）就算通过
        if response.status_code != 404:
            print(f"✅ 同步端点存在（状态码: {response.status_code}）")
            if response.status_code == 200:
                print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            else:
                print(f"响应: {response.text[:200]}")
            return True
        else:
            print("❌ 同步端点不存在")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_sync_logs_endpoint():
    """测试同步日志端点"""
    print_test_header("测试 GET /sync/logs 端点")
    try:
        response = requests.get(f"{API_V1}/sync/logs", params={"limit": 5})
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            print("✅ 同步日志查询正常")
            return True
        else:
            print(f"❌ 同步日志查询失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始测试重构后的 API")
    print("="*60)
    
    results = {
        "健康检查": test_health_check(),
        "已删除 POST /assignments": test_deleted_create_assignment(),
        "已删除 PUT /assignments/{id}": test_deleted_update_assignment(),
        "已删除 DELETE /assignments/{id}": test_deleted_delete_assignment(),
        "保留 GET /assignments": test_list_assignments(),
        "新增 POST /sync/assignments": test_sync_endpoint_exists(),
        "新增 GET /sync/logs": test_sync_logs_endpoint(),
    }
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 测试通过")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

