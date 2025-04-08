"""make source_id non-nullable with default

Revision ID: 412cf2311285
Revises: e902f1403a16
Create Date: 2025-04-05 15:13:11.204627

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "412cf2311285"
down_revision = "e902f1403a16"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First update any existing NULL values to 'unknown'
    op.execute(
        text("UPDATE transactions SET source_id = 'unknown' WHERE source_id IS NULL")
    )

    # Then make the column non-nullable and set the default
    op.alter_column(
        "transactions",
        "source_id",
        existing_type=sa.VARCHAR(),
        nullable=False,
        server_default="unknown",
    )


def downgrade() -> None:
    # Remove the default and make nullable again
    op.alter_column(
        "transactions",
        "source_id",
        existing_type=sa.VARCHAR(),
        nullable=True,
        server_default=None,
    )
