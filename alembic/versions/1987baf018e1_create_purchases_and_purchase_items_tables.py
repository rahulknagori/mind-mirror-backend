"""Create purchases and purchase_items tables

Revision ID: 1987baf018e1
Revises: 2b3c4d5e6f7a
Create Date: 2026-08-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1987baf018e1'
down_revision: Union[str, None] = '2b3c4d5e6f7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'purchases' not in existing_tables:
        op.create_table('purchases',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('purchase_number', sa.String(length=50), nullable=False),
            sa.Column('purchase_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('sub_total', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('discount_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
            sa.Column('tax_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('payment_method', sa.String(length=20), nullable=False),
            sa.Column('paid_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('balance_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='received'),
            sa.Column('notes', sa.String(length=500), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('purchase_number')
        )
        op.create_index(op.f('ix_purchases_id'), 'purchases', ['id'], unique=False)
        op.create_index('ix_purchases_user_id', 'purchases', ['user_id'], unique=False)
        op.create_index('ix_purchases_supplier_id', 'purchases', ['supplier_id'], unique=False)
        op.create_index('ix_purchases_purchase_number', 'purchases', ['purchase_number'], unique=False)

    if 'purchase_items' not in existing_tables:
        op.create_table('purchase_items',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('purchase_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('medicine_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('medicine_name', sa.String(length=255), nullable=False),
            sa.Column('batch_number', sa.String(length=255), nullable=True),
            sa.Column('expiry_date', sa.String(length=50), nullable=True),
            sa.Column('mrp', sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column('purchase_price', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
            sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
            sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
            sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
            sa.Column('line_total', sa.Numeric(precision=12, scale=2), nullable=False),
            sa.ForeignKeyConstraint(['purchase_id'], ['purchases.id'], ),
            sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_purchase_items_id'), 'purchase_items', ['id'], unique=False)
        op.create_index('ix_purchase_items_purchase_id', 'purchase_items', ['purchase_id'], unique=False)
        op.create_index('ix_purchase_items_medicine_id', 'purchase_items', ['medicine_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_purchase_items_medicine_id', table_name='purchase_items')
    op.drop_index('ix_purchase_items_purchase_id', table_name='purchase_items')
    op.drop_index(op.f('ix_purchase_items_id'), table_name='purchase_items')
    op.drop_table('purchase_items')

    op.drop_index('ix_purchases_purchase_number', table_name='purchases')
    op.drop_index('ix_purchases_supplier_id', table_name='purchases')
    op.drop_index('ix_purchases_user_id', table_name='purchases')
    op.drop_index(op.f('ix_purchases_id'), table_name='purchases')
    op.drop_table('purchases')
