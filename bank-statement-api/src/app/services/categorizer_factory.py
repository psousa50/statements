from typing import Dict, Optional

from ..repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.embedding import (
    EmbeddingTransactionCategorizer,
    TransactionCategorizer,
)
from src.app.services.categorizers.keyword import KeywordTransactionCategorizer
from src.app.services.categorizers.rule_based import RuleBasedTransactionCategorizer
from src.app.services.categorizers.gemini import GeminiTransactionCategorizer


class CategorizerFactory:

    CATEGORIZER_TYPES = {
        "embedding": EmbeddingTransactionCategorizer,
        "rule_based": RuleBasedTransactionCategorizer,
        "keyword": KeywordTransactionCategorizer,
        "gemini": GeminiTransactionCategorizer,
    }

    @classmethod
    def create_categorizer(
        cls,
        categorizer_type: str,
        categories_repository: CategoriesRepository,
        config: Optional[Dict] = None,
    ) -> TransactionCategorizer:
        config = config or {}
        
        if categorizer_type not in cls.CATEGORIZER_TYPES:
            raise ValueError(
                f"Unsupported categorizer type: {categorizer_type}. "
                f"Supported types are: {', '.join(cls.CATEGORIZER_TYPES.keys())}"
            )
        
        categorizer_class = cls.CATEGORIZER_TYPES[categorizer_type]
        
        if categorizer_type == "embedding":
            return categorizer_class(
                categories_repository=categories_repository,
                model=config.get("model"),
                similarity_func=config.get("similarity_func"),
            )
        elif categorizer_type == "keyword":
            return categorizer_class(
                categories_repository=categories_repository,
                keywords_map=config.get("keywords_map"),
            )
        elif categorizer_type == "gemini":
            return categorizer_class(
                categories_repository=categories_repository,
                api_key=config.get("api_key"),
                model_name=config.get("model_name", "gemini-pro"),
            )
        else:
            return categorizer_class(categories_repository=categories_repository)
