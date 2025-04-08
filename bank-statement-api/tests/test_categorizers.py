import pytest
from unittest.mock import MagicMock

from types import SimpleNamespace

from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizer_factory import CategorizerFactory
from src.app.services.categorizers.embedding import EmbeddingTransactionCategorizer
from src.app.services.categorizers.gemini import GeminiTransactionCategorizer
from src.app.services.categorizers.rule_based import RuleBasedTransactionCategorizer
from src.app.services.categorizers.keyword import KeywordTransactionCategorizer


@pytest.mark.integration
class TestCategorizerFactory:
    def test_create_embedding_categorizer(self):
        mock_repo = MagicMock(spec=CategoriesRepository)
        
        categorizer = CategorizerFactory.create_categorizer(
            "embedding", mock_repo
        )
        
        assert isinstance(categorizer, EmbeddingTransactionCategorizer)
        
    def test_create_rule_based_categorizer(self):
        mock_repo = MagicMock(spec=CategoriesRepository)
        
        categorizer = CategorizerFactory.create_categorizer(
            "rule_based", mock_repo
        )
        
        assert isinstance(categorizer, RuleBasedTransactionCategorizer)
        
    def test_create_keyword_categorizer(self):
        mock_repo = MagicMock(spec=CategoriesRepository)
        
        categorizer = CategorizerFactory.create_categorizer(
            "keyword", mock_repo
        )
        
        assert isinstance(categorizer, KeywordTransactionCategorizer)
        
    def test_create_gemini_categorizer(self):
        mock_repo = MagicMock(spec=CategoriesRepository)
        
        categorizer = CategorizerFactory.create_categorizer(
            "gemini", mock_repo, {"api_key": "test_key"}
        )
        
        assert isinstance(categorizer, GeminiTransactionCategorizer)
        
    def test_invalid_categorizer_type(self):
        mock_repo = MagicMock(spec=CategoriesRepository)
        
        with pytest.raises(ValueError):
            CategorizerFactory.create_categorizer(
                "invalid_type", mock_repo
            )


@pytest.mark.integration
class TestDifferentCategorizers:
    def setup_method(self):
        self.mock_repo = MagicMock(spec=CategoriesRepository)
        
        grocery_category = MagicMock()
        grocery_category.id = 1
        grocery_category.category_name = "Groceries"
        grocery_category.subcategories = []
        
        restaurant_category = MagicMock()
        restaurant_category.id = 2
        restaurant_category.category_name = "Restaurants"
        restaurant_category.subcategories = []
        
        self.mock_repo.get_all.return_value = [grocery_category, restaurant_category]
        
    def test_rule_based_categorizer(self):
        categorizer = CategorizerFactory.create_categorizer(
            "rule_based", self.mock_repo
        )
        
        category_id, confidence = categorizer.categorize_transaction("Payment to GROCERY STORE")
        
        assert isinstance(confidence, float)
        
    def test_keyword_categorizer(self):
        categorizer = CategorizerFactory.create_categorizer(
            "keyword", self.mock_repo
        )
        
        categorizer.add_keyword("grocery", 1)
        categorizer.add_keyword("restaurant", 2)
        
        category_id, confidence = categorizer.categorize_transaction("Payment to GROCERY STORE")
        
        assert category_id == 1
        assert confidence > 0.0
        
        category_id, confidence = categorizer.categorize_transaction("Dinner at FANCY RESTAURANT")
        assert category_id == 2
        assert confidence > 0.0


@pytest.mark.integration
class TestEmbeddingTransactionCategorizer:

    def test_categorize_transaction(self):
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

        categorizer = EmbeddingTransactionCategorizer(
            categories_repository=categories_repository,
        )

        category_id, confidence = categorizer.categorize_transaction(
            "Dinner at a nice restaurant"
        )

        print(f"Category ID: {category_id}, Confidence: {confidence}")

        assert category_id == 2
        assert confidence > 0.5

@pytest.mark.integration
class TestGeminiCategorizer:
    @pytest.mark.skip(reason="Requires API key and network access")
    async def test_gemini_categorizer(self):
        
        mock_repo = MagicMock(spec=CategoriesRepository)
        
        grocery_category = MagicMock()
        grocery_category.id = 1
        grocery_category.category_name = "Groceries"
        grocery_category.subcategories = []
        
        mock_repo.get_all.return_value = [grocery_category]
        
        categorizer = CategorizerFactory.create_categorizer(
            "gemini", 
            mock_repo, 
            {"api_key": "YOUR_API_KEY_HERE"}  # Replace with actual API key for testing
        )
        
        category_id, confidence = await categorizer.categorize_transaction("Payment to GROCERY STORE")
        
        assert category_id is not None
        assert confidence > 0.0
