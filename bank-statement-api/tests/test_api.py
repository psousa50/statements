from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
from datetime import date

from src.app.main import app
from src.app.db import Base, get_db
from src.app.models import Category, Transaction


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_with_categories(test_db):
    db = TestingSessionLocal()
    categories = [
        Category(id=1, category_name="Groceries"),
        Category(id=2, category_name="Transport"),
        Category(id=3, category_name="Entertainment")
    ]
    db.add_all(categories)
    db.commit()
    yield db
    db.close()


@pytest.fixture(scope="function")
def db_with_transactions(db_with_categories):
    db = TestingSessionLocal()
    transactions = [
        Transaction(id=1, date=date(2023, 1, 1), description="Supermarket", amount=50.0, category_id=1),
        Transaction(id=2, date=date(2023, 1, 2), description="Uber", amount=15.0, category_id=2),
        Transaction(id=3, date=date(2023, 1, 3), description="Netflix", amount=12.99, category_id=3)
    ]
    db.add_all(transactions)
    db.commit()
    yield db
    db.close()


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Bank Statement API" in response.json()["message"]


def test_get_categories(db_with_categories):
    response = client.get("/categories/")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 3
    assert categories[0]["category_name"] == "Groceries"


def test_create_category(test_db):
    response = client.post(
        "/categories/",
        json={"category_name": "Test Category"}
    )
    assert response.status_code == 200
    assert response.json()["category_name"] == "Test Category"


def test_get_transactions(db_with_transactions):
    response = client.get("/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 3
    assert transactions[0]["description"] == "Netflix"  # Most recent first


def test_get_transactions_with_filters(db_with_transactions):
    # Test date filter
    response = client.get("/transactions/?start_date=2023-01-02")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 2
    
    # Test category filter
    response = client.get("/transactions/?category_id=1")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Supermarket"
    
    # Test search filter
    response = client.get("/transactions/?search=uber")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Uber"
