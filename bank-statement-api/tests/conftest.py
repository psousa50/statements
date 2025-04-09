import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.db import Base
from src.app.main import App
from src.app.models import Category, Source, Transaction
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
    categorizer=MagicMock(),
):
    return App(
        db_session=db_session,
        categories_repository=categories_repository,
        sources_repository=sources_repository,
        transactions_repository=transactions_repository,
        categorizer=categorizer,
    )


def random_transaction_create(source_id: int) -> TransactionCreate:
    return TransactionCreate(
        date=date.today(),
        description=f"TestTransaction_{uuid.uuid4().hex[:8]}",
        amount=Decimal(f"{uuid.uuid4().int % 1000}.{uuid.uuid4().int % 100:02d}"),
        currency="EUR",
        source_id=source_id,
    )

def random_transaction(
    source_id: int, 
    description: str = f"TestTransaction_{uuid.uuid4().hex[:8]}",
    category_id: int = 1,
    ) -> Transaction:
    return Transaction(
        id=uuid.uuid4(),
        date=date.today(),
        description=description,
        amount=Decimal(f"{uuid.uuid4().int % 1000}.{uuid.uuid4().int % 100:02d}"),
        currency="EUR",
        source_id=source_id,
        category_id=category_id,
        normalized_description=description.lower(),
        categorization_status="categorized"
    )

def random_category():
    return Category(category_name=f"TestCategory_{uuid.uuid4().hex[:8]}")


def random_source():
    return Source(
        name=f"TestSource_{uuid.uuid4().hex[:8]}",
        description=f"Description for test source {uuid.uuid4().hex[:8]}",
    )

def create_category(id: int, category_name: str, subcategories: list[SimpleNamespace] = []):
    return SimpleNamespace(
        id=id,
        category_name=category_name,
        subcategories=subcategories,
    )

def create_category_tree(
    id: int,
    category_name: str,
    subcategory_id_1: int,
    subcategory_name_1: str,
    subcategory_id_2: int,
    subcategory_name_2: str,
) -> list[SimpleNamespace]:
    # Create subcategories first
    subcategory1 = SimpleNamespace(
        id=subcategory_id_1, 
        category_name=subcategory_name_1, 
        parent_category_id=id,
        subcategories=None
    )
    
    subcategory2 = SimpleNamespace(
        id=subcategory_id_2, 
        category_name=subcategory_name_2, 
        parent_category_id=id,
        subcategories=None
    )
    
    # Create root category with subcategories
    root = SimpleNamespace(
        id=id,
        category_name=category_name,
        parent_category_id=None,
        subcategories=[subcategory1, subcategory2]
    )
    
    return [root, subcategory1, subcategory2]

def create_sample_categories_repository():
    restaurant = SimpleNamespace(
        id=2, category_name="Restaurant", parent_category_id=1, subcategories=[]
    )
    groceries = SimpleNamespace(
        id=3, category_name="Groceries", parent_category_id=1, subcategories=[]
    )
    food = SimpleNamespace(
        id=1,
        category_name="Food",
        parent_category_id=None,
        subcategories=[restaurant, groceries],
    )

    categories_repository = MagicMock()
    categories_repository.get_all.return_value = [food, restaurant, groceries]

    return categories_repository
