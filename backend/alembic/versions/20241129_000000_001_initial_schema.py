"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-11-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create students table
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('enrollment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('course_id', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('student_id')
    )
    op.create_index('ix_students_student_id', 'students', ['student_id'], unique=False)
    op.create_index('ix_students_course_id', 'students', ['course_id'], unique=False)
    op.create_index('ix_students_course_id_student_id', 'students', ['course_id', 'student_id'], unique=False)

    # Create rubrics table
    op.create_table(
        'rubrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rubric_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('criteria', sa.JSON(), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rubric_id')
    )
    op.create_index('ix_rubrics_rubric_id', 'rubrics', ['rubric_id'], unique=False)

    # Create assignments table
    op.create_table(
        'assignments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('assignment_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assignment_type', sa.Enum('CODE', 'ESSAY', 'QUIZ', name='assignmenttype'), nullable=False),
        sa.Column('course_id', sa.String(length=50), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('rubric_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['rubric_id'], ['rubrics.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('assignment_id')
    )
    op.create_index('ix_assignments_assignment_id', 'assignments', ['assignment_id'], unique=False)
    op.create_index('ix_assignments_course_id', 'assignments', ['course_id'], unique=False)
    op.create_index('ix_assignments_course_id_due_date', 'assignments', ['course_id', 'due_date'], unique=False)

    # Create submissions table
    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('submission_id', sa.String(length=50), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'GRADED', 'FLAGGED', name='submissionstatus'), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('submission_id')
    )
    op.create_index('ix_submissions_submission_id', 'submissions', ['submission_id'], unique=False)
    op.create_index('ix_submissions_student_id', 'submissions', ['student_id'], unique=False)
    op.create_index('ix_submissions_assignment_id', 'submissions', ['assignment_id'], unique=False)
    op.create_index('ix_submissions_student_assignment', 'submissions', ['student_id', 'assignment_id'], unique=False)
    op.create_index('ix_submissions_status_submitted_at', 'submissions', ['status', 'submitted_at'], unique=False)

    # Create grading_results table
    op.create_table(
        'grading_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('feedback', sa.JSON(), nullable=True),
        sa.Column('graded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('graded_by', sa.Enum('AI', 'TEACHER', name='gradedby'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('submission_id')
    )
    op.create_index('ix_grading_results_submission_id', 'grading_results', ['submission_id'], unique=False)

    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_id', sa.String(length=50), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.String(length=50), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('category', sa.Enum('CONCEPT', 'ASSIGNMENT', 'TECHNICAL', 'ADMINISTRATIVE', 'OTHER', name='questioncategory'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ANSWERED', 'ESCALATED', 'CLOSED', name='questionstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_id')
    )
    op.create_index('ix_questions_question_id', 'questions', ['question_id'], unique=False)
    op.create_index('ix_questions_student_id', 'questions', ['student_id'], unique=False)
    op.create_index('ix_questions_course_id', 'questions', ['course_id'], unique=False)
    op.create_index('ix_questions_course_status', 'questions', ['course_id', 'status'], unique=False)
    op.create_index('ix_questions_student_created', 'questions', ['student_id', 'created_at'], unique=False)

    # Create answers table
    op.create_table(
        'answers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('ai_answer', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('needs_teacher_review', sa.Boolean(), nullable=False),
        sa.Column('teacher_answer', sa.Text(), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_id')
    )
    op.create_index('ix_answers_question_id', 'answers', ['question_id'], unique=False)

    # Create plagiarism_checks table
    op.create_table(
        'plagiarism_checks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('is_flagged', sa.Boolean(), nullable=False),
        sa.Column('matches', sa.JSON(), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('submission_id')
    )
    op.create_index('ix_plagiarism_checks_submission_id', 'plagiarism_checks', ['submission_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('plagiarism_checks')
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('grading_results')
    op.drop_table('submissions')
    op.drop_table('assignments')
    op.drop_table('rubrics')
    op.drop_table('students')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS questionstatus")
    op.execute("DROP TYPE IF EXISTS questioncategory")
    op.execute("DROP TYPE IF EXISTS gradedby")
    op.execute("DROP TYPE IF EXISTS submissionstatus")
    op.execute("DROP TYPE IF EXISTS assignmenttype")

