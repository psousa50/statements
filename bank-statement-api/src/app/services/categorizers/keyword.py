from typing import Optional, Dict, Tuple

from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.embedding import TransactionCategorizer


class KeywordTransactionCategorizer(TransactionCategorizer):
    def __init__(self, categories_repository: CategoriesRepository, keywords_map: Optional[Dict[str, int]] = None):
        self.categories_repository = categories_repository
        self.keywords_map = keywords_map or {}
        if not keywords_map:
            self.refresh_rules()

    def add_keyword(self, keyword: str, category_id: int):
        """Add a keyword mapping to a category"""
        self.keywords_map[keyword.lower()] = category_id

    def categorize_transaction(self, description: str) -> Tuple[Optional[int], float]:
        description_words = description.lower().split()

        for word in description_words:
            if word in self.keywords_map:
                return self.keywords_map[word], 1.0

        # Try with partial matching
        for keyword, category_id in self.keywords_map.items():
            if keyword in description.lower():
                return category_id, 0.8

        return None, 0.0

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
