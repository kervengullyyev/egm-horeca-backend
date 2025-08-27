"""Add orders and order_items tables

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False),
        sa.Column('customer_email', sa.String(255), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=True),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=True),
        sa.Column('payment_status', sa.String(50), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('stripe_session_id', sa.String(255), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('receipt_url', sa.String(500), nullable=True),
        sa.Column('order_status', sa.String(50), nullable=True),
        sa.Column('shipping_address', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('billing_address', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('tax_id', sa.String(100), nullable=True),
        sa.Column('trade_register_no', sa.String(100), nullable=True),
        sa.Column('bank_name', sa.String(200), nullable=True),
        sa.Column('iban', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_order_number'), 'orders', ['order_number'], unique=True)
    op.create_index(op.f('ix_orders_customer_email'), 'orders', ['customer_email'], unique=False)
    op.create_index(op.f('ix_orders_payment_status'), 'orders', ['payment_status'], unique=False)
    op.create_index(op.f('ix_orders_order_status'), 'orders', ['order_status'], unique=False)

    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=False),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(200), nullable=False),
        sa.Column('product_slug', sa.String(200), nullable=False),
        sa.Column('variant_id', sa.String(), nullable=True),
        sa.Column('variant_name', sa.String(100), nullable=True),
        sa.Column('variant_value_en', sa.String(100), nullable=True),
        sa.Column('variant_value_ro', sa.String(100), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('product_image', sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_orders_order_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_payment_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_customer_email'), table_name='orders')
    op.drop_index(op.f('ix_orders_order_number'), table_name='orders')
    op.drop_table('orders')
