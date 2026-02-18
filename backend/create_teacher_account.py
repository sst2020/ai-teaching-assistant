"""
创建标准测试账号

使用方法：
    cd backend
    python create_teacher_account.py           # 创建全部3个测试账号
    python create_teacher_account.py admin     # 仅创建管理员账号
    python create_teacher_account.py teacher   # 仅创建教师账号
    python create_teacher_account.py student   # 仅创建学生账号

标准测试账号：
    管理员: 0000000001 / Admin123456
    教师:   0000000002 / Teacher123456
    学生:   0000000003 / Student123456
"""
import sqlite3
import bcrypt
import sys
from datetime import datetime


# 标准测试账号配置
TEST_ACCOUNTS = {
    'admin': {
        'student_id': '0000000001',
        'name': '管理员',
        'password': 'Admin123456',
        'role': 'admin',
    },
    'teacher': {
        'student_id': '0000000002',
        'name': '测试教师',
        'password': 'Teacher123456',
        'role': 'teacher',
    },
    'student': {
        'student_id': '0000000003',
        'name': '测试学生',
        'password': 'Student123456',
        'role': 'student',
    },
}


def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_account(student_id: str, name: str, password: str, role: str):
    """创建测试账号"""
    conn = sqlite3.connect('teaching_assistant.db')
    cursor = conn.cursor()

    # 检查账号是否已存在
    cursor.execute('SELECT id FROM users WHERE student_id = ?', (student_id,))
    if cursor.fetchone():
        print(f"账号 {student_id} 已存在，跳过创建")
        conn.close()
        return

    # 哈希密码
    password_hash = hash_password(password)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 创建 User 记录
    cursor.execute('''
        INSERT INTO users (student_id, password_hash, role, is_active, name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, password_hash, role, True, name, now, now))

    user_id = cursor.lastrowid
    print(f"创建 User 记录成功，ID: {user_id}")

    # 创建 Student 记录（所有角色都需要关联 student 表）
    email = f"{student_id}@test.local"
    cursor.execute('''
        INSERT INTO students (student_id, name, email, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, name, email, user_id, now, now))

    student_record_id = cursor.lastrowid
    print(f"创建 Student 记录成功，ID: {student_record_id}")

    conn.commit()
    conn.close()

    print(f"\n=== {role} 测试账号创建成功 ===")
    print(f"账号: {student_id}")
    print(f"姓名: {name}")
    print(f"密码: {password}")
    print(f"角色: {role}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 创建指定角色的账号
        target = sys.argv[1].lower()
        if target in TEST_ACCOUNTS:
            acc = TEST_ACCOUNTS[target]
            create_account(acc['student_id'], acc['name'], acc['password'], acc['role'])
        else:
            print(f"未知角色: {target}，可选: admin, teacher, student")
    else:
        # 创建全部3个标准测试账号
        print("=== 创建全部标准测试账号 ===\n")
        for role_key, acc in TEST_ACCOUNTS.items():
            create_account(acc['student_id'], acc['name'], acc['password'], acc['role'])
            print()

