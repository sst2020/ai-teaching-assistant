import sqlite3

conn = sqlite3.connect('teaching_assistant.db')

# 获取所有表
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('Tables:', tables)

# 检查 users 表结构
if 'users' in tables:
    cursor = conn.execute('PRAGMA table_info(users)')
    columns = [(row[1], row[2]) for row in cursor.fetchall()]
    print('Users columns:', columns)
else:
    print('Users table does not exist')

# 检查 auth_logs 表结构
if 'auth_logs' in tables:
    cursor = conn.execute('PRAGMA table_info(auth_logs)')
    columns = [(row[1], row[2]) for row in cursor.fetchall()]
    print('Auth_logs columns:', columns)
else:
    print('Auth_logs table does not exist')

# 检查索引
cursor = conn.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")
indexes = [(row[0], row[1]) for row in cursor.fetchall()]
print('Indexes:', indexes)

# 检查 alembic_version
if 'alembic_version' in tables:
    cursor = conn.execute('SELECT * FROM alembic_version')
    versions = [row[0] for row in cursor.fetchall()]
    print('Alembic versions:', versions)

conn.close()

