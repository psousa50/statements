from typing import List, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..models import Category

from sentence_transformers import SentenceTransformer    

from ..repositories.categories_repository import CategoriesRepository

from dataclasses import dataclass

@dataclass
class Subcategory:
    category_id: int
    category_name: str
    subcategory_name: str

class TransactionCategorizer:
    def __init__(self, categories_repository: CategoriesRepository, model=None, similarity_func=None):
        self.categories_repository = categories_repository
        self.model = model or SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.similarity_func = similarity_func or cosine_similarity
        self.expanded_categories, self.embeddings = self.refresh_categories_embeddings()
    
    def refresh_categories_embeddings(self) -> Tuple[Tuple[List[Category], List[Tuple[int, int]]], np.ndarray]:
        categories = self.categories_repository.get_all()
        
        if not categories:
            return (categories, []), np.array([])

        expanded_categories = [Subcategory(sub_cat.id, cat.category_name, sub_cat.category_name) for cat in categories if cat.subcategories is not None for sub_cat in cat.subcategories]

        category_texts = [f"{cat.category_name} - {cat.subcategory_name}" for cat in expanded_categories]
        embeddings = self.model.encode(category_texts)
        
        return expanded_categories, embeddings
    
    def categorize_transaction(self, description: str) -> Tuple[Optional[int], float]:
        try:
            transaction_embedding = self.model.encode([description.lower()])
            similarities = self.similarity_func(transaction_embedding, self.embeddings)
            
            if similarities.ndim > 1:
                best_idx = np.argmax(similarities[0])
                confidence = similarities[0][best_idx]
            else:
                best_idx = np.argmax(similarities)
                confidence = similarities[best_idx]
                
            if best_idx < len(self.expanded_categories):
                main_category_id = self.expanded_categories[best_idx].category_id
                return main_category_id, float(confidence)
            else:
                return None, 0.0
        except Exception as e:
            return None, 0.0
    
    def refresh_rules(self):
        """Refresh the categorization rules by updating the categories and embeddings"""
        self.expanded_categories, self.embeddings = self.refresh_categories_embeddings()
        return self.expanded_categories, self.embeddings