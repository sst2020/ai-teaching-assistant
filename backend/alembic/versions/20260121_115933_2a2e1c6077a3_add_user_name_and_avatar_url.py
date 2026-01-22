"""add_user_name_and_avatar_url

Revision ID: 2a2e1c6077a3
Revises: 20260121_000000
Create Date: 2026-01-21 11:59:33.261748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a2e1c6077a3'
down_revision: Union[str, None] = '20260121_000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 只添加新列，跳过 SQLite 不支持的 ALTER COLUMN 操作
    op.add_column('users', sa.Column('name', sa.String(length=100), nullable=True, comment='用户姓名'))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True, comment='用户头像 URL'))


def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'name')

