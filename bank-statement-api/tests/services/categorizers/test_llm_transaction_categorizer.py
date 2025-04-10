import pytest

from src.app.ai.gemini_ai import GeminiAI
from src.app.ai.groq_ai import GroqAI
from src.app.services.categorizers.llm_transaction_categorizer import LLMTransactionCategorizer
from src.app.services.categorizers.transaction_categorizer import CategorisationData
from tests.conftest import create_sample_categories_repository


@pytest.mark.integration
class TestLLMTransactionCategorizer:
    @pytest.mark.asyncio
    async def test_grok_categorizer(self):
        categories_repository = create_sample_categories_repository()
        categorizer = LLMTransactionCategorizer(
            categories_repository=categories_repository,
            llm_client=GroqAI(),
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

    @pytest.mark.asyncio
    async def test_gemini_categorizer(self):
        categories_repository = create_sample_categories_repository()
        categorizer = LLMTransactionCategorizer(
            categories_repository=categories_repository,
            llm_client=GeminiAI()
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
