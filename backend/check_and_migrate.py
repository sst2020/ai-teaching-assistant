"""检查数据库状态并运行迁移"""
import sqlite3
import os
import subprocess

db_path = 'teaching_assistant.db'

# 检查数据库文件是否存在
if not os.path.exists(db_path):
    print(f"数据库文件 {db_path} 不存在")
    print("需要运行 Alembic 迁移来创建数据库")
else:
    print(f"数据库文件 {db_path} 存在")
    
    # 检查表结构
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n现有表: {[t[0] for t in tables]}")
    
    # 检查 alembic_version 表
    if ('alembic_version',) in tables:
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        print(f"当前迁移版本: {version[0] if version else 'None'}")
    else:
        print("alembic_version 表不存在")
    
    conn.close()

print("\n运行 Alembic 迁移...")
os.chdir('backend')
result = subprocess.run(['alembic', 'upgrade', 'head'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("错误:", result.stderr)

