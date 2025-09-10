"""update_existing_orders_currency_to_ron

Revision ID: 23dc8648ac2c
Revises: 004
Create Date: 2025-09-10 13:42:09.115452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23dc8648ac2c'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update any existing orders with USD currency to RON
    op.execute("UPDATE orders SET currency = 'RON' WHERE currency = 'USD' OR currency IS NULL")


def downgrade() -> None:
    # Revert RON back to USD (if needed)
    op.execute("UPDATE orders SET currency = 'USD' WHERE currency = 'RON'")
