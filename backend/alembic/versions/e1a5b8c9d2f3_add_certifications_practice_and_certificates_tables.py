"""add_certifications_practice_and_certificates_tables

Revision ID: e1a5b8c9d2f3
Revises: dce43e9a439d
Create Date: 2026-09-16 16:47:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a5b8c9d2f3'
down_revision: Union[str, Sequence[str], None] = 'dce43e9a439d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Certifications
    op.create_table(
        'certifications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=150), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('vendor', sa.String(length=100), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('badge_icon', sa.String(length=50), nullable=False),
        sa.Column('duration', sa.String(length=50), nullable=False),
        sa.Column('training_title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('training_certificate_name', sa.String(length=255), nullable=False),
        sa.Column('official_url', sa.String(length=500), nullable=True),
        sa.Column('is_official_certification', sa.Boolean(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('exam_domains', sa.JSON(), nullable=False),
        sa.Column('skills_gained', sa.JSON(), nullable=False),
        sa.Column('practice_questions_count', sa.Integer(), nullable=False),
        sa.Column('mock_exams_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_certifications_id'), 'certifications', ['id'], unique=False)
    op.create_index(op.f('ix_certifications_slug'), 'certifications', ['slug'], unique=True)
    op.create_index(op.f('ix_certifications_code'), 'certifications', ['code'], unique=False)
    op.create_index(op.f('ix_certifications_title'), 'certifications', ['title'], unique=False)
    op.create_index(op.f('ix_certifications_provider'), 'certifications', ['provider'], unique=False)
    op.create_index(op.f('ix_certifications_level'), 'certifications', ['level'], unique=False)
    op.create_index(op.f('ix_certifications_is_published'), 'certifications', ['is_published'], unique=False)

    # 2. Certification Trainings
    op.create_table(
        'certification_trainings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('certification_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=False),
        sa.Column('estimated_hours', sa.String(length=50), nullable=False),
        sa.Column('course_id', sa.String(length=36), nullable=True),
        sa.Column('modules', sa.JSON(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['certification_id'], ['certifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_certification_trainings_id'), 'certification_trainings', ['id'], unique=False)
    op.create_index(op.f('ix_certification_trainings_slug'), 'certification_trainings', ['slug'], unique=True)
    op.create_index(op.f('ix_certification_trainings_certification_id'), 'certification_trainings', ['certification_id'], unique=False)
    op.create_index(op.f('ix_certification_trainings_course_id'), 'certification_trainings', ['course_id'], unique=False)
    op.create_index(op.f('ix_certification_trainings_is_published'), 'certification_trainings', ['is_published'], unique=False)

    # 3. User Certification Enrollments
    op.create_table(
        'user_certification_enrollments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('certification_id', sa.String(length=36), nullable=False),
        sa.Column('training_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['certification_id'], ['certifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['training_id'], ['certification_trainings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'training_id', name='uq_user_training_enrollment'),
    )
    op.create_index(op.f('ix_user_certification_enrollments_id'), 'user_certification_enrollments', ['id'], unique=False)
    op.create_index(op.f('ix_user_certification_enrollments_user_id'), 'user_certification_enrollments', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_certification_enrollments_certification_id'), 'user_certification_enrollments', ['certification_id'], unique=False)
    op.create_index(op.f('ix_user_certification_enrollments_training_id'), 'user_certification_enrollments', ['training_id'], unique=False)
    op.create_index(op.f('ix_user_certification_enrollments_status'), 'user_certification_enrollments', ['status'], unique=False)

    # 4. Practice Questions
    op.create_table(
        'practice_questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('certification_id', sa.String(length=36), nullable=False),
        sa.Column('training_id', sa.String(length=36), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('options', sa.JSON(), nullable=False),
        sa.Column('correct_option', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(length=150), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['certification_id'], ['certifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['training_id'], ['certification_trainings.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_practice_questions_id'), 'practice_questions', ['id'], unique=False)
    op.create_index(op.f('ix_practice_questions_certification_id'), 'practice_questions', ['certification_id'], unique=False)
    op.create_index(op.f('ix_practice_questions_training_id'), 'practice_questions', ['training_id'], unique=False)
    op.create_index(op.f('ix_practice_questions_domain'), 'practice_questions', ['domain'], unique=False)
    op.create_index(op.f('ix_practice_questions_is_published'), 'practice_questions', ['is_published'], unique=False)

    # 5. Practice Attempts
    op.create_table(
        'practice_attempts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('certification_id', sa.String(length=36), nullable=False),
        sa.Column('training_id', sa.String(length=36), nullable=True),
        sa.Column('attempt_type', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('percentage', sa.Float(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('passing_percentage', sa.Float(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('correct_answers', sa.Integer(), nullable=False),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['certification_id'], ['certifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['training_id'], ['certification_trainings.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_practice_attempts_id'), 'practice_attempts', ['id'], unique=False)
    op.create_index(op.f('ix_practice_attempts_user_id'), 'practice_attempts', ['user_id'], unique=False)
    op.create_index(op.f('ix_practice_attempts_certification_id'), 'practice_attempts', ['certification_id'], unique=False)
    op.create_index(op.f('ix_practice_attempts_training_id'), 'practice_attempts', ['training_id'], unique=False)
    op.create_index(op.f('ix_practice_attempts_attempt_type'), 'practice_attempts', ['attempt_type'], unique=False)
    op.create_index(op.f('ix_practice_attempts_passed'), 'practice_attempts', ['passed'], unique=False)

    # 6. Practice Attempt Answers
    op.create_table(
        'practice_attempt_answers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('attempt_id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('selected_answer', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('points_earned', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['attempt_id'], ['practice_attempts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['practice_questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_question_answer'),
    )
    op.create_index(op.f('ix_practice_attempt_answers_id'), 'practice_attempt_answers', ['id'], unique=False)
    op.create_index(op.f('ix_practice_attempt_answers_attempt_id'), 'practice_attempt_answers', ['attempt_id'], unique=False)
    op.create_index(op.f('ix_practice_attempt_answers_question_id'), 'practice_attempt_answers', ['question_id'], unique=False)

    # 7. Certificates
    op.create_table(
        'certificates',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('certification_id', sa.String(length=36), nullable=True),
        sa.Column('training_id', sa.String(length=36), nullable=False),
        sa.Column('certificate_number', sa.String(length=100), nullable=False),
        sa.Column('verification_code', sa.String(length=100), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('completion_percentage', sa.Float(), nullable=False),
        sa.Column('recipient_name_snapshot', sa.String(length=200), nullable=False),
        sa.Column('training_title_snapshot', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['certification_id'], ['certifications.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['training_id'], ['certification_trainings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'training_id', name='uq_user_training_certificate'),
    )
    op.create_index(op.f('ix_certificates_id'), 'certificates', ['id'], unique=False)
    op.create_index(op.f('ix_certificates_user_id'), 'certificates', ['user_id'], unique=False)
    op.create_index(op.f('ix_certificates_certification_id'), 'certificates', ['certification_id'], unique=False)
    op.create_index(op.f('ix_certificates_training_id'), 'certificates', ['training_id'], unique=False)
    op.create_index(op.f('ix_certificates_certificate_number'), 'certificates', ['certificate_number'], unique=True)
    op.create_index(op.f('ix_certificates_verification_code'), 'certificates', ['verification_code'], unique=True)
    op.create_index(op.f('ix_certificates_status'), 'certificates', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('certificates')
    op.drop_table('practice_attempt_answers')
    op.drop_table('practice_attempts')
    op.drop_table('practice_questions')
    op.drop_table('user_certification_enrollments')
    op.drop_table('certification_trainings')
    op.drop_table('certifications')
