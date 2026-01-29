"""
创建测试账号

使用方法：
    cd backend
    python create_teacher_account.py           # 创建教师账号
    python create_teacher_account.py student   # 创建学生账号
"""
import sqlite3
import bcrypt
import sys
from datetime import datetime


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

    # 创建 Student 记录
    email = f"{student_id}@student.local"
    cursor.execute('''
        INSERT INTO students (student_id, name, email, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, name, email, user_id, now, now))

    student_record_id = cursor.lastrowid
    print(f"创建 Student 记录成功，ID: {student_record_id}")

    conn.commit()
    conn.close()

    print(f"\n=== {role} 测试账号创建成功 ===")
    print(f"学号: {student_id}")
    print(f"姓名: {name}")
    print(f"密码: {password}")
    print(f"角色: {role}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'student':
        # 创建学生测试账号
        create_account('2000000001', '测试学生', 'student123', 'student')
    else:
        # 创建教师测试账号
        create_account('1000000001', '测试教师', 'teacher123', 'teacher')

