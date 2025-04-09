import pytest

from src.app.services.categorizers.groq import GroqTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import CategorisationData
from tests.conftest import create_sample_categories_repository


@pytest.mark.integration
class TestGroqCategorizer:
    @pytest.mark.asyncio
    async def test_grok_categorizer(self):
        categories_repository = create_sample_categories_repository()
        categorizer = GroqTransactionCategorizer(
            categories_repository=categories_repository
        )

        transactions = [
            CategorisationData(
                transaction_id=1,
                description="Payment to GROCERIES STORE",
                normalized_description="Payment to GROCERIES STORE",
            )
        ]
        results = await categorizer.categorize_transaction(transactions)

        assert results[0].category_id == 3
        assert results[0].confidence > 0.0
