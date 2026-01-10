"""remove firebase_uid from users

Revision ID: a9b8c7d6e5f4
Revises: f6e5d4c3b2a1
Create Date: 2025-12-20 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9b8c7d6e5f4'
down_revision: Union[str, None] = 'f6e5d4c3b2a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the index on firebase_uid first (if it exists)
    try:
        op.drop_index('ix_users_firebase_uid', table_name='users')
    except Exception:
        pass  # Index might not exist
    
    # Remove firebase_uid column from users table
    op.drop_column('users', 'firebase_uid')


def downgrade() -> None:
    # Add firebase_uid column back (for rollback purposes)
    op.add_column('users', sa.Column('firebase_uid', sa.String(), nullable=True))
    # Recreate index if needed
    op.create_index('ix_users_firebase_uid', 'users', ['firebase_uid'], unique=True)

