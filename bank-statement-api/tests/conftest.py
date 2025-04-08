import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.db import Base
from src.app.main import App
from src.app.models import Category, Source
from src.app.schemas import TransactionCreate


def create_test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    return db


db_session = create_test_db()


def create_app(
        db_session=db_session,
        categories_repository=MagicMock(),
        sources_repository=MagicMock(), 
        transactions_repository=MagicMock(), 
        categorizer=MagicMock()
    ):
    return App(
        db_session=db_session,
        categories_repository=categories_repository,
        sources_repository=sources_repository,
        transactions_repository=transactions_repository,
        categorizer=categorizer
    )

def random_transaction(source_id: int) -> TransactionCreate:
    return TransactionCreate(
        date=date.today(),
        description=f"TestTransaction_{uuid.uuid4().hex[:8]}",
        amount=Decimal(f"{uuid.uuid4().int % 1000}.{uuid.uuid4().int % 100:02d}"),
        currency="EUR",
        source_id=source_id
    )

def random_category():
    return Category(category_name=f"TestCategory_{uuid.uuid4().hex[:8]}")


def random_source():
    return Source(
        name=f"TestSource_{uuid.uuid4().hex[:8]}",
        description=f"Description for test source {uuid.uuid4().hex[:8]}"
    )
