import pytest
import asyncio
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.gemini import GeminiTransactionCategorizer
from src.app.db import get_db

@pytest.mark.asyncio
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

    for description in descriptions:
        category_id, confidence = await categorizer.categorize_transaction(description)
        print(f"{description}: {category_id} {confidence}")
        await asyncio.sleep(1000)
    
    
    