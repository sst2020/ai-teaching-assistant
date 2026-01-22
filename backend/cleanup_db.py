import sqlite3

conn = sqlite3.connect('teaching_assistant.db')

# 删除临时表
conn.execute('DROP TABLE IF EXISTS _alembic_tmp_users')
conn.execute('DROP TABLE IF EXISTS _alembic_tmp_auth_logs')

# 删除之前添加的 student_id 列（如果存在）
# SQLite 不支持 DROP COLUMN，需要重建表
# 但由于我们要继续迁移，先保留 student_id 列

conn.commit()
print('Cleanup completed')

# 再次检查状态
cursor = conn.execute('PRAGMA table_info(users)')
columns = [(row[1], row[2]) for row in cursor.fetchall()]
print('Users columns after cleanup:', columns)

conn.close()

