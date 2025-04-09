import pytest
from unittest.mock import MagicMock

from types import SimpleNamespace

from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.embedding import EmbeddingTransactionCategorizer
from src.app.services.categorizers.gemini import GeminiTransactionCategorizer
from src.app.services.categorizers.rule_based import RuleBasedTransactionCategorizer
from src.app.services.categorizers.keyword import KeywordTransactionCategorizer


def create_sample_categories_repository():
    restaurant = SimpleNamespace(
        id=2, category_name="Restaurant", parent_category_id=1, subcategories=[]
    )
    groceries = SimpleNamespace(
        id=3, category_name="Groceries", parent_category_id=1, subcategories=[]
    )
    food = SimpleNamespace(
        id=1,
        category_name="Food",
        parent_category_id=None,
        subcategories=[restaurant, groceries],
    )

    categories_repository = MagicMock()
    categories_repository.get_all.return_value = [food, restaurant, groceries]

    return categories_repository

@pytest.mark.integration
class TestDifferentCategorizers:
        
    @pytest.mark.asyncio
    async def test_rule_based_categorizer(self):
        categories_repository = create_sample_categories_repository()
        categorizer = RuleBasedTransactionCategorizer(
            categories_repository=categories_repository
        )
        
        category_id, confidence = await categorizer.categorize_transaction("Payment to GROCERIES STORE")
        
        assert category_id == 3
        assert confidence == 1.0
        
    def test_keyword_categorizer(self):
        categories_repository = create_sample_categories_repository()
        categorizer = KeywordTransactionCategorizer(
            categories_repository=categories_repository
        )
        
        categorizer.add_keyword("grocery", 3)
        categorizer.add_keyword("restaurant", 2)
        
        category_id, confidence = categorizer.categorize_transaction("Payment to GROCERY STORE")
        
        assert category_id == 3
        assert confidence > 0.0
        
        category_id, confidence = categorizer.categorize_transaction("Dinner at FANCY RESTAURANT")
        assert category_id == 2
        assert confidence > 0.0


@pytest.mark.integration
class TestEmbeddingTransactionCategorizer:
    @pytest.mark.asyncio
    async def test_categorize_transaction(self):
        categories_repository = create_sample_categories_repository()
        categorizer = EmbeddingTransactionCategorizer(
            categories_repository=categories_repository
        )
        
        category_id, confidence = await categorizer.categorize_transaction("Payment to GROCERY STORE")
        
        assert category_id == 3
        assert confidence > 0.0
        
        category_id, confidence = await categorizer.categorize_transaction(
            "Dinner at a nice restaurant"
        )

        assert category_id == 2
        assert confidence > 0.5

@pytest.mark.integration
class TestGeminiCategorizer:
    @pytest.mark.asyncio
    async def test_gemini_categorizer(self):
        categories_repository = create_sample_categories_repository()        
        categorizer = GeminiTransactionCategorizer(
            categories_repository=categories_repository,
        )
        
        category_id, confidence = await categorizer.categorize_transaction("Payment to GROCERY STORE")
        
        assert category_id is not None
        assert confidence > 0.0
