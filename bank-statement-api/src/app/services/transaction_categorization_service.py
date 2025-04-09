from ..repositories.transactions_repository import TransactionsRepository
from .categorizers.transaction_categorizer import (
    CategorizableTransaction,
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
        pending_transactions = (
            self.transactions_repository.get_uncategorized_transactions(batch_size)
        )

        if not pending_transactions:
            return 0

        categorized_count = 0

        categorized_transactions = [
            CategorizableTransaction(
                id=transaction.id,
                description=transaction.description,
                normalized_description=transaction.normalized_description,
            )
            for transaction in pending_transactions
        ]
        results = await self.categorizer.categorize_transaction(
            categorized_transactions
        )
        for transaction, result in zip(pending_transactions, results):
            try:
                category_id = result.category_id
                self.transactions_repository.update_transaction_category(
                    transaction.id, category_id, "categorized"
                )
                categorized_count += 1
            except Exception:
                self.transactions_repository.update_transaction_category(
                    transaction.id, None, "failed"
                )
        return categorized_count
