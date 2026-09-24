"""add_projects_steps_resources_and_enrollment_tables

Revision ID: f3b8c9d4e5a6
Revises: e1a5b8c9d2f3
Create Date: 2026-09-22 20:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3b8c9d4e5a6'
down_revision: Union[str, Sequence[str], None] = 'e1a5b8c9d2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase 7 Projects domain."""
    # 1. Projects
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('short_description', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='Intermediate'),
        sa.Column('estimated_hours', sa.String(length=50), nullable=False, server_default='14 hours'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='published'),
        sa.Column('featured', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('prerequisites', sa.JSON(), nullable=False),
        sa.Column('learning_objectives', sa.JSON(), nullable=False),
        sa.Column('deliverables', sa.JSON(), nullable=False),
        sa.Column('technologies', sa.JSON(), nullable=False),
        sa.Column('architecture_overview', sa.Text(), nullable=True),
        sa.Column('repository_url', sa.String(length=500), nullable=True),
        sa.Column('documentation_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_slug'), 'projects', ['slug'], unique=True)
    op.create_index(op.f('ix_projects_difficulty'), 'projects', ['difficulty'], unique=False)
    op.create_index(op.f('ix_projects_status'), 'projects', ['status'], unique=False)
    op.create_index(op.f('ix_projects_featured'), 'projects', ['featured'], unique=False)

    # 2. Project Steps
    op.create_table(
        'project_steps',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_type', sa.String(length=50), nullable=False, server_default='build'),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('command', sa.String(length=500), nullable=True),
        sa.Column('expected_outcome', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'step_order', name='uq_project_step_order')
    )
    op.create_index(op.f('ix_project_steps_id'), 'project_steps', ['id'], unique=False)
    op.create_index(op.f('ix_project_steps_project_id'), 'project_steps', ['project_id'], unique=False)

    # 3. Project Resources
    op.create_table(
        'project_resources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False, server_default='documentation'),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_resources_id'), 'project_resources', ['id'], unique=False)
    op.create_index(op.f('ix_project_resources_project_id'), 'project_resources', ['project_id'], unique=False)

    # 4. Project Courses (M2M)
    op.create_table(
        'project_courses',
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('course_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'course_id')
    )

    # 5. Project Skills (M2M)
    op.create_table(
        'project_skills',
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('skill_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'skill_id')
    )

    # 6. User Project Enrollments
    op.create_table(
        'user_project_enrollments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='in_progress'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'project_id', name='uq_user_project_enrollment')
    )
    op.create_index(op.f('ix_user_project_enrollments_id'), 'user_project_enrollments', ['id'], unique=False)
    op.create_index(op.f('ix_user_project_enrollments_user_id'), 'user_project_enrollments', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_project_enrollments_project_id'), 'user_project_enrollments', ['project_id'], unique=False)
    op.create_index(op.f('ix_user_project_enrollments_status'), 'user_project_enrollments', ['status'], unique=False)

    # 7. Project Step Progress
    op.create_table(
        'project_step_progress',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('project_step_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_step_id'], ['project_steps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'project_step_id', name='uq_user_project_step_progress')
    )
    op.create_index(op.f('ix_project_step_progress_id'), 'project_step_progress', ['id'], unique=False)
    op.create_index(op.f('ix_project_step_progress_user_id'), 'project_step_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_project_step_progress_project_step_id'), 'project_step_progress', ['project_step_id'], unique=False)
    op.create_index(op.f('ix_project_step_progress_status'), 'project_step_progress', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('project_step_progress')
    op.drop_table('user_project_enrollments')
    op.drop_table('project_skills')
    op.drop_table('project_courses')
    op.drop_table('project_resources')
    op.drop_table('project_steps')
    op.drop_table('projects')
