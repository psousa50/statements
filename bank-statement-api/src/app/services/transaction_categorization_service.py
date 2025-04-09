from ..repositories.transactions_repository import TransactionsRepository
from .categorizers.transaction_categorizer import TransactionCategorizer


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

        for transaction in pending_transactions:
            try:
                category_id, confidence = await self.categorizer.categorize_transaction(
                    transaction.description
                )

                if category_id is not None:
                    self.transactions_repository.update_transaction_category(
                        transaction.id, category_id, "categorized"
                    )
                    categorized_count += 1
                else:
                    self.transactions_repository.update_transaction_category(
                        transaction.id, None, "failed"
                    )
            except Exception:
                self.transactions_repository.update_transaction_category(
                    transaction.id, None, "failed"
                )

        return categorized_count
