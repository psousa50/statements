import asyncio

from ..repositories.transactions_repository import TransactionsRepository
from .categorizers.transaction_categorizer import (
    CategorisationData,
    TransactionCategorizer,
)


class TransactionCategorizationService:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        categorizer: TransactionCategorizer,
    ):
        self.transactions_repository = transactions_repository
        self.categorizer = categorizer

    async def categorize_pending_transactions(self, batch_size: int = 10) -> int:
        categorized_count = 0
        print("Starting categorization process...")
        while True:
            await asyncio.sleep(1)
            pending_transactions = (
                self.transactions_repository.get_uncategorized_transactions(batch_size)
            )
            print(f"Found {len(pending_transactions)} pending transactions")
            if not pending_transactions:
                break

            categorized_count += len(pending_transactions)

            categorized_transactions = [
                CategorisationData(
                    transaction_id=transaction.id,
                    description=transaction.description,
                    normalized_description=transaction.normalized_description,
                )
                for transaction in pending_transactions
            ]
            results = await self.categorizer.categorize_transaction(
                categorized_transactions
            )
            for result in results:
                try:
                    category_id = result.category_id
                    self.transactions_repository.update_transaction_category(
                        result.transaction_id, category_id, "categorized"
                    )
                    categorized_count += 1
                except Exception:
                    self.transactions_repository.update_transaction_category(
                        result.transaction_id, None, "failed"
                    )
        return categorized_count
