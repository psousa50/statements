import json
from typing import List

from src.app.ai.gemini_ai import GeminiAI
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.prompts import categorization_prompt
from src.app.services.categorizers.transaction_categorizer import (
    CategorizableTransaction, CategorizationResult, TransactionCategorizer)


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
        self, transactions: List[CategorizableTransaction]
    ) -> List[CategorizationResult]:
        if not self.categories:
            raise ValueError("Categories not loaded")

        try:
            prompt = categorization_prompt(transactions, self.categories)
            response = await self.gemini.generate(prompt)

            # Parse the response to extract category_id and confidence
            try:
                results = json.loads(response)
                categorized_results = []
                for i, result in enumerate(results):
                    category_id = result.get("category_id")
                    confidence = result.get("confidence", 0.0)
                    if category_id is not None:
                        categorized_results.append(
                            CategorizationResult(
                                id=transactions[i].id,
                                category_id=category_id,
                                confidence=confidence,
                            )
                        )
                return categorized_results
            except json.JSONDecodeError:
                # If response isn't valid JSON, try to extract just the category ID
                for category in self.categories:
                    if str(category.id) in response:
                        return [
                            CategorizationResult(
                                id=transaction.id,
                                category_id=category.id,
                                confidence=0.7,
                            )
                            for transaction in transactions
                        ]

            except Exception as e:
                print(f"Error: {e}")
                raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def refresh_rules(self):
        self.categories = self.categories_repository.get_all()
        return self.categories
