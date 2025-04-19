from fastapi.testclient import TestClient

from src.app.repositories.categories_repository import CategoriesRepository
from tests.conftest import create_app, db_session, random_category


def test_create_category():
    categories_repository = CategoriesRepository(db_session)

    app_instance = create_app(
        db_session=db_session, categories_repository=categories_repository
    )

    client = TestClient(app_instance.app)

    existing_categories = len(categories_repository.get_all())

    category = random_category()
    response = client.post(
        "/categories", json={"category_name": category.category_name}
    )

    assert response.status_code == 200

    categories = categories_repository.get_all()
    assert len(categories) == existing_categories + 1
    assert (
        len([c for c in categories if c.category_name == category.category_name]) == 1
    )


def test_create_category_if_exists():
    categories_repository = CategoriesRepository(db_session)
    category = random_category()
    categories_repository.create(category)

    app_instance = create_app(
        db_session=db_session, categories_repository=categories_repository
    )

    client = TestClient(app_instance.app)

    existing_categories = len(categories_repository.get_all())

    response = client.post(
        "/categories", json={"category_name": category.category_name}
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"] == f"Category {category.category_name} already exists"
    )

    categories = categories_repository.get_all()
    assert len(categories) == existing_categories


def test_get_categories():
    categories_repository = CategoriesRepository(db_session)

    category1 = random_category()
    category2 = random_category()
    categories_repository.create(category1)
    categories_repository.create(category2)

    app_instance = create_app(
        db_session=db_session, categories_repository=categories_repository
    )

    client = TestClient(app_instance.app)

    response = client.get("/categories")

    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 2
    assert any(c["categoryName"] == category1.category_name for c in categories)
    assert any(c["categoryName"] == category2.category_name for c in categories)


def test_get_category():
    categories_repository = CategoriesRepository(db_session)

    category = random_category()
    categories_repository.create(category)

    app_instance = create_app(
        db_session=db_session, categories_repository=categories_repository
    )

    client = TestClient(app_instance.app)

    all_categories = client.get("/categories").json()
    test_category = next(
        c for c in all_categories if c["categoryName"] == category.category_name
    )

    response = client.get(f"/categories/{test_category['id']}")

    assert response.status_code == 200
    assert response.json()["categoryName"] == category.category_name
    assert response.json()["id"] == test_category["id"]


def test_get_category_not_found():
    categories_repository = CategoriesRepository(db_session)

    app_instance = create_app(
        db_session=db_session, categories_repository=categories_repository
    )

    client = TestClient(app_instance.app)

    response = client.get("/categories/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
