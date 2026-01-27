# -*- coding: utf-8 -*-
"""
API Refactoring Test Script
Tests the refactored API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def test_health():
    print("\n[TEST] Health Check")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("[PASS] Health check OK")
        return True
    print("[FAIL] Health check failed")
    return False

def test_create_deleted():
    print("\n[TEST] POST /assignments (should be deleted)")
    payload = {"title": "Test", "assignment_type": "code", "course_id": "CS101", "due_date": "2026-02-01T23:59:59", "max_score": 100}
    r = requests.post(f"{API_V1}/assignments", json=payload)
    print(f"Status: {r.status_code}")
    if r.status_code in [404, 405]:
        print("[PASS] Endpoint correctly deleted")
        return True
    print(f"[FAIL] Endpoint still exists: {r.status_code}")
    return False

def test_update_deleted():
    print("\n[TEST] PUT /assignments/1 (should be deleted)")
    r = requests.put(f"{API_V1}/assignments/1", json={"title": "Updated"})
    print(f"Status: {r.status_code}")
    if r.status_code in [404, 405]:
        print("[PASS] Endpoint correctly deleted")
        return True
    print(f"[FAIL] Endpoint still exists: {r.status_code}")
    return False

def test_delete_deleted():
    print("\n[TEST] DELETE /assignments/1 (should be deleted)")
    r = requests.delete(f"{API_V1}/assignments/1")
    print(f"Status: {r.status_code}")
    if r.status_code in [404, 405]:
        print("[PASS] Endpoint correctly deleted")
        return True
    print(f"[FAIL] Endpoint still exists: {r.status_code}")
    return False

def test_list_assignments():
    print("\n[TEST] GET /assignments (should work)")
    r = requests.get(f"{API_V1}/assignments", params={"page": 1, "page_size": 10})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("[PASS] List assignments OK")
        return True
    print(f"[FAIL] List assignments failed: {r.status_code}")
    return False

def test_sync_endpoint():
    print("\n[TEST] POST /sync/assignments (new endpoint)")
    r = requests.post(f"{API_V1}/sync/assignments")
    print(f"Status: {r.status_code}")
    if r.status_code != 404:
        print(f"[PASS] Sync endpoint exists (status: {r.status_code})")
        return True
    print("[FAIL] Sync endpoint not found")
    return False

def test_sync_logs():
    print("\n[TEST] GET /sync/logs (new endpoint)")
    r = requests.get(f"{API_V1}/sync/logs", params={"limit": 5})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("[PASS] Sync logs OK")
        return True
    print(f"[FAIL] Sync logs failed: {r.status_code}")
    return False

def main():
    print("="*60)
    print("API Refactoring Test Suite")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("DELETE POST /assignments", test_create_deleted),
        ("DELETE PUT /assignments/{id}", test_update_deleted),
        ("DELETE DELETE /assignments/{id}", test_delete_deleted),
        ("KEEP GET /assignments", test_list_assignments),
        ("NEW POST /sync/assignments", test_sync_endpoint),
        ("NEW GET /sync/logs", test_sync_logs),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

