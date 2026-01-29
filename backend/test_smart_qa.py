"""测试智能问答 API"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_triage_question():
    """测试分诊问答接口"""
    url = f"{BASE_URL}/triage/ask"
    data = {
        "question": "什么是递归？请用Python举例说明",
        "user_id": "2000000001",
        "user_name": "测试学生",
        "is_urgent": False
    }
    
    print(f"请求 URL: {url}")
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data, timeout=60)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== 智能问答成功 ===")
            print(f"问题: {result.get('question', '')[:50]}...")
            print(f"分诊决策: {result.get('decision', '')}")
            print(f"答案来源: {result.get('answer_source', '')}")
            print(f"匹配分数: {result.get('match_score', 0)}")
            print(f"置信度消息: {result.get('confidence_message', '')}")
            print(f"\n答案内容:")
            answer = result.get('answer', '')
            if answer:
                print(answer[:500] + "..." if len(answer) > 500 else answer)
            else:
                print("(无答案)")
        else:
            print(f"\n=== 请求失败 ===")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"\n请求失败: {e}")


if __name__ == '__main__':
    test_triage_question()

