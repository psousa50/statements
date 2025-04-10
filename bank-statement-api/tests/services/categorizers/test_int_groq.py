import pytest

from src.app.ai.groq_ai import GroqAI
from src.app.db import get_db
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.llm_transaction_categorizer import LLMTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import (
    CategorisationData,
)


@pytest.mark.asyncio
async def test_groq():
    db = next(get_db())
    categories_repository = CategoriesRepository(db)
    categorizer = LLMTransactionCategorizer(
        categories_repository,
        GroqAI(),
    )

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
            CategorisationData(
                transaction_id=i,
                description=description,
                normalized_description=description,
            )
        )

    results = await categorizer.categorize_transaction(transactions)
    for i, result in enumerate(results):
        print(f"{i}: {result}")
