import pytest
from unittest.mock import MagicMock, patch
from src.app.services.categorizer import TransactionCategorizer
from src.app.models import Category, Transaction


def test_categorize_transaction():
    # Create a mock DB session
    mock_db = MagicMock()
    
    # Create the categorizer with the mock DB
    categorizer = TransactionCategorizer(mock_db)
    
    # Test various descriptions
    assert categorizer.categorize_transaction("LIDL STORE PURCHASE") == "Groceries"
    assert categorizer.categorize_transaction("UBER TRIP 12345") == "Transport"
    assert categorizer.categorize_transaction("NETFLIX SUBSCRIPTION") == "Entertainment"
    assert categorizer.categorize_transaction("SALARY PAYMENT") == "Income"
    assert categorizer.categorize_transaction("UNKNOWN TRANSACTION") is None


def test_get_or_create_category_existing():
    # Create a mock DB session
    mock_db = MagicMock()
    
    # Mock the query result for an existing category
    mock_category = Category(id=1, category_name="Groceries")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_category
    
    # Create the categorizer with the mock DB
    categorizer = TransactionCategorizer(mock_db)
    
    # Test getting an existing category
    result = categorizer.get_or_create_category("Groceries")
    
    # Verify the result
    assert result == mock_category
    
    # Verify that no new category was created
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_get_or_create_category_new():
    # Create a mock DB session
    mock_db = MagicMock()
    
    # Mock the query result for a non-existing category
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Create the categorizer with the mock DB
    categorizer = TransactionCategorizer(mock_db)
    
    # Test creating a new category
    result = categorizer.get_or_create_category("NewCategory")
    
    # Verify that a new category was created
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    
    # Verify the category name
    args, _ = mock_db.add.call_args
    assert args[0].category_name == "NewCategory"


def test_categorize_transactions():
    # Create a mock DB session
    mock_db = MagicMock()
    
    # Create mock transactions
    transactions = [
        Transaction(id=1, description="LIDL PURCHASE", amount=50.0),
        Transaction(id=2, description="UBER RIDE", amount=15.0),
        Transaction(id=3, description="UNKNOWN", amount=25.0)
    ]
    
    # Mock get_or_create_category to return categories with IDs
    def mock_get_or_create(category_name):
        category_ids = {"Groceries": 1, "Transport": 2}
        return Category(id=category_ids.get(category_name, 99), category_name=category_name)
    
    # Create the categorizer with the mock DB
    categorizer = TransactionCategorizer(mock_db)
    categorizer.get_or_create_category = mock_get_or_create
    
    # Categorize the transactions
    results = categorizer.categorize_transactions(transactions)
    
    # Verify the results
    assert len(results) == 3
    assert results[0][1] == "Groceries"
    assert results[1][1] == "Transport"
    assert results[2][1] is None
    
    # Verify the category IDs were set
    assert transactions[0].category_id == 1
    assert transactions[1].category_id == 2
    assert transactions[2].category_id is None
    
    # Verify that changes were committed
    mock_db.commit.assert_called_once()
