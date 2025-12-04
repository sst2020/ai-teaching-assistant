"""add qa_log table

Revision ID: 20251204_100001
Revises: 20251204_100000
Create Date: 2025-12-04 10:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251204_100001'
down_revision: Union[str, None] = '20251204_100000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建问答日志表
    op.create_table(
        'qa_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('log_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('user_name', sa.String(100), nullable=True),
        sa.Column('session_id', sa.String(36), nullable=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('question_keywords', sa.JSON(), nullable=True),
        sa.Column('detected_category', sa.String(50), nullable=True),
        sa.Column('detected_difficulty', sa.Integer(), nullable=True),
        sa.Column('matched_entry_id', sa.String(36), nullable=True),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('match_method', sa.String(50), nullable=True),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('answer_source', sa.String(50), nullable=True),
        sa.Column('triage_result', sa.String(20), nullable=True),
        sa.Column('assigned_to', sa.String(36), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_urgent', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('is_helpful', sa.Boolean(), nullable=True),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('handled_by', sa.String(36), nullable=True),
        sa.Column('handled_at', sa.DateTime(), nullable=True),
        sa.Column('response_time_seconds', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_qa_logs_log_id', 'qa_logs', ['log_id'], unique=True)
    op.create_index('ix_qa_logs_user_id', 'qa_logs', ['user_id'])
    op.create_index('ix_qa_logs_session_id', 'qa_logs', ['session_id'])
    op.create_index('ix_qa_logs_matched_entry_id', 'qa_logs', ['matched_entry_id'])
    op.create_index('ix_qa_logs_triage_result', 'qa_logs', ['triage_result'])
    op.create_index('ix_qa_logs_status', 'qa_logs', ['status'])
    op.create_index('ix_qa_logs_is_urgent', 'qa_logs', ['is_urgent'])
    op.create_index('ix_qa_logs_created_at', 'qa_logs', ['created_at'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_qa_logs_created_at', table_name='qa_logs')
    op.drop_index('ix_qa_logs_is_urgent', table_name='qa_logs')
    op.drop_index('ix_qa_logs_status', table_name='qa_logs')
    op.drop_index('ix_qa_logs_triage_result', table_name='qa_logs')
    op.drop_index('ix_qa_logs_matched_entry_id', table_name='qa_logs')
    op.drop_index('ix_qa_logs_session_id', table_name='qa_logs')
    op.drop_index('ix_qa_logs_user_id', table_name='qa_logs')
    op.drop_index('ix_qa_logs_log_id', table_name='qa_logs')
    
    # 删除表
    op.drop_table('qa_logs')

