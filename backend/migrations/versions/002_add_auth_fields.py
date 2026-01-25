"""Add authentication fields to user table

Revision ID: 002
Revises: 001
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add email and password_hash columns to user table."""

    # Add email column (nullable initially for existing users)
    op.add_column('user', sa.Column('email', sa.String(length=255), nullable=True))

    # Add password_hash column (nullable initially for existing users)
    op.add_column('user', sa.Column('password_hash', sa.String(length=255), nullable=True))

    # Create unique index on email
    op.create_index('idx_user_email', 'user', ['email'], unique=True)

    # Note: For fresh installations, make columns NOT NULL immediately
    # For existing installations with users, migrate data first, then:
    # op.alter_column('user', 'email', nullable=False)
    # op.alter_column('user', 'password_hash', nullable=False)


def downgrade() -> None:
    """Remove authentication fields from user table."""

    # Drop index
    op.drop_index('idx_user_email', table_name='user')

    # Drop columns
    op.drop_column('user', 'password_hash')
    op.drop_column('user', 'email')
