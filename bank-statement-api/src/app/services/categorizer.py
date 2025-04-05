from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from ..models import Category, Transaction


class TransactionCategorizer:
    def __init__(self, db: Session):
        self.db = db
        self.rules = self._initialize_rules()
        
    def _initialize_rules(self) -> Dict[str, List[str]]:
        """Initialize basic categorization rules based on keywords."""
        return {
            "Groceries": ["supermarket", "grocery", "food", "market", "lidl", "aldi", "continente", "pingo doce"],
            "Dining": ["restaurant", "cafe", "coffee", "dining", "food delivery", "uber eats", "glovo"],
            "Transport": ["uber", "taxi", "bolt", "lyft", "train", "bus", "metro", "subway", "transport"],
            "Utilities": ["electricity", "water", "gas", "internet", "phone", "utility", "bill"],
            "Entertainment": ["cinema", "movie", "theater", "concert", "netflix", "spotify", "subscription"],
            "Shopping": ["amazon", "store", "shop", "retail", "clothing", "electronics"],
            "Health": ["pharmacy", "doctor", "hospital", "medical", "healthcare", "clinic"],
            "Housing": ["rent", "mortgage", "property"],
            "Income": ["salary", "deposit", "income", "wage", "payment received"],
            "Transfer": ["transfer", "wire", "bank", "withdrawal", "atm"]
        }
    
    def categorize_transaction(self, description: str) -> Optional[str]:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: The transaction description
            
        Returns:
            The category name or None if no match is found
        """
        description_lower = description.lower()
        
        for category, keywords in self.rules.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        return None
    
    def get_or_create_category(self, category_name: str) -> Category:
        """
        Get an existing category or create a new one if it doesn't exist.
        
        Args:
            category_name: The name of the category
            
        Returns:
            The Category object
        """
        category = self.db.query(Category).filter(Category.category_name == category_name).first()
        
        if not category:
            category = Category(category_name=category_name)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            
        return category
    
    def categorize_transactions(self, transactions: List[Transaction]) -> List[Tuple[Transaction, Optional[str]]]:
        """
        Categorize a list of transactions.
        
        Args:
            transactions: List of transactions to categorize
            
        Returns:
            List of tuples containing the transaction and its category name
        """
        results = []
        
        for transaction in transactions:
            category_name = self.categorize_transaction(transaction.description)
            results.append((transaction, category_name))
            
            if category_name:
                category = self.get_or_create_category(category_name)
                transaction.category_id = category.id
        
        self.db.commit()
        return results
