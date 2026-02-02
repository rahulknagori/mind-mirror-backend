"""Create bills, bill_items, and customers tables

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-02-01 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension if not already enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Helper function to check if table exists
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create customers table if it doesn't exist
    if 'customers' not in existing_tables:
        op.create_table('customers',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('address', sa.String(length=500), nullable=True),
            sa.Column('age', sa.Integer(), nullable=True),
            sa.Column('gender', sa.String(length=10), nullable=True),
            sa.Column('credit_limit', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('outstanding_balance', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)
        op.create_index('ix_customers_user_id', 'customers', ['user_id'], unique=False)
        op.create_index('ix_customers_phone', 'customers', ['phone'], unique=False)
    
    # Create bills table if it doesn't exist
    if 'bills' not in existing_tables:
        op.create_table('bills',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('bill_number', sa.String(length=50), nullable=False),
            sa.Column('bill_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('sub_total', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('discount_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
            sa.Column('tax_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('payment_method', sa.String(length=20), nullable=False),
            sa.Column('paid_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('balance_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='completed'),
            sa.Column('notes', sa.String(length=500), nullable=True),
            sa.Column('docter_name', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('bill_number')
        )
        op.create_index(op.f('ix_bills_id'), 'bills', ['id'], unique=False)
        op.create_index('ix_bills_user_id', 'bills', ['user_id'], unique=False)
        op.create_index('ix_bills_customer_id', 'bills', ['customer_id'], unique=False)
    
    # Create bill_items table if it doesn't exist
    if 'bill_items' not in existing_tables:
        op.create_table('bill_items',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('bill_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('medicine_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('medicine_name', sa.String(length=255), nullable=False),
            sa.Column('batch_number', sa.String(length=255), nullable=True),
            sa.Column('expiry_date', sa.String(length=50), nullable=True),
            sa.Column('mrp', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('selling_price', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
            sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
            sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
            sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
            sa.Column('line_total', sa.Numeric(precision=12, scale=2), nullable=False),
            sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], ),
            sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_bill_items_id'), 'bill_items', ['id'], unique=False)
        op.create_index('ix_bill_items_bill_id', 'bill_items', ['bill_id'], unique=False)
        op.create_index('ix_bill_items_medicine_id', 'bill_items', ['medicine_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_index('ix_bill_items_medicine_id', table_name='bill_items')
    op.drop_index('ix_bill_items_bill_id', table_name='bill_items')
    op.drop_index(op.f('ix_bill_items_id'), table_name='bill_items')
    op.drop_table('bill_items')
    
    op.drop_index('ix_bills_customer_id', table_name='bills')
    op.drop_index('ix_bills_user_id', table_name='bills')
    op.drop_index(op.f('ix_bills_id'), table_name='bills')
    op.drop_table('bills')
    
    op.drop_index('ix_customers_phone', table_name='customers')
    op.drop_index('ix_customers_user_id', table_name='customers')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
