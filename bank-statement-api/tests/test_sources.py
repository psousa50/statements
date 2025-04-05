import pytest
from datetime import date

from src.app.models import Source, Transaction


@pytest.fixture(scope="function")
def db_with_sources(test_db):
    sources = [
        Source(id=1, name="unknown", description="Default source for transactions with unknown origin"),
        Source(id=2, name="bank1", description="First bank"),
        Source(id=3, name="bank2", description="Second bank")
    ]
    test_db.add_all(sources)
    test_db.commit()
    return test_db


def test_get_sources(client, db_with_sources):
    response = client.get("/sources")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) == 3
    assert sources[0]["name"] == "unknown"
    assert sources[1]["name"] == "bank1"
    assert sources[2]["name"] == "bank2"


def test_get_source_by_id(client, db_with_sources):
    response = client.get("/sources/2")
    assert response.status_code == 200
    source = response.json()
    assert source["name"] == "bank1"
    assert source["description"] == "First bank"


def test_get_source_not_found(client, db_with_sources):
    response = client.get("/sources/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Source not found"


def test_create_source(client, test_db):
    response = client.post(
        "/sources",
        json={"name": "new_bank", "description": "A new bank source"}
    )
    assert response.status_code == 200
    source = response.json()
    assert source["name"] == "new_bank"
    assert source["description"] == "A new bank source"


def test_create_source_duplicate_name(client, db_with_sources):
    response = client.post(
        "/sources",
        json={"name": "bank1", "description": "Duplicate name"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Source with this name already exists"


def test_update_source(client, db_with_sources):
    response = client.put(
        "/sources/2",
        json={"name": "updated_bank", "description": "Updated description"}
    )
    assert response.status_code == 200
    source = response.json()
    assert source["name"] == "updated_bank"
    assert source["description"] == "Updated description"


def test_update_source_not_found(client, db_with_sources):
    response = client.put(
        "/sources/999",
        json={"name": "nonexistent", "description": "This source doesn't exist"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Source not found"


def test_update_source_duplicate_name(client, db_with_sources):
    response = client.put(
        "/sources/2",
        json={"name": "bank2", "description": "Trying to use existing name"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Source with this name already exists"


def test_delete_source(client, db_with_sources):
    # Create a source that we can delete
    response = client.post(
        "/sources",
        json={"name": "temp_source", "description": "Temporary source for deletion test"}
    )
    source_id = response.json()["id"]
    
    # Delete the source
    response = client.delete(f"/sources/{source_id}")
    assert response.status_code == 200
    deleted_source = response.json()
    assert deleted_source["name"] == "temp_source"
    
    # Verify it's gone
    response = client.get(f"/sources/{source_id}")
    assert response.status_code == 404


def test_delete_default_source(client, db_with_sources):
    # Try to delete the default "unknown" source
    response = client.delete("/sources/1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot delete the default 'unknown' source"


def test_delete_source_with_transactions(client, db_with_sources):
    # Create a transaction that uses source_id=2
    transaction = Transaction(
        date=date(2023, 1, 1),
        description="Test transaction",
        amount=100.0,
        source_id=2
    )
    db_with_sources.add(transaction)
    db_with_sources.commit()
    
    # Try to delete the source
    response = client.delete("/sources/2")
    assert response.status_code == 400
    assert "Cannot delete source that is used by transactions" in response.json()["detail"]
