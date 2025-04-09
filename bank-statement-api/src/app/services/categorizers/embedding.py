import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.app.repositories.categories_repository import CategoriesRepository
from src.app.services.categorizers.transaction_categorizer import CategorizableTransaction, CategorizationResult, TransactionCategorizer


@dataclass
class Subcategory:
    category_id: int
    category_name: str
    subcategory_name: str


class EmbeddingTransactionCategorizer(TransactionCategorizer):
    def __init__(
        self,
        categories_repository: CategoriesRepository,
        model=None,
        similarity_func=None,
    ):
        # Force CPU usage to avoid MPS issues
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        self.categories_repository = categories_repository
        self.model = model or SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2", device="cpu"  # Force CPU usage
        )
        self.similarity_func = similarity_func or cosine_similarity
        self.expanded_categories, self.embeddings = self.refresh_categories_embeddings()

    def refresh_categories_embeddings(
        self,
    ) -> Tuple[List[Subcategory], np.ndarray]:
        categories = self.categories_repository.get_all()

        if not categories:
            return [], np.array([])

        expanded_categories = [
            Subcategory(sub_cat.id, cat.category_name, sub_cat.category_name)
            for cat in categories
            if cat.subcategories is not None
            for sub_cat in cat.subcategories
        ]

        category_texts = [
            f"{cat.category_name} - {cat.subcategory_name}"
            for cat in expanded_categories
        ]
        embeddings = self.model.encode(category_texts)

        return expanded_categories, embeddings

    async def categorize_transaction(self, transactions: List[CategorizableTransaction]) -> List[CategorizationResult]:
        try:
            transaction_embeddings = self.model.encode([transaction.normalized_description for transaction in transactions])
            similarities = self.similarity_func(transaction_embeddings, self.embeddings)

            results = []
            for i, similarity in enumerate(similarities):
                if similarity.ndim > 1:
                    best_idx = np.argmax(similarity[0])
                    confidence = similarity[0][best_idx]
                else:
                    best_idx = np.argmax(similarity)
                    confidence = similarity[best_idx]

                if best_idx < len(self.expanded_categories):
                    main_category_id = self.expanded_categories[best_idx].category_id
                    results.append(
                        CategorizationResult(id=transactions[i].id, category_id=main_category_id, confidence=confidence))
                else:
                    results.append(CategorizationResult(id=transactions[i].id, category_id=None, confidence=0.0))

            return results
        except Exception:
            return [CategorizationResult(id=transaction.id, category_id=None, confidence=0.0) for transaction in transactions]

    def refresh_rules(self):
        self.expanded_categories, self.embeddings = self.refresh_categories_embeddings()
        return self.expanded_categories, self.embeddings
