import pytest
from unittest.mock import MagicMock

from types import SimpleNamespace

from src.app.services.categorizers.embedding import EmbeddingTransactionCategorizer
from src.app.services.categorizers.gemini import GeminiTransactionCategorizer
from src.app.services.categorizers.rule_based import RuleBasedTransactionCategorizer
from src.app.services.categorizers.keyword import KeywordTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import CategorizableTransaction

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
        
        transactions = [CategorizableTransaction(id=1, description="Payment to GROCERIES STORE", normalized_description="Payment to GROCERIES STORE")]
        results = await categorizer.categorize_transaction(transactions)
        
        assert results[0].category_id == 3
        assert results[0].confidence == 1.0
        
    def test_keyword_categorizer(self):
        categories_repository = create_sample_categories_repository()
        categorizer = KeywordTransactionCategorizer(
            categories_repository=categories_repository
        )
        
        categorizer.add_keyword("grocery", 3)
        categorizer.add_keyword("restaurant", 2)
        
        transactions = [CategorizableTransaction(id=1, description="Payment to GROCERIES STORE", normalized_description="Payment to GROCERIES STORE")]
        results = categorizer.categorize_transaction(transactions)
        
        assert results[0].category_id == 3
        assert results[0].confidence > 0.0
        
        transactions = [CategorizableTransaction(id=1, description="Dinner at FANCY RESTAURANT", normalized_description="Dinner at FANCY RESTAURANT")]
        results = categorizer.categorize_transaction(transactions)
        assert results[0].category_id == 2
        assert results[0].confidence > 0.0


@pytest.mark.integration
class TestEmbeddingTransactionCategorizer:
    @pytest.mark.asyncio
    async def test_categorize_transaction(self):
        categories_repository = create_sample_categories_repository()
        categorizer = EmbeddingTransactionCategorizer(
            categories_repository=categories_repository
        )
        
        transactions = [CategorizableTransaction(id=1, description="Payment to GROCERIES STORE", normalized_description="Payment to GROCERIES STORE")]
        results = await categorizer.categorize_transaction(transactions)
        
        assert results[0].category_id == 3
        assert results[0].confidence > 0.0
        
        transactions = [CategorizableTransaction(id=1, description="Dinner at a nice restaurant", normalized_description="Dinner at a nice restaurant")]
        results = await categorizer.categorize_transaction(transactions)

        assert results[0].category_id == 2
        assert results[0].confidence > 0.5

@pytest.mark.integration
@pytest.mark.skip
class TestGeminiCategorizer:
    @pytest.mark.asyncio
    async def test_gemini_categorizer(self):
        categories_repository = create_sample_categories_repository()        
        categorizer = GeminiTransactionCategorizer(
            categories_repository=categories_repository,
        )
        
        transactions = [CategorizableTransaction(id=1, description="Payment to GROCERIES STORE", normalized_description="Payment to GROCERIES STORE")]
        results = await categorizer.categorize_transaction(transactions)
        
        assert results[0].category_id is not None
        assert results[0].confidence > 0.0
