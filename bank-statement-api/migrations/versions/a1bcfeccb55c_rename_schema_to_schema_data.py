"""rename_schema_to_schema_data

Revision ID: a1bcfeccb55c
Revises: 85a74cd6fd3a
Create Date: 2025-04-14 16:58:08.611795

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "a1bcfeccb55c"
down_revision = "85a74cd6fd3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a temporary table with the new schema
    op.execute(
        """
        ALTER TABLE statement_schemas 
        RENAME COLUMN schema TO schema_data
        """
    )


def downgrade() -> None:
    # Revert the column rename
    op.execute(
        """
        ALTER TABLE statement_schemas 
        RENAME COLUMN schema_data TO schema
        """
    )
