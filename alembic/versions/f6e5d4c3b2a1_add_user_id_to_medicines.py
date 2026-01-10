"""add user_id to medicines

Revision ID: f6e5d4c3b2a1
Revises: a1b2c3d4e5f6
Create Date: 2025-12-20 15:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6e5d4c3b2a1'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id column to medicines table
    op.add_column('medicines', sa.Column('user_id', sa.Integer(), nullable=True))
    # Create foreign key constraint
    op.create_foreign_key('fk_medicines_user_id', 'medicines', 'users', ['user_id'], ['id'])
    # Create index for better query performance
    op.create_index(op.f('ix_medicines_user_id'), 'medicines', ['user_id'], unique=False)
    # Make it non-nullable after adding the column (if you have existing data, you'll need to handle that)
    # For now, keeping it nullable=True to avoid errors with existing data


def downgrade() -> None:
    # Remove index
    op.drop_index(op.f('ix_medicines_user_id'), table_name='medicines')
    # Remove foreign key constraint
    op.drop_constraint('fk_medicines_user_id', 'medicines', type_='foreignkey')
    # Remove column
    op.drop_column('medicines', 'user_id')

