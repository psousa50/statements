from sqlalchemy import create_engine, inspect, text

from src.app.db import DATABASE_URL


def reset_tables():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    tables_to_drop = ["statements", "statement_schemas"]
    existing_tables = inspector.get_table_names()

    with engine.connect() as conn:
        # Drop tables with CASCADE option
        for table in tables_to_drop:
            if table in existing_tables:
                print(f"Dropping table: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))

        # Remove statement_id column from transactions if it exists
        if "transactions" in existing_tables:
            columns = [c["name"] for c in inspector.get_columns("transactions")]
            if "statement_id" in columns:
                print("Removing statement_id column from transactions table")
                conn.execute(
                    text("ALTER TABLE transactions DROP COLUMN IF EXISTS statement_id")
                )

        conn.commit()

    print("Tables dropped successfully!")
    print(
        "Now run 'alembic upgrade head' to recreate the tables with the correct schema."
    )


if __name__ == "__main__":
    reset_tables()
