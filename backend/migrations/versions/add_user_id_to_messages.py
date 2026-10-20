"""add user_id to messages

Revision ID: add_user_id_to_messages
Revises: add_template_info_to_template
Create Date: 2026-04-20 22:57:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_id_to_messages'
down_revision = 'add_template_info_to_template'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('messages', sa.Column('user_id', sa.String(36), nullable=True))
    op.create_foreign_key('fk_messages_user_id', 'messages', 'users', ['user_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_messages_user_id', 'messages', type_='foreignkey')
    op.drop_column('messages', 'user_id')
