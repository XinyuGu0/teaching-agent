"""add template_info to template

Revision ID: add_template_info_to_template
Revises: add_styles_to_template
Create Date: 2026-03-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_template_info_to_template'
down_revision = 'add_styles_to_template'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('templates', sa.Column('template_info', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('templates', 'template_info')
