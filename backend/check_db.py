import sqlite3
import sys

conn = sqlite3.connect('teaching_assistant.db')

# 检查特定学号
if len(sys.argv) > 1:
    student_id = sys.argv[1]
    print(f"=== 查询学号: {student_id} ===")
    cursor = conn.execute('SELECT id, student_id, role, is_active, name FROM users WHERE student_id = ?', (student_id,))
    user = cursor.fetchone()
    if user:
        print(f"找到用户: ID={user[0]}, 学号={user[1]}, 角色={user[2]}, 激活={user[3]}, 姓名={user[4]}")
    else:
        print(f"未找到学号为 {student_id} 的用户")
else:
    # 检查 users 表数据
    print("=== Users 表数据 ===")
    cursor = conn.execute('SELECT id, student_id, role, is_active, name FROM users LIMIT 10')
    users = cursor.fetchall()
    if users:
        for row in users:
            print(f"ID: {row[0]}, 学号: {row[1]}, 角色: {row[2]}, 激活: {row[3]}, 姓名: {row[4]}")
    else:
        print("没有用户数据")

    # 检查 students 表数据
    print("\n=== Students 表数据 ===")
    cursor = conn.execute('SELECT id, student_id, name, user_id FROM students LIMIT 10')
    students = cursor.fetchall()
    if students:
        for row in students:
            print(f"ID: {row[0]}, 学号: {row[1]}, 姓名: {row[2]}, User ID: {row[3]}")
    else:
        print("没有学生数据")

conn.close()

