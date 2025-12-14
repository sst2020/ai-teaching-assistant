"""add auth log model

Revision ID: 20251214_000000
Revises: 20251213_000000
Create Date: 2024-12-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251214_000000'
down_revision: Union[str, None] = '20251213_000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 auth_logs 表用于认证事件日志"""
    op.create_table(
        'auth_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('extra_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_auth_logs_id', 'auth_logs', ['id'])
    op.create_index('ix_auth_logs_user_id', 'auth_logs', ['user_id'])
    op.create_index('ix_auth_logs_email', 'auth_logs', ['email'])
    op.create_index('ix_auth_logs_event_type', 'auth_logs', ['event_type'])
    op.create_index('ix_auth_logs_status', 'auth_logs', ['status'])
    op.create_index('ix_auth_logs_created_at', 'auth_logs', ['created_at'])
    
    # 创建复合索引
    op.create_index('idx_user_event', 'auth_logs', ['user_id', 'event_type'])
    op.create_index('idx_event_time', 'auth_logs', ['event_type', 'created_at'])
    op.create_index('idx_failed_login', 'auth_logs', ['email', 'event_type', 'status', 'created_at'])


def downgrade() -> None:
    """删除 auth_logs 表"""
    # 删除复合索引
    op.drop_index('idx_failed_login', table_name='auth_logs')
    op.drop_index('idx_event_time', table_name='auth_logs')
    op.drop_index('idx_user_event', table_name='auth_logs')
    
    # 删除单列索引
    op.drop_index('ix_auth_logs_created_at', table_name='auth_logs')
    op.drop_index('ix_auth_logs_status', table_name='auth_logs')
    op.drop_index('ix_auth_logs_event_type', table_name='auth_logs')
    op.drop_index('ix_auth_logs_email', table_name='auth_logs')
    op.drop_index('ix_auth_logs_user_id', table_name='auth_logs')
    op.drop_index('ix_auth_logs_id', table_name='auth_logs')
    
    # 删除表
    op.drop_table('auth_logs')

