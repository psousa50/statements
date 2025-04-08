from types import SimpleNamespace
from unittest.mock import MagicMock

from src.app.services.categorizer import TransactionCategorizer


class TestTransactionCategorizer:

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

        categorizer = TransactionCategorizer(
            categories_repository=categories_repository
        )

        category_id, confidence = categorizer.categorize_transaction(
            "Dinner at a nice restaurant"
        )

        print(f"Category ID: {category_id}, Confidence: {confidence}")

        assert category_id == 2
        assert confidence > 0.5
