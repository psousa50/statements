from datetime import date
import io
import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from src.app.models import Category, Transaction, Source


@pytest.fixture
def db_with_categories(test_db):
    # Create test categories
    categories = [
        Category(id=1, category_name="Groceries"),
        Category(id=2, category_name="Transportation"),
        Category(id=3, category_name="Entertainment")
    ]
    test_db.add_all(categories)
    test_db.commit()
    return test_db


@pytest.fixture
def db_with_transactions(db_with_categories):
    # Create a source for the transactions
    source = Source(id=1, name="test_bank", description="Test Bank")
    db_with_categories.add(source)
    db_with_categories.commit()
    
    # Create test transactions
    transactions = [
        Transaction(id=1, date=date(2023, 1, 1), description="Supermarket", amount=50.0, category_id=1, source_id=1),
        Transaction(id=2, date=date(2023, 1, 2), description="Uber", amount=15.0, category_id=2, source_id=1),
        Transaction(id=3, date=date(2023, 1, 3), description="Cinema", amount=20.0, category_id=3, source_id=1)
    ]
    db_with_categories.add_all(transactions)
    db_with_categories.commit()
    
    return db_with_categories


# Mock the SentenceTransformer to avoid dependency issues
@pytest.fixture(autouse=True)
def mock_sentence_transformer():
    # Set SENTENCE_TRANSFORMER_AVAILABLE to False to use the dummy model
    with patch('src.app.services.categorizer.SENTENCE_TRANSFORMER_AVAILABLE', False):
        yield


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_categories(client, db_with_categories):
    response = client.get("/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 3
    assert categories[0]["category_name"] == "Groceries"


def test_create_category(client, test_db):
    response = client.post(
        "/categories",
        json={"category_name": "Food"}
    )
    assert response.status_code == 200
    assert response.json()["category_name"] == "Food"


def test_get_transactions(client, db_with_transactions):
    response = client.get("/transactions")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 3


def test_get_transactions_with_filters(client, db_with_transactions):
    # Test date filter
    response = client.get("/transactions?start_date=2023-01-02")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 2
    
    # Test category filter
    response = client.get("/transactions?category_id=1")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Supermarket"
    
    # Test search filter
    response = client.get("/transactions?search=uber")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Uber"
    
    # Test source_id filter
    response = client.get("/transactions?source_id=1")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 3


def test_upload_file_with_source_id(client, test_db):
    # Create a test CSV file with transaction data
    csv_content = """date,description,amount,currency
2023-02-01,Test Transaction,100.00,EUR"""
    
    # Create a source first
    source = Source(id=1, name="test_bank", description="Test Bank")
    test_db.add(source)
    test_db.commit()
    
    # Upload the file with a source_id
    response = client.post(
        "/upload?source_id=1",
        files={"file": ("test.csv", csv_content, "text/csv")}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result


def test_upload_file_without_source_id(client, test_db):
    # Create a test CSV file with transaction data
    csv_content = """date,description,amount,currency
2023-03-01,Another Transaction,50.00,EUR"""
    
    # Create default source
    default_source = Source(id=1, name="unknown", description="Default source")
    test_db.add(default_source)
    test_db.commit()
    
    # Upload the file without a source_id
    response = client.post(
        "/upload",
        files={"file": ("test.csv", csv_content, "text/csv")}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
