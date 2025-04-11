import json
from typing import List

from src.app.ai.gemini_ai import GeminiAI
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.prompts import categorization_prompt
from src.app.services.categorizers.transaction_categorizer import (
    CategorisationData,
    CategorizationResult,
    TransactionCategorizer,
)


class GeminiTransactionCategorizer(TransactionCategorizer):
    def __init__(
        self,
        categories_repository: CategoriesRepository,
    ):
        self.categories_repository = categories_repository
        self.gemini = GeminiAI()
        self.categories = categories_repository.get_all()
        self.refresh_rules()

    async def categorize_transaction(
        self, transactions: List[CategorisationData]
    ) -> List[CategorizationResult]:
        if not self.categories:
            raise ValueError("Categories not loaded")

        prompt = categorization_prompt(transactions, self.categories)
        response = await self.gemini.generate_async(prompt)

        results = json.loads(response)
        categorized_results = []
        for i, result in enumerate(results):
            sub_category_id = result.get("sub_category_id")
            confidence = result.get("confidence", 0.0)
            if sub_category_id is not None:
                categorized_results.append(
                    CategorizationResult(
                        normalized_description=transactions[i].normalized_description,
                        sub_category_id=sub_category_id,
                        confidence=confidence,
                    )
                )
        return categorized_results

    def refresh_rules(self):
        self.categories = self.categories_repository.get_all()
        return self.categories
