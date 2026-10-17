"""create suppliers table

Backfills the suppliers table, which was never created by an earlier
migration but is referenced by purchases.supplier_id. Guarded so it is
a no-op on databases that already have the table.

Revision ID: 2b3c4d5e6f7a
Revises: c1d2e3f4a5b6
Create Date: 2025-12-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2b3c4d5e6f7a'
down_revision: Union[str, None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if 'suppliers' in inspector.get_table_names():
        return

    op.create_table('suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_name', sa.String(length=255), nullable=False),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('gst_number', sa.String(length=50), nullable=True),
        sa.Column('drug_license_number', sa.String(length=100), nullable=True),
        sa.Column('drug_license_expiry', sa.Date(), nullable=True),
        sa.Column('credit_days', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('opening_balance', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('gst_number')
    )
    op.create_index('ix_suppliers_user_id', 'suppliers', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_suppliers_user_id', table_name='suppliers')
    op.drop_table('suppliers')
