from datetime import date

from fastapi.testclient import TestClient

from src.app.repositories.categories_repository import CategoriesRepository
from src.app.repositories.sources_repository import SourcesRepository
from src.app.repositories.transactions_repository import TransactionsRepository
from tests.conftest import (
    create_app,
    db_session,
    random_category,
    random_source,
    random_transaction,
)


def test_get_transactions():
    transactions_repository = TransactionsRepository(db_session)
    sources_repository = SourcesRepository(db_session)

    source = sources_repository.create(random_source())
    transaction1 = transactions_repository.create(random_transaction(source.id))
    transaction2 = transactions_repository.create(random_transaction(source.id))

    app_instance = create_app(
        db_session=db_session,
        transactions_repository=transactions_repository,
        sources_repository=sources_repository,
    )

    client = TestClient(app_instance.app)

    response = client.get("/transactions")

    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) >= 2
    assert any(t["description"] == transaction1.description for t in transactions)
    assert any(t["description"] == transaction2.description for t in transactions)


def test_get_transactions_with_filters():
    transactions_repository = TransactionsRepository(db_session)
    sources_repository = SourcesRepository(db_session)

    source = sources_repository.create(random_source())

    transactionCreate1 = random_transaction(source.id)
    transactionCreate1.date = date(2023, 1, 15)
    transactionCreate1.description = "Filtered Transaction Test"
    transaction1 = transactions_repository.create(transactionCreate1)

    transactionCreate2 = random_transaction(source.id)
    transactionCreate2.date = date(2023, 2, 15)
    transaction2 = transactions_repository.create(transactionCreate2)

    app_instance = create_app(
        db_session=db_session,
        transactions_repository=transactions_repository,
        sources_repository=sources_repository,
    )

    client = TestClient(app_instance.app)

    response = client.get("/transactions?start_date=2023-01-01&end_date=2023-01-31")
    assert response.status_code == 200
    transactions = response.json()
    assert any(t["description"] == transaction1.description for t in transactions)
    assert not any(t["description"] == transaction2.description for t in transactions)

    response = client.get(f"/transactions?source_id={source.id}")
    assert response.status_code == 200
    transactions = response.json()
    assert any(t["description"] == transaction1.description for t in transactions)
    assert any(t["description"] == transaction2.description for t in transactions)

    response = client.get("/transactions?search=Filtered")
    assert response.status_code == 200
    transactions = response.json()
    assert any(t["description"] == transaction1.description for t in transactions)
    assert not any(t["description"] == transaction2.description for t in transactions)


def test_get_transaction():
    transactions_repository = TransactionsRepository(db_session)
    sources_repository = SourcesRepository(db_session)

    source = sources_repository.create(random_source())

    transactionCreate = random_transaction(source.id)
    transaction = transactions_repository.create(transactionCreate)

    app_instance = create_app(
        db_session=db_session,
        transactions_repository=transactions_repository,
        sources_repository=sources_repository,
    )

    client = TestClient(app_instance.app)

    response = client.get(f"/transactions/{transaction.id}")

    assert response.status_code == 200
    assert response.json()["description"] == transaction.description
    assert response.json()["id"] == transaction.id


def test_get_transaction_not_found():
    transactions_repository = TransactionsRepository(db_session)
    sources_repository = SourcesRepository(db_session)

    app_instance = create_app(
        db_session=db_session,
        transactions_repository=transactions_repository,
        sources_repository=sources_repository,
    )

    client = TestClient(app_instance.app)

    response = client.get("/transactions/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_categorize_transaction():
    transactions_repository = TransactionsRepository(db_session)
    sources_repository = SourcesRepository(db_session)
    categories_repository = CategoriesRepository(db_session)

    category = categories_repository.create(random_category())
    source = sources_repository.create(random_source())

    transactionCreate = random_transaction(source.id)
    transaction = transactions_repository.create(transactionCreate)

    app_instance = create_app(
        db_session=db_session,
        transactions_repository=transactions_repository,
        sources_repository=sources_repository,
        categories_repository=categories_repository,
    )

    client = TestClient(app_instance.app)

    response = client.put(
        f"/transactions/{transaction.id}/categorize?category_id={category.id}"
    )

    assert response.status_code == 200
    assert response.json()["category_id"] == category.id

    updated_transaction = transactions_repository.get_by_id(transaction.id)
    assert updated_transaction.category_id == category.id


def test_categorize_transaction_not_found():
    transactions_repository = TransactionsRepository(db_session)
    sources_repository = SourcesRepository(db_session)
    categories_repository = CategoriesRepository(db_session)

    category = categories_repository.create(random_category())

    app_instance = create_app(
        db_session=db_session,
        transactions_repository=transactions_repository,
        sources_repository=sources_repository,
        categories_repository=categories_repository,
    )

    client = TestClient(app_instance.app)

    response = client.put(f"/transactions/99999/categorize?category_id={category.id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
