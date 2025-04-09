import pytest

from src.app.db import get_db
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.gemini import GeminiTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import \
    CategorizableTransaction


@pytest.mark.asyncio
@pytest.mark.skip
async def test_gemini():
    db = next(get_db())
    categories_repository = CategoriesRepository(db)
    categorizer = GeminiTransactionCategorizer(categories_repository)

    descriptions = [
        "Aerofarma Laboratorios S.A.I.C",
        "Airbnb",
        "Alges Com Sabores",
        "Alipay",
        "Allegro",
        "Alvaros",
        "Alvaros Cafe Unipess",
        "Amadeu Batista E",
        "Amazon",
        "Anca Lolo",
        "Andor",
        "Angels' Bar",
        "Antoniobarb",
        "Apple",
        "Apple Pay Top-Up by *0264",
        "Apple Pay Top-Up by *6660",
        "Apple Pay Top-Up by *6678",
        "Apple Pay Top-Up by *6964",
        "Apribeiro",
    ]

    transactions = []
    for i, description in enumerate(descriptions):
        transactions.append(
            CategorizableTransaction(
                id=i, description=description, normalized_description=description
            )
        )

    results = await categorizer.categorize_transaction(transactions)
    for i, result in enumerate(results):
        print(f"{i}: {result}")
