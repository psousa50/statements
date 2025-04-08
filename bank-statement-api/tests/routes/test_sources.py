import uuid
from fastapi.testclient import TestClient

from src.app.repositories.sources_repository import SourcesRepository
from tests.conftest import create_app, db_session, random_source


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
    
    source = random_source()
    sources_repository.create(source)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    all_sources = client.get("/sources").json()
    test_source = next(s for s in all_sources if s["name"] == source.name)
    
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
    
    response = client.get("/sources/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_source():
    sources_repository = SourcesRepository(db_session)
    
    source = random_source()
    sources_repository.create(source)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    all_sources = client.get("/sources").json()
    test_source = next(s for s in all_sources if s["name"] == source.name)
    
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
    
    updated_source = sources_repository.get_by_id(test_source["id"])
    assert updated_source.name == new_name
    assert updated_source.description == new_description


def test_delete_source():
    sources_repository = SourcesRepository(db_session)
    
    source = random_source()
    sources_repository.create(source)
    
    app_instance = create_app(
        db_session=db_session,
        sources_repository=sources_repository
    )
    
    client = TestClient(app_instance.app)
    
    all_sources = client.get("/sources").json()
    test_source = next(s for s in all_sources if s["name"] == source.name)
    
    response = client.delete(f"/sources/{test_source['id']}")
    
    assert response.status_code == 204
    
    deleted_source = sources_repository.get_by_id(test_source["id"])
    assert deleted_source is None
