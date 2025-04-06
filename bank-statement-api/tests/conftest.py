import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.main import app
from src.app.db import Base, get_db
from src.app.models import Category, Transaction, Source
from src.app.services.categorizer import TransactionCategorizer
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.repositories.sources_repository import SourcesRepository
from src.app.repositories.transactions_repository import TransactionsRepository


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
    
    # Patch the TransactionCategorizer constructor to return our mock
    with patch('src.app.main.TransactionCategorizer', return_value=mock_categorizer):
        yield mock_categorizer


# Patch the repositories to use our test database
@pytest.fixture(scope="function")
def patch_repositories(test_db):
    # Create repository instances with the test database
    categories_repo = CategoriesRepository(test_db)
    sources_repo = SourcesRepository(test_db)
    transactions_repo = TransactionsRepository(test_db)
    
    # Patch the repository constructors and methods
    with patch('src.app.main.CategoriesRepository', return_value=categories_repo), \
         patch('src.app.main.SourcesRepository', return_value=sources_repo), \
         patch('src.app.main.TransactionsRepository', return_value=transactions_repo), \
         patch('src.app.repositories.categories_repository.CategoriesRepository.create', autospec=True), \
         patch('src.app.repositories.sources_repository.SourcesRepository.create', autospec=True), \
         patch('src.app.repositories.categories_repository.CategoriesRepository.get_by_name', autospec=True), \
         patch('src.app.repositories.sources_repository.SourcesRepository.get_by_name', autospec=True), \
         patch('src.app.repositories.sources_repository.SourcesRepository.get_by_id', autospec=True), \
         patch('src.app.repositories.sources_repository.SourcesRepository.delete', autospec=True):
        yield


# Create a mock database session that returns objects with IDs set
@pytest.fixture(scope="function")
def mock_db_session():
    """
    Create a mock database session that returns objects with IDs set.
    This ensures that when objects are created in tests, they have valid IDs.
    """
    class MockDBSession:
        def __init__(self):
            self.next_id = 1
            self.objects = {}
        
        def add(self, obj):
            if not hasattr(obj, 'id') or obj.id is None:
                obj.id = self.next_id
                self.next_id += 1
            self.objects[obj.id] = obj
        
        def commit(self):
            pass
        
        def refresh(self, obj):
            pass
        
        def query(self, model):
            class MockQuery:
                def __init__(self, session, model):
                    self.session = session
                    self.model = model
                
                def filter(self, *args, **kwargs):
                    return self
                
                def first(self):
                    return None
                
                def all(self):
                    return [obj for obj in self.session.objects.values() if isinstance(obj, self.model)]
            
            return MockQuery(self, model)
    
    return MockDBSession()


# Create a function to build a test app with injected dependencies
@pytest.fixture
def test_app(test_db):
    """
    Create a test app with all routes and injected dependencies.
    This allows tests to use a clean app instance with controlled dependencies.
    """
    from fastapi import FastAPI
    from src.app.routes.categories import CategoryRouter
    from src.app.routes.sources import SourceRouter
    from src.app.routes.transactions import TransactionRouter
    from src.app.routes.upload import TransactionUploadRouter
    from src.app.repositories.categories_repository import CategoriesRepository
    from src.app.repositories.sources_repository import SourcesRepository
    from src.app.repositories.transactions_repository import TransactionsRepository
    from src.app.services.categorizer import TransactionCategorizer
    
    # Create a new FastAPI app
    app = FastAPI(title="Test Bank Statement API")
    
    # Create repositories with the test database
    categories_repository = CategoriesRepository(test_db)
    sources_repository = SourcesRepository(test_db)
    transactions_repository = TransactionsRepository(test_db)
    
    # Create the categorizer
    categorizer = TransactionCategorizer(categories_repository)
    
    # Create routers with the repositories
    def on_category_change(action, categories):
        categorizer.refresh_rules()
        
    category_router = CategoryRouter(categories_repository, on_change_callback=on_category_change)
    source_router = SourceRouter(sources_repository)
    transaction_router = TransactionRouter(transactions_repository)
    upload_router = TransactionUploadRouter(
        transactions_repository=transactions_repository,
        sources_repository=sources_repository,
        categorizer=categorizer
    )
    
    # Include the routers in the app
    app.include_router(category_router.router)
    app.include_router(source_router.router)
    app.include_router(transaction_router.router)
    app.include_router(upload_router.router)
    
    # Override the get_db dependency
    from src.app.db import get_db
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # We'll close it in the test_db fixture
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app

# Create a test client with the test app
@pytest.fixture
def test_client(test_app):
    """Create a test client using the test app."""
    from fastapi.testclient import TestClient
    return TestClient(test_app)

# Override the get_db dependency for testing
@pytest.fixture(scope="function")
def client(test_db, mock_categorizer_for_api_tests, patch_repositories):
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
