import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.main import app, get_categorizer
from src.app.db import Base, get_db
from src.app.models import Category, Transaction, Source
from src.app.services.categorizer import TransactionCategorizer


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables before running tests
Base.metadata.create_all(bind=engine)


# This fixture will be used by the FastAPI dependency override
@pytest.fixture(scope="function")
def test_db():
    # Clear all tables before each test
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(delete(table))
    
    # Create a new session for the test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Mock the TransactionCategorizer for API tests
@pytest.fixture(scope="function")
def mock_categorizer_for_api_tests(monkeypatch, request):
    # Skip this fixture for categorizer tests
    if request.node.module.__name__ == "tests.test_categorizer":
        yield
        return
    
    # Create a mock model
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.5, 0.5]])
    
    # Create a mock similarity function
    def mock_similarity(a, b):
        return np.array([0.8])
    
    # Create a mock categorizer instance
    mock_categorizer = MagicMock()
    mock_categorizer.categorize_transaction.return_value = (1, 0.8)  # Return a dummy category ID and confidence
    
    # Create a mock get_categorizer function
    def mock_get_categorizer_func(db):
        return mock_categorizer
    
    # Override the get_categorizer dependency
    app.dependency_overrides[get_categorizer] = mock_get_categorizer_func
    
    yield mock_categorizer


# Override the get_db dependency for testing
@pytest.fixture(scope="function")
def client(test_db, mock_categorizer_for_api_tests):
    # Create a function that returns the test database session
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # We'll close it in the test_db fixture
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client using the app with the overridden dependency
    with TestClient(app) as client:
        yield client
    
    # Clear the dependency overrides after the test
    app.dependency_overrides.clear()
