"""add styles to slides

Revision ID: 003_add_styles_to_slides
Revises: 002_add_image_url_to_slides
Create Date: 2026-07-07

"""
from alembic import op
import sqlalchemy as sa

revision = '003_add_styles_to_slides'
down_revision = '002_add_image_url_to_slides'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем колонку styles в таблицу slides
    op.add_column('slides', sa.Column('styles', sa.JSON, nullable=True))


def downgrade():
    # Удаляем колонку styles
    op.drop_column('slides', 'styles')