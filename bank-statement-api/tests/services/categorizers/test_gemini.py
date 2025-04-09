import pytest

from src.app.services.categorizers.gemini import GeminiTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import CategorisationData
from tests.conftest import create_sample_categories_repository


@pytest.mark.integration
@pytest.mark.skip
class TestGeminiCategorizer:
    @pytest.mark.asyncio
    async def test_gemini_categorizer(self):
        categories_repository = create_sample_categories_repository()
        categorizer = GeminiTransactionCategorizer(
            categories_repository=categories_repository,
        )

        transactions = [
            CategorisationData(
                description="Payment to GROCERIES STORE",
                normalized_description="Payment to GROCERIES STORE",
            )
        ]
        results = await categorizer.categorize_transaction(transactions)

        assert results[0].category_id is not None
        assert results[0].confidence > 0.0
