"""email to student_id migration

Revision ID: 20260121_000000
Revises: 1691bb2950d3
Create Date: 2026-01-21 00:00:00.000000

将用户认证系统从邮箱认证改为学号认证：
- users 表：删除 email 列，添加 student_id 列
- auth_logs 表：删除 email 列，添加 student_id 列

注意：此迁移使用直接 SQL 语句来处理 SQLite 的限制。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260121_000000'
down_revision: Union[str, None] = '1691bb2950d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 获取数据库连接
    conn = op.get_bind()

    # 检查 student_id 列是否已存在（处理部分迁移的情况）
    result = conn.execute(sa.text("PRAGMA table_info(users)"))
    users_columns = [row[1] for row in result.fetchall()]
    student_id_exists = 'student_id' in users_columns
    email_exists = 'email' in users_columns

    # ============ 处理 users 表 ============
    if not student_id_exists:
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN student_id VARCHAR(10)"))

    # 为现有用户生成临时学号
    conn.execute(sa.text("""
        UPDATE users
        SET student_id = printf('%010d', 2026000000 + id)
        WHERE student_id IS NULL OR student_id = ''
    """))

    if email_exists:
        # 删除 email 索引
        conn.execute(sa.text("DROP INDEX IF EXISTS ix_users_email"))

        # 重建 users 表（SQLite 不支持 DROP COLUMN）
        conn.execute(sa.text("""
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY,
                student_id VARCHAR(10) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'student' NOT NULL,
                is_active BOOLEAN DEFAULT 1 NOT NULL,
                last_login DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(sa.text("""
            INSERT INTO users_new (id, student_id, password_hash, role, is_active, last_login, created_at, updated_at)
            SELECT id, student_id, password_hash, role, is_active, last_login, created_at, updated_at
            FROM users
        """))

        conn.execute(sa.text("DROP TABLE users"))
        conn.execute(sa.text("ALTER TABLE users_new RENAME TO users"))

        # 创建索引
        conn.execute(sa.text("CREATE UNIQUE INDEX ix_users_student_id ON users (student_id)"))
        conn.execute(sa.text("CREATE INDEX ix_users_id ON users (id)"))

    # ============ 处理 auth_logs 表 ============
    result = conn.execute(sa.text("PRAGMA table_info(auth_logs)"))
    auth_logs_columns = [row[1] for row in result.fetchall()]
    auth_student_id_exists = 'student_id' in auth_logs_columns
    auth_email_exists = 'email' in auth_logs_columns

    if not auth_student_id_exists:
        conn.execute(sa.text("ALTER TABLE auth_logs ADD COLUMN student_id VARCHAR(10)"))

    # 为现有日志设置默认学号
    conn.execute(sa.text("""
        UPDATE auth_logs
        SET student_id = '0000000000'
        WHERE student_id IS NULL OR student_id = ''
    """))

    if auth_email_exists:
        # 删除旧索引
        conn.execute(sa.text("DROP INDEX IF EXISTS ix_auth_logs_email"))
        conn.execute(sa.text("DROP INDEX IF EXISTS idx_failed_login"))

        # 重建 auth_logs 表
        conn.execute(sa.text("""
            CREATE TABLE auth_logs_new (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                student_id VARCHAR(10) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                ip_address VARCHAR(45),
                user_agent VARCHAR(500),
                failure_reason VARCHAR(255),
                extra_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))

        conn.execute(sa.text("""
            INSERT INTO auth_logs_new (id, user_id, student_id, event_type, status, ip_address, user_agent, failure_reason, extra_data, created_at)
            SELECT id, user_id, student_id, event_type, status, ip_address, user_agent, failure_reason, extra_data, created_at
            FROM auth_logs
        """))

        conn.execute(sa.text("DROP TABLE auth_logs"))
        conn.execute(sa.text("ALTER TABLE auth_logs_new RENAME TO auth_logs"))

        # 创建索引
        conn.execute(sa.text("CREATE INDEX ix_auth_logs_id ON auth_logs (id)"))
        conn.execute(sa.text("CREATE INDEX ix_auth_logs_user_id ON auth_logs (user_id)"))
        conn.execute(sa.text("CREATE INDEX ix_auth_logs_student_id ON auth_logs (student_id)"))
        conn.execute(sa.text("CREATE INDEX ix_auth_logs_event_type ON auth_logs (event_type)"))
        conn.execute(sa.text("CREATE INDEX ix_auth_logs_status ON auth_logs (status)"))
        conn.execute(sa.text("CREATE INDEX ix_auth_logs_created_at ON auth_logs (created_at)"))
        conn.execute(sa.text("CREATE INDEX idx_user_event ON auth_logs (user_id, event_type)"))
        conn.execute(sa.text("CREATE INDEX idx_event_time ON auth_logs (event_type, created_at)"))
        conn.execute(sa.text("CREATE INDEX idx_failed_login ON auth_logs (student_id, event_type, status, created_at)"))


def downgrade() -> None:
    # 获取数据库连接
    conn = op.get_bind()

    # ============ 恢复 users 表 ============
    # 删除索引
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_users_student_id"))

    # 重建 users 表
    conn.execute(sa.text("""
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'student' NOT NULL,
            is_active BOOLEAN DEFAULT 1 NOT NULL,
            last_login DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(sa.text("""
        INSERT INTO users_new (id, email, password_hash, role, is_active, last_login, created_at, updated_at)
        SELECT id, student_id || '@temp.edu', password_hash, role, is_active, last_login, created_at, updated_at
        FROM users
    """))

    conn.execute(sa.text("DROP TABLE users"))
    conn.execute(sa.text("ALTER TABLE users_new RENAME TO users"))

    # 创建索引
    conn.execute(sa.text("CREATE UNIQUE INDEX ix_users_email ON users (email)"))
    conn.execute(sa.text("CREATE INDEX ix_users_id ON users (id)"))

    # ============ 恢复 auth_logs 表 ============
    # 删除索引
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_auth_logs_student_id"))
    conn.execute(sa.text("DROP INDEX IF EXISTS idx_failed_login"))

    # 重建 auth_logs 表
    conn.execute(sa.text("""
        CREATE TABLE auth_logs_new (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            email VARCHAR(255) NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL,
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            failure_reason VARCHAR(255),
            extra_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """))

    conn.execute(sa.text("""
        INSERT INTO auth_logs_new (id, user_id, email, event_type, status, ip_address, user_agent, failure_reason, extra_data, created_at)
        SELECT id, user_id, student_id || '@temp.edu', event_type, status, ip_address, user_agent, failure_reason, extra_data, created_at
        FROM auth_logs
    """))

    conn.execute(sa.text("DROP TABLE auth_logs"))
    conn.execute(sa.text("ALTER TABLE auth_logs_new RENAME TO auth_logs"))

    # 创建索引
    conn.execute(sa.text("CREATE INDEX ix_auth_logs_id ON auth_logs (id)"))
    conn.execute(sa.text("CREATE INDEX ix_auth_logs_user_id ON auth_logs (user_id)"))
    conn.execute(sa.text("CREATE INDEX ix_auth_logs_email ON auth_logs (email)"))
    conn.execute(sa.text("CREATE INDEX ix_auth_logs_event_type ON auth_logs (event_type)"))
    conn.execute(sa.text("CREATE INDEX ix_auth_logs_status ON auth_logs (status)"))
    conn.execute(sa.text("CREATE INDEX ix_auth_logs_created_at ON auth_logs (created_at)"))
    conn.execute(sa.text("CREATE INDEX idx_user_event ON auth_logs (user_id, event_type)"))
    conn.execute(sa.text("CREATE INDEX idx_event_time ON auth_logs (event_type, created_at)"))
    conn.execute(sa.text("CREATE INDEX idx_failed_login ON auth_logs (email, event_type, status, created_at)"))
