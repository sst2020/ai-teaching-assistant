"""add knowledge_base table

Revision ID: 20251204_100000
Revises: 92ae8528c62e
Create Date: 2025-12-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251204_100000'
down_revision: Union[str, None] = '92ae8528c62e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建知识库表
    op.create_table(
        'knowledge_base_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entry_id', sa.String(36), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('difficulty_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('language', sa.String(50), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('helpful_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_knowledge_base_entries_entry_id', 'knowledge_base_entries', ['entry_id'], unique=True)
    op.create_index('ix_knowledge_base_entries_category', 'knowledge_base_entries', ['category'])
    op.create_index('ix_knowledge_base_entries_difficulty_level', 'knowledge_base_entries', ['difficulty_level'])
    op.create_index('ix_knowledge_base_entries_language', 'knowledge_base_entries', ['language'])
    op.create_index('ix_knowledge_base_entries_is_active', 'knowledge_base_entries', ['is_active'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_knowledge_base_entries_is_active', table_name='knowledge_base_entries')
    op.drop_index('ix_knowledge_base_entries_language', table_name='knowledge_base_entries')
    op.drop_index('ix_knowledge_base_entries_difficulty_level', table_name='knowledge_base_entries')
    op.drop_index('ix_knowledge_base_entries_category', table_name='knowledge_base_entries')
    op.drop_index('ix_knowledge_base_entries_entry_id', table_name='knowledge_base_entries')
    
    # 删除表
    op.drop_table('knowledge_base_entries')

