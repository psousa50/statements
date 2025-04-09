from typing import Dict, List, Optional

from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.transaction_categorizer import (
    CategorizableTransaction, CategorizationResult, TransactionCategorizer)


class KeywordTransactionCategorizer(TransactionCategorizer):
    def __init__(
        self,
        categories_repository: CategoriesRepository,
        keywords_map: Optional[Dict[str, int]] = None,
    ):
        self.categories_repository = categories_repository
        self.keywords_map = keywords_map or {}
        if not keywords_map:
            self.refresh_rules()

    def add_keyword(self, keyword: str, category_id: int):
        """Add a keyword mapping to a category"""
        self.keywords_map[keyword.lower()] = category_id

    def categorize_transaction(
        self, transactions: List[CategorizableTransaction]
    ) -> List[CategorizationResult]:
        results = []
        for transaction in transactions:
            description = transaction.description.lower()

            for word in description.split():
                if word in self.keywords_map:
                    results.append(
                        CategorizationResult(
                            id=transaction.id,
                            category_id=self.keywords_map[word],
                            confidence=1.0,
                        )
                    )
                    break

        return results

    def refresh_rules(self):
        """Generate keyword mappings from category names"""
        categories = self.categories_repository.get_all()
        self.keywords_map = {}

        for category in categories:
            # Add the main category name as a keyword
            words = category.category_name.lower().split()
            for word in words:
                if len(word) > 3:  # Only use words longer than 3 characters
                    self.keywords_map[word] = category.id

            # Add subcategory names as keywords
            if category.subcategories:
                for subcategory in category.subcategories:
                    words = subcategory.category_name.lower().split()
                    for word in words:
                        if len(word) > 3:
                            self.keywords_map[word] = subcategory.id

        return self.keywords_map
