"""add user profile fields

Revision ID: add_user_profile_fields
Revises: add_source_format_to_template
Create Date: 2026-03-22
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_profile_fields'
down_revision = 'add_source_format_to_template'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('teacher_gender', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('teacher_age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('school_name', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('subject_category', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('courses', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('teaching_styles', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('users', 'teaching_styles')
    op.drop_column('users', 'courses')
    op.drop_column('users', 'subject_category')
    op.drop_column('users', 'school_name')
    op.drop_column('users', 'teacher_age')
    op.drop_column('users', 'teacher_gender')
