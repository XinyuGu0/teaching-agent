"""add source format to template

Revision ID: add_source_format_to_template
Revises: add_styles_to_template
Create Date: 2026-03-17 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_source_format_to_template'
down_revision = 'add_styles_to_template'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('templates', sa.Column('source_format', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('templates', 'source_format')
