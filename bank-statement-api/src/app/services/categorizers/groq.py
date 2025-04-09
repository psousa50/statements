import json
from dataclasses import dataclass
from typing import List

from src.app.ai.groq_ai import GroqAI
from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.transaction_categorizer import (
    CategorizableTransaction,
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
        self, transactions: List[CategorizableTransaction]
    ) -> List[CategorizationResult]:
        if not self.categories:
            raise ValueError("Categories not loaded")

        try:
            prompt = self._create_categorization_prompt(transactions)
            response = await self.groq.generate(prompt)

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
                print(f"Error parsing Groq response: {e}")
                raise e
        except Exception as e:
            print(f"Error with Groq generation: {e}")
            raise e

    def refresh_rules(self):
        self.categories = self.categories_repository.get_all()
        return self.categories

    def _create_categorization_prompt(
        self, transactions: List[CategorizableTransaction]
    ) -> str:
        expanded_categories = [
            Subcategory(sub_cat.id, cat.category_name, sub_cat.category_name)
            for cat in self.categories
            if cat.subcategories is not None
            for sub_cat in cat.subcategories
        ]

        categories_info = [
            f"{{id: {cat.category_id}, name: {cat.subcategory_name}}}"
            for cat in expanded_categories
        ]

        transaction_descriptions = [
            f"{{transaction_id: {t.id}, description: {t.description}, normalized_description: {t.normalized_description}}}" for t in transactions
        ]

        prompt = f"""
You are a bank transaction categorization assistant. Your task is to categorize the following transaction description into one of the provided categories.

Transactions: 
{'\n'.join(transaction_descriptions)}

Available Categories:
{json.dumps(categories_info, indent=2)}

Analyze the transaction description and determine the most appropriate category ID from the list above.
Return your answer as a JSON object with the following format:
[
    {{
        "transaction_id": <id of the transaction>,
        "category_id": <id of the selected category or subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }},
    {{
        "transaction_id": <id of the transaction>,
        "category_id": <id of the selected category or subcategory>,
        "confidence": <a number between 0 and 1 indicating your confidence in this categorization>
    }}
]

Only return the JSON object, nothing else.
"""
        return prompt
