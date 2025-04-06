import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from unittest.mock import MagicMock

from src.app.db import Base
from src.app.main import App
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.models import Category

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


def test_create_category():
    categories_repository = CategoriesRepository(db_session)
        
    app_instance = create_app(
        db_session=db_session,
        categories_repository=categories_repository
    )
    
    client = TestClient(app_instance.app)
    
    existing_categories = len(categories_repository.get_all())

    category = random_category()
    response = client.post(
        "/categories",
        json={"category_name": category.category_name}
    )
    
    assert response.status_code == 200
    
    categories = categories_repository.get_all()
    assert len(categories) == existing_categories + 1
    assert len([c for c in categories if c.category_name == category.category_name]) == 1
    
def test_create_category_if_exists():
    categories_repository = CategoriesRepository(db_session)
    category = random_category()
    categories_repository.create(category)
        
    app_instance = create_app(
        db_session=db_session,
        categories_repository=categories_repository
    )
    
    client = TestClient(app_instance.app)

    existing_categories = len(categories_repository.get_all())
        
    response = client.post(
        "/categories",
        json={"category_name": category.category_name}
    )
    
    assert response.status_code == 409
    assert response.json()["detail"] == f"Category {category.category_name} already exists"   
    
    categories = categories_repository.get_all()
    assert len(categories) == existing_categories

def random_category():
    return Category(category_name=f"TestCategory_{uuid.uuid4().hex[:8]}")
    