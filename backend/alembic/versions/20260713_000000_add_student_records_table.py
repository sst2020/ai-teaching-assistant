"""add student_records table

Revision ID: 20260713_student_records
Revises: 20260212_mysql_compat
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260713_student_records'
down_revision: Union[str, None] = '20260212_mysql_compat'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'student_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False, comment='学生姓名'),
        sa.Column('student_id', sa.String(50), nullable=False, comment='学号'),
        sa.Column('password_hash', sa.String(255), nullable=False, comment='bcrypt 哈希后的密码'),
        sa.Column('assignment_number', sa.String(50), nullable=False, comment='作业编号'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id'),
    )
    op.create_index('ix_student_records_student_id', 'student_records', ['student_id'])
    op.create_index('ix_student_records_assignment_number', 'student_records', ['assignment_number'])


def downgrade() -> None:
    op.drop_index('ix_student_records_assignment_number', table_name='student_records')
    op.drop_index('ix_student_records_student_id', table_name='student_records')
    op.drop_table('student_records')
