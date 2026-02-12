# 数据库迁移指南：从 SQLite 到 MySQL

本文档介绍了如何将 AI Teaching Assistant 应用从 SQLite 数据库迁移到 MySQL 数据库。

## 1. 准备工作

### 安装 MySQL 驱动
确保已安装 MySQL 相关依赖：
```bash
pip install aiomysql PyMySQL
```

### 配置 MySQL 数据库
在 `backend/.env` 文件中更新数据库配置：
```env
# 从
DATABASE_URL=sqlite:///./teaching_assistant.db

# 改为
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name
```

## 2. 模型兼容性调整

### 字符串字段长度
MySQL 需要为 VARCHAR 字段指定最大长度，已在模型中更新：
- `String(10)` for student_id
- `String(255)` for password_hash
- `String(50)` for role
- `String(100)` for name
- `String(500)` for avatar_url

### 时区处理
确保 DateTime 字段正确处理时区信息：
```python
DateTime(timezone=True)
```

### 存储引擎
为 MySQL 指定 InnoDB 存储引擎以支持事务和外键约束：
```python
__table_args__ = (
    # ... indexes ...
    {'mysql_engine': 'InnoDB'}
)
```

## 3. 迁移步骤

### 3.1 备份当前数据
在进行任何更改之前，请备份当前的 SQLite 数据库：
```bash
cp teaching_assistant.db backup_teaching_assistant.db
```

### 3.2 导出现有数据
使用以下脚本导出现有数据到 JSON 文件：
```python
# export_data.py
import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from models import User, Student, Assignment, Submission, GradingResult, Question, Answer

async def export_data():
    # 使用当前 SQLite 数据库
    sqlite_engine = create_async_engine("sqlite+aiosqlite:///teaching_assistant.db")
    
    async with sqlite_engine.begin() as conn:
        # 导出数据到 JSON
        # ... 实现导出逻辑 ...
        
    await sqlite_engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_data())
```

### 3.3 更新数据库配置
更新 `.env` 文件中的 `DATABASE_URL` 设置。

### 3.4 创建 MySQL 表结构
运行 Alembic 迁移创建表结构：
```bash
cd backend
python -m alembic upgrade head
```

### 3.5 导入数据
使用以下脚本将数据导入 MySQL：
```python
# import_data.py
import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from models import User, Student, Assignment, Submission, GradingResult, Question, Answer

async def import_data():
    # 使用新的 MySQL 数据库
    mysql_engine = create_async_engine("mysql+aiomysql://...")
    
    async with mysql_engine.begin() as conn:
        # 从 JSON 导入数据
        # ... 实现导入逻辑 ...
        
    await mysql_engine.dispose()

if __name__ == "__main__":
    asyncio.run(import_data())
```

## 4. 验证迁移

### 4.1 检查表结构
验证所有表和索引是否正确创建：
```bash
# 连接到 MySQL 并检查表
mysql -u username -p
SHOW TABLES;
DESCRIBE users;
```

### 4.2 验证数据完整性
检查关键数据是否正确迁移：
- 用户账户
- 学生信息
- 作业和提交
- 评分结果
- 问答记录

### 4.3 测试应用程序
启动应用程序并执行以下操作：
- 用户登录
- 提交作业
- 查看成绩
- 问答功能

## 5. 常见问题及解决方案

### 5.1 字符编码问题
如果遇到字符编码问题，在 MySQL 中设置正确的字符集：
```sql
ALTER DATABASE database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5.2 外键约束问题
如果遇到外键约束问题，检查数据导入顺序，确保父表数据先于子表数据导入。

### 5.3 时区问题
确保应用程序和数据库服务器使用相同的时区设置。

## 6. 性能优化建议

### 6.1 索引优化
根据查询模式添加适当的索引：
```sql
CREATE INDEX idx_questions_status ON questions(status);
CREATE INDEX idx_submissions_student_assignment ON submissions(student_id, assignment_id);
```

### 6.2 连接池配置
在生产环境中调整连接池大小：
```python
async_engine = create_async_engine(
    get_database_url(async_mode=True),
    echo=settings.DATABASE_ECHO,
    pool_size=20,  # 根据负载调整
    max_overflow=30,
    pool_pre_ping=True,
)
```

## 7. 回滚计划

如果迁移过程中出现问题，可以执行以下回滚步骤：

1. 停止应用程序
2. 删除 MySQL 数据库
3. 恢复 SQLite 配置
4. 重启应用程序

## 8. 监控和维护

### 8.1 监控查询性能
定期检查慢查询日志并优化慢查询。

### 8.2 数据库备份
设置定期备份策略：
```bash
# 每日备份
mysqldump -u username -p database_name > backup_$(date +%F).sql
```

### 8.3 连接监控
监控数据库连接数，确保不会超出 MySQL 的最大连接限制。