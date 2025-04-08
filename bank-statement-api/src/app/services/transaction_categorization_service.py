from ..repositories.transactions_repository import TransactionsRepository
from src.app.services.categorizers.embedding import TransactionCategorizer
import inspect
import asyncio


class TransactionCategorizationService:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        categorizer: TransactionCategorizer,
    ):
        self.transactions_repository = transactions_repository
        self.categorizer = categorizer
        self.is_async_categorizer = inspect.iscoroutinefunction(categorizer.categorize_transaction)

    def categorize_pending_transactions(self, batch_size: int = 10) -> int:
        print(f"Using {self.categorizer.__class__.__name__} to categorize transactions.")
        
        # If we have an async categorizer, we need to use a different approach
        if self.is_async_categorizer:
            print("Async categorizer detected, but called from synchronous context.")
            print("This might not work correctly. Consider using an async endpoint.")
            # For synchronous contexts, we'll use a synchronous categorizer instead
            # This is a fallback that might not work optimally
            return 0
        
        pending_transactions = (
            self.transactions_repository.get_uncategorized_transactions(batch_size)
        )

        if not pending_transactions:
            return 0

        categorized_count = 0

        for transaction in pending_transactions:
            try:
                category_id, confidence = self.categorizer.categorize_transaction(
                    transaction.description
                )

                print(f"Categorized {transaction.description} as {category_id} with confidence {confidence}")

                if category_id is not None:
                    self.transactions_repository.update_transaction_category(
                        transaction.id, category_id, "categorized"
                    )
                    categorized_count += 1
                else:
                    self.transactions_repository.update_transaction_category(
                        transaction.id, None, "failed"
                    )
            except Exception as e:
                print(f"Error categorizing transaction: {e}")
                self.transactions_repository.update_transaction_category(
                    transaction.id, None, "failed"
                )

        return categorized_count
    
    async def categorize_pending_transactions_async(self, batch_size: int = 10) -> int:
        print(f"Using {self.categorizer.__class__.__name__} to categorize transactions (async).")
        
        pending_transactions = (
            self.transactions_repository.get_uncategorized_transactions(batch_size)
        )

        if not pending_transactions:
            return 0

        categorized_count = 0

        for transaction in pending_transactions:
            try:
                if self.is_async_categorizer:
                    category_id, confidence = await self.categorizer.categorize_transaction(
                        transaction.description
                    )
                else:
                    # For non-async categorizers in an async context
                    category_id, confidence = self.categorizer.categorize_transaction(
                        transaction.description
                    )

                print(f"Categorized {transaction.description} as {category_id} with confidence {confidence}")

                if category_id is not None:
                    self.transactions_repository.update_transaction_category(
                        transaction.id, category_id, "categorized"
                    )
                    categorized_count += 1
                else:
                    self.transactions_repository.update_transaction_category(
                        transaction.id, None, "failed"
                    )
            except Exception as e:
                print(f"Error categorizing transaction: {e}")
                self.transactions_repository.update_transaction_category(
                    transaction.id, None, "failed"
                )

        return categorized_count
