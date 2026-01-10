"""add hashed_password to users

Revision ID: a1b2c3d4e5f6
Revises: 75648c0386f8
Create Date: 2025-12-20 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '75648c0386f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add hashed_password column to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove hashed_password column from users table
    op.drop_column('users', 'hashed_password')

