from typing import List, Optional

from ..models import Transaction
from ..repositories.transactions_repository import TransactionsRepository
from .categorizer import TransactionCategorizer


class TransactionCategorizationService:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        categorizer: TransactionCategorizer,
    ):
        self.transactions_repository = transactions_repository
        self.categorizer = categorizer

    def categorize_pending_transactions(self, batch_size: int = 100) -> int:
        """
        Categorize a batch of pending transactions
        
        Args:
            batch_size: Maximum number of transactions to process in one batch
            
        Returns:
            Number of transactions successfully categorized
        """
        # Get pending transactions
        pending_transactions = self.transactions_repository.get_uncategorized_transactions(batch_size)
        
        if not pending_transactions:
            return 0
            
        categorized_count = 0
        
        # Process each transaction
        for transaction in pending_transactions:
            try:
                # Use the categorizer to determine the category
                category_id, confidence = self.categorizer.categorize_transaction(
                    transaction.description
                )
                
                if category_id is not None:
                    # Update the transaction with the category and mark as categorized
                    self.transactions_repository.update_transaction_category(
                        transaction.id, 
                        category_id, 
                        "categorized"
                    )
                    categorized_count += 1
                else:
                    # If categorization failed, mark as failed
                    transaction.categorization_status = "failed"
                    self.transactions_repository.update(transaction)
            except Exception:
                # If an error occurred, mark as failed
                transaction.categorization_status = "failed"
                self.transactions_repository.update(transaction)
                
        return categorized_count
