import json
from dataclasses import dataclass
from typing import List

from src.app.ai.groq_ai import GroqAI
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.prompts import categorization_prompt
from src.app.services.categorizers.transaction_categorizer import (
    CategorisationData,
    CategorizationResult,
    TransactionCategorizer,
)


@dataclass
class Subcategory:
    category_id: int
    category_name: str
    subcategory_name: str


class GroqTransactionCategorizer(TransactionCategorizer):
    def __init__(
        self,
        categories_repository: CategoriesRepository,
    ):
        self.categories_repository = categories_repository
        self.groq = GroqAI()
        self.categories = categories_repository.get_all()
        self.refresh_rules()

    async def categorize_transaction(
        self, transactions: List[CategorisationData]
    ) -> List[CategorizationResult]:
        if not self.categories:
            raise ValueError("Categories not loaded")

        prompt = categorization_prompt(transactions, self.categories)
        response = await self.groq.generate(prompt)

        results = json.loads(response)
        categorized_results = []
        for result in results:
            transaction_description = result.get("transaction_description")
            category_id = result.get("category_id")
            confidence = result.get("confidence", 0.0)
            for transaction in transactions:
                if transaction.normalized_description == transaction_description:
                    categorized_results.append(
                        CategorizationResult(
                            transaction_id=transaction.transaction_id,
                            category_id=category_id,
                            confidence=confidence,
                        )
                    )
        return categorized_results

    def refresh_rules(self):
        self.categories = self.categories_repository.get_all()
        return self.categories
