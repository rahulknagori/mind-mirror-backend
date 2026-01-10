"""convert ids to uuid

Revision ID: b1c2d3e4f5a6
Revises: a9b8c7d6e5f4
Create Date: 2025-12-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a9b8c7d6e5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension if not already enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Step 1: Create mapping table to preserve user ID relationships
    op.execute("""
        CREATE TEMP TABLE user_id_mapping AS
        SELECT id as old_id, gen_random_uuid() as new_id
        FROM users
    """)
    
    # Step 2: Drop foreign key constraint and index on medicines.user_id
    try:
        op.drop_constraint('fk_medicines_user_id', 'medicines', type_='foreignkey')
    except Exception:
        pass
    
    try:
        op.drop_index('ix_medicines_user_id', table_name='medicines')
    except Exception:
        pass
    
    # Step 3: Convert users.id from integer to UUID (using mapping)
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.add_column('users', sa.Column('id_temp', postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE users u
        SET id_temp = m.new_id
        FROM user_id_mapping m
        WHERE u.id = m.old_id
    """)
    op.drop_column('users', 'id')
    op.alter_column('users', 'id_temp', new_column_name='id', nullable=False)
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # Step 4: Convert medicines.user_id from integer to UUID (using mapping)
    op.add_column('medicines', sa.Column('user_id_temp', postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE medicines m
        SET user_id_temp = um.new_id
        FROM user_id_mapping um
        WHERE m.user_id = um.old_id
    """)
    op.drop_column('medicines', 'user_id')
    op.alter_column('medicines', 'user_id_temp', new_column_name='user_id', nullable=False)
    
    # Step 5: Convert medicines.id from integer to UUID
    op.drop_constraint('medicines_pkey', 'medicines', type_='primary')
    op.add_column('medicines', sa.Column('id_temp', postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE medicines SET id_temp = gen_random_uuid()")
    op.drop_column('medicines', 'id')
    op.alter_column('medicines', 'id_temp', new_column_name='id', nullable=False)
    op.create_primary_key('medicines_pkey', 'medicines', ['id'])
    
    # Step 6: Recreate foreign key constraint
    op.create_foreign_key('fk_medicines_user_id', 'medicines', 'users', ['user_id'], ['id'])
    
    # Step 7: Recreate indexes
    op.create_index('ix_medicines_id', 'medicines', ['id'], unique=False)
    op.create_index('ix_medicines_user_id', 'medicines', ['user_id'], unique=False)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)


def downgrade() -> None:
    # This is complex to reverse - would need to map UUIDs back to integers
    # For now, just raise an exception
    raise NotImplementedError("Cannot automatically downgrade UUID to Integer - manual migration required")

