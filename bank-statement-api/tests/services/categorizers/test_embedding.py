from unittest.mock import MagicMock

import pytest

from src.app.services.categorizers.embedding import EmbeddingTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import CategorisationData
from tests.conftest import create_category_tree


@pytest.mark.integration
class TestEmbeddingTransactionCategorizer:
    @pytest.mark.asyncio
    async def test_categorize_transaction(self):
        categories = create_category_tree(
            id=10,
            category_name="Food",
            subcategory_id_1=20,
            subcategory_name_1="Restaurant",
            subcategory_id_2=30,
            subcategory_name_2="Groceries",
        )
        categories_repository = MagicMock()
        categories_repository.get_all.return_value = categories

        categorizer = EmbeddingTransactionCategorizer(
            categories_repository=categories_repository
        )

        transactions = [
            CategorisationData(
                transaction_id=100,
                description="Dinner at a nice restaurant",
                normalized_description="dinner at a nice restaurant",
            ),
            CategorisationData(
                transaction_id=200,
                description="Payment to Groceries Store",
                normalized_description="payment to groceries store",
            ),
        ]
        results = await categorizer.categorize_transaction(transactions)

        assert results[0].transaction_id == 100
        assert results[0].sub_category_id == 20
        assert results[0].confidence > 0.0

        assert results[1].transaction_id == 200
        assert results[1].sub_category_id == 30
        assert results[1].confidence > 0.4
