"""add image_url to slides

Revision ID: 002_add_image_url_to_slides
Revises: 001_initial_tables
Create Date: 2026-07-07

"""
from alembic import op
import sqlalchemy as sa

revision = '002_add_image_url_to_slides'
down_revision = '001_initial_tables'
branch_labels = None
depends_on = None

# Добавление колонки image_url в таблицу slides
def upgrade():
    op.add_column('slides', sa.Column('image_url', sa.String(500), nullable=True))

# Удаление колонки image_url
def downgrade():
    op.drop_column('slides', 'image_url')