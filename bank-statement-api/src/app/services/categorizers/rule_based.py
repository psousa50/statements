import re
from typing import List

from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.transaction_categorizer import (
    CategorizableTransaction,
    CategorizationResult,
    TransactionCategorizer,
)


class RuleBasedTransactionCategorizer(TransactionCategorizer):
    def __init__(self, categories_repository: CategoriesRepository):
        self.categories_repository = categories_repository
        self.rules = []
        self.refresh_rules()

    async def categorize_transaction(
        self, transactions: List[CategorizableTransaction]
    ) -> List[CategorizationResult]:
        results = []
        for transaction in transactions:
            description = transaction.description.lower()

            for pattern, category_id, confidence in self.rules:
                if re.search(pattern, description):
                    results.append(
                        CategorizationResult(
                            id=transaction.id,
                            category_id=category_id,
                            confidence=confidence,
                        )
                    )
                    break

        return results

    def refresh_rules(self):
        """Refresh the categorization rules from the database"""
        categories = self.categories_repository.get_all()
        self.rules = []

        for category in categories:
            if category.subcategories:
                for subcategory in category.subcategories:
                    pattern = (
                        r"\b" + re.escape(subcategory.category_name.lower()) + r"\b"
                    )
                    self.rules.append((pattern, subcategory.id, 1.0))

        return self.rules
