import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.db import Base
from src.app.main import App
from src.app.models import Category, Source
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.repositories.sources_repository import SourcesRepository


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

def random_source():
    return Source(
        name=f"TestSource_{uuid.uuid4().hex[:8]}",
        description=f"Description for test source {uuid.uuid4().hex[:8]}"
    )

# Tests for get_categories and get_category endpoints
def test_get_categories():
    categories_repository = CategoriesRepository(db_session)
    
    # Create some test categories
    category1 = random_category()
    category2 = random_category()
    categories_repository.create(category1)
    categories_repository.create(category2)
    
    app_instance = create_app(
        db_session=db_session,
        categories_repository=categories_repository
    )
    
    client = TestClient(app_instance.app)
    
    response = client.get("/categories")
    
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 2
    assert any(c["category_name"] == category1.category_name for c in categories)
    assert any(c["category_name"] == category2.category_name for c in categories)

def test_get_category():
    categories_repository = CategoriesRepository(db_session)
    
    # Create a test category
    category = random_category()
    categories_repository.create(category)
    
    app_instance = create_app(
        db_session=db_session,
        categories_repository=categories_repository
    )
    
    client = TestClient(app_instance.app)
    
    # Get all categories to find the ID of our test category
    all_categories = client.get("/categories").json()
    test_category = next(c for c in all_categories if c["category_name"] == category.category_name)
    
    # Get the specific category
    response = client.get(f"/categories/{test_category['id']}")
    
    assert response.status_code == 200
    assert response.json()["category_name"] == category.category_name
    assert response.json()["id"] == test_category["id"]

def test_get_category_not_found():
    categories_repository = CategoriesRepository(db_session)
    
    app_instance = create_app(
        db_session=db_session,
        categories_repository=categories_repository
    )
    
    client = TestClient(app_instance.app)
    
    # Try to get a category with a non-existent ID
    response = client.get("/categories/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

# Tests for sources endpoints
def test_create_source():
    sources_repository = SourcesRepository(db_session)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    existing_sources = len(sources_repository.get_all())
    
    source = random_source()
    response = client.post(
        "/sources",
        json={
            "name": source.name,
            "description": source.description
        }
    )
    
    assert response.status_code == 200
    
    sources = sources_repository.get_all()
    assert len(sources) == existing_sources + 1
    assert len([s for s in sources if s.name == source.name]) == 1

def test_create_source_if_exists():
    sources_repository = SourcesRepository(db_session)
    source = random_source()
    sources_repository.create(source)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    existing_sources = len(sources_repository.get_all())
    
    response = client.post(
        "/sources",
        json={
            "name": source.name,
            "description": "New description"
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
    
    sources = sources_repository.get_all()
    assert len(sources) == existing_sources

def test_get_sources():
    sources_repository = SourcesRepository(db_session)
    
    # Create some test sources
    source1 = random_source()
    source2 = random_source()
    sources_repository.create(source1)
    sources_repository.create(source2)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    response = client.get("/sources")
    
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) >= 2
    assert any(s["name"] == source1.name for s in sources)
    assert any(s["name"] == source2.name for s in sources)

def test_get_source():
    sources_repository = SourcesRepository(db_session)
    
    # Create a test source
    source = random_source()
    sources_repository.create(source)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    # Get all sources to find the ID of our test source
    all_sources = client.get("/sources").json()
    test_source = next(s for s in all_sources if s["name"] == source.name)
    
    # Get the specific source
    response = client.get(f"/sources/{test_source['id']}")
    
    assert response.status_code == 200
    assert response.json()["name"] == source.name
    assert response.json()["id"] == test_source["id"]

def test_get_source_not_found():
    sources_repository = SourcesRepository(db_session)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    # Try to get a source with a non-existent ID
    response = client.get("/sources/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_source():
    sources_repository = SourcesRepository(db_session)
    
    # Create a test source
    source = random_source()
    sources_repository.create(source)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    # Get all sources to find the ID of our test source
    all_sources = client.get("/sources").json()
    test_source = next(s for s in all_sources if s["name"] == source.name)
    
    # Update the source
    new_name = f"Updated_{source.name}"
    new_description = f"Updated description {uuid.uuid4().hex[:8]}"
    
    response = client.put(
        f"/sources/{test_source['id']}",
        json={
            "name": new_name,
            "description": new_description
        }
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["description"] == new_description
    
    # Verify the source was updated in the database
    updated_source = sources_repository.get_by_id(test_source["id"])
    assert updated_source.name == new_name
    assert updated_source.description == new_description

def test_delete_source():
    sources_repository = SourcesRepository(db_session)
    
    # Create a test source
    source = random_source()
    sources_repository.create(source)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    # Get all sources to find the ID of our test source
    all_sources = client.get("/sources").json()
    test_source = next(s for s in all_sources if s["name"] == source.name)
    
    # Delete the source
    response = client.delete(f"/sources/{test_source['id']}")
    
    assert response.status_code == 204
    
    # Verify the source was deleted from the database
    deleted_source = sources_repository.get_by_id(test_source["id"])
    assert deleted_source is None