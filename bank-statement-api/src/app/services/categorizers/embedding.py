import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.app.repositories.categories_repository import CategoriesRepository
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
            raise ValueError("Categories not loaded")

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

    async def categorize_transaction(
        self, transactions: List[CategorisationData]
    ) -> List[CategorizationResult]:
        unique_normalized_descriptions = list(
            set(transaction.normalized_description for transaction in transactions)
        )

        transaction_embeddings = self.model.encode(unique_normalized_descriptions)
        similarities = self.similarity_func(transaction_embeddings, self.embeddings)

        results = []
        for i, transaction in enumerate(transactions):
            similarity_idx = unique_normalized_descriptions.index(
                transaction.normalized_description
            )
            similarity = similarities[similarity_idx]
            best_idx = np.argmax(similarity)
            confidence = similarity[best_idx]

            main_category_id = self.expanded_categories[best_idx].category_id
            results.append(
                CategorizationResult(
                    transaction_id=transaction.transaction_id,
                    category_id=main_category_id,
                    confidence=float(confidence),
                )
            )

        return results

    def refresh_rules(self):
        self.expanded_categories, self.embeddings = self.refresh_categories_embeddings()
        return self.expanded_categories, self.embeddings
