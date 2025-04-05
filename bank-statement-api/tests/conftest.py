import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.main import app
from src.app.db import Base, get_db
from src.app.models import Category, Transaction, Source


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


# Override the get_db dependency for testing
@pytest.fixture(scope="function")
def client(test_db):
    # Override the dependency to use our test database
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # We'll close it in the test_db fixture
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client using the app with the overridden dependency
    with TestClient(app) as client:
        yield client
    
    # Clean up after the test
    app.dependency_overrides.clear()
