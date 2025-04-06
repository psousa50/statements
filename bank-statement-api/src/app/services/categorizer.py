from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..models import Category

from sentence_transformers import SentenceTransformer    

from ..repositories.categories_repository import CategoriesRepository

class TransactionCategorizer:
    def __init__(self, categories_repository: CategoriesRepository, model=None, similarity_func=None):
        self.categories_repository = categories_repository        
        self.model = model or SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.similarity_func = similarity_func or cosine_similarity
        self.categories, self.embeddings = self.refresh_categories_embeddings()
    
    def refresh_categories_embeddings(self) -> Tuple[Tuple[List[Category], List[Tuple[int, int]]], np.ndarray]:
        categories = self.categories_repository.get_all()
        
        # If there are no categories, return empty lists to avoid errors
        if not categories:
            return (categories, []), np.array([])

        # Create a list of category descriptions for embedding
        category_texts = []
        category_map = []  # Maps index to (main_category_id, sub_category_id)
        
        for main_cat in categories:
            # Check if main_cat has subcategories attribute and it's a list or iterable
            subcats = []
            
            # Try subcategories first
            if hasattr(main_cat, 'subcategories'):
                try:
                    if main_cat.subcategories is not None:
                        subcats = list(main_cat.subcategories)
                except (TypeError, ValueError):
                    # Not iterable
                    pass
            
            # If no subcategories found, try sub_categories for backward compatibility
            if not subcats and hasattr(main_cat, 'sub_categories'):
                try:
                    if main_cat.sub_categories is not None:
                        subcats = list(main_cat.sub_categories)
                except (TypeError, ValueError):
                    # Not iterable
                    pass
            
            # Process subcategories if any were found
            for sub_cat in subcats:
                category_texts.append(f"{main_cat.category_name.lower()} -> {sub_cat.category_name}")
                category_map.append((main_cat.id, sub_cat.id))
        
        # If no category texts were generated, return empty lists
        if not category_texts:
            return (categories, category_map), np.array([])
            
        # Generate embeddings for the categories
        try:
            embeddings = self.model.encode(category_texts)
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Return zeros as fallback
            embeddings = np.zeros((len(category_texts), 4))
            
        return (categories, category_map), embeddings
    
    def categorize_transaction(self, description: str) -> Tuple[Optional[int], float]:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: The transaction description text
            
        Returns:
            A tuple of (category_id, confidence) where category_id is the main category ID
            and confidence is a float between 0 and 1
        """
        # If no embeddings or categories, return None
        if not hasattr(self.categories, '__len__') or len(self.categories[1]) == 0 or self.embeddings.size == 0:
            return None, 0.0
            
        try:
            transaction_embedding = self.model.encode([description.lower()])
            similarities = self.similarity_func(transaction_embedding, self.embeddings)
            
            # Find the best match
            # Handle different shapes of similarity arrays (for testing vs. production)
            if similarities.ndim > 1:
                best_idx = np.argmax(similarities[0])
                confidence = similarities[0][best_idx]
            else:
                best_idx = np.argmax(similarities)
                confidence = similarities[best_idx]
                
            # Get the main category ID for the best match
            _, category_map = self.categories
            if best_idx < len(category_map):
                main_category_id, _ = category_map[best_idx]
                return main_category_id, float(confidence)
            else:
                return None, 0.0
        except Exception as e:
            print(f"Error categorizing transaction: {str(e)}")
            return None, 0.0
    
    def refresh_rules(self):
        """Refresh the categorization rules by updating the categories and embeddings"""
        self.categories, self.embeddings = self.refresh_categories_embeddings()
        return self.categories, self.embeddings