"""create sources table and update transaction source_id

Revision ID: 25188a7e8dba
Revises: 412cf2311285
Create Date: 2025-04-05 15:15:53.370385

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '25188a7e8dba'
down_revision = '412cf2311285'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if sources table exists, if not create it
    connection = op.get_bind()
    result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sources')"))
    table_exists = result.scalar()
    
    if not table_exists:
        # Create the sources table
        op.create_table('sources',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_sources_id'), 'sources', ['id'], unique=False)
        op.create_index(op.f('ix_sources_name'), 'sources', ['name'], unique=True)
    
    # Insert a default source if it doesn't exist
    result = connection.execute(text("SELECT EXISTS (SELECT FROM sources WHERE name = 'unknown')"))
    default_source_exists = result.scalar()
    
    if not default_source_exists:
        op.execute(text("INSERT INTO sources (name, description) VALUES ('unknown', 'Default source for transactions with unknown origin')"))
    
    # Get the ID of the default source
    result = connection.execute(text("SELECT id FROM sources WHERE name = 'unknown'"))
    default_source_id = result.scalar()
    
    # Get all distinct source_id values from transactions
    result = connection.execute(text("SELECT DISTINCT source_id FROM transactions WHERE source_id != 'unknown'"))
    source_names = [row[0] for row in result if row[0] is not None]
    
    # Create a source record for each distinct source_id if it doesn't exist
    for name in source_names:
        result = connection.execute(text(f"SELECT EXISTS (SELECT FROM sources WHERE name = '{name}')"))
        source_exists = result.scalar()
        
        if not source_exists:
            op.execute(text(f"INSERT INTO sources (name) VALUES ('{name}')"))
        
        # Get the ID of the source
        result = connection.execute(text(f"SELECT id FROM sources WHERE name = '{name}'"))
        source_id = result.scalar()
        
        # Update transactions to use the new source_id (which is now a foreign key)
        op.execute(text(f"UPDATE transactions SET source_id = '{source_id}' WHERE source_id = '{name}'"))
    
    # Update all transactions with 'unknown' source_id to use the default source
    op.execute(text(f"UPDATE transactions SET source_id = '{default_source_id}' WHERE source_id = 'unknown'"))
    
    # Create a temporary column to store the integer source_id
    op.add_column('transactions', sa.Column('temp_source_id', sa.Integer(), nullable=True))
    
    # Copy the integer values to the temporary column
    op.execute(text("UPDATE transactions SET temp_source_id = source_id::integer"))
    
    # Drop the old source_id column
    op.drop_column('transactions', 'source_id')
    
    # Rename the temporary column to source_id
    op.alter_column('transactions', 'temp_source_id', new_column_name='source_id', nullable=False)
    
    # Create the foreign key constraint
    op.create_foreign_key(None, 'transactions', 'sources', ['source_id'], ['id'])
    op.create_index(op.f('ix_transactions_source_id'), 'transactions', ['source_id'], unique=False)


def downgrade() -> None:
    # Drop the foreign key constraint
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_index(op.f('ix_transactions_source_id'), table_name='transactions')
    
    # Create a temporary column to store the string source_id
    op.add_column('transactions', sa.Column('temp_source_id', sa.String(), nullable=True))
    
    # Get the source names
    connection = op.get_bind()
    result = connection.execute(text("SELECT id, name FROM sources"))
    sources = {row[0]: row[1] for row in result}
    
    # Update the temporary column with the source names
    for source_id, source_name in sources.items():
        op.execute(text(f"UPDATE transactions SET temp_source_id = '{source_name}' WHERE source_id = {source_id}"))
    
    # Drop the old source_id column
    op.drop_column('transactions', 'source_id')
    
    # Rename the temporary column to source_id
    op.alter_column('transactions', 'temp_source_id', new_column_name='source_id', nullable=False, server_default='unknown')
    
    # Note: We don't drop the sources table in downgrade since it may be used by other parts of the application
