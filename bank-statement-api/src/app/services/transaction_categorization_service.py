import asyncio
import logging

from ..repositories.categories_repository import CategoriesRepository
from ..repositories.transactions_repository import TransactionsRepository
from .categorizers.transaction_categorizer import (
    CategorisationData,
    TransactionCategorizer,
)

logger = logging.getLogger("app")


class TransactionCategorizationService:
    def __init__(
        self,
        categories_repository: CategoriesRepository,
        transactions_repository: TransactionsRepository,
        categorizer: TransactionCategorizer,
    ):
        self.categories_repository = categories_repository
        self.transactions_repository = transactions_repository
        self.categorizer = categorizer

    async def categorize_pending_transactions(self, batch_size: int = 10) -> int:
        categorized_count = 0
        logger.debug("Starting categorization process...")
        while True:
            await asyncio.sleep(1)
            pending_transactions = (
                self.transactions_repository.get_uncategorized_transactions(batch_size)
            )
            logger.debug(f"Found {len(pending_transactions)} pending transactions")
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
                    sub_category_id = result.sub_category_id
                    logger.debug(
                        f"Categorizing transaction {result.transaction_id} with sub_category_id {sub_category_id}"
                    )
                    category_id = self.categories_repository.get_parent_category_id(
                        sub_category_id
                    )
                    logger.debug(f"Found parent category_id {category_id}")
                    self.transactions_repository.update_transaction_category(
                        transaction_id=result.transaction_id,
                        category_id=category_id,
                        sub_category_id=sub_category_id,
                        status="categorized",
                    )
                    logger.debug(f"Categorized transaction {result.transaction_id}")
                    categorized_count += 1
                except Exception:
                    self.transactions_repository.update_transaction_category(
                        transaction_id=result.transaction_id,
                        category_id=None,
                        sub_category_id=None,
                        status="failed",
                    )
                    logger.error(
                        f"Failed to categorize transaction {result.transaction_id}"
                    )
        return categorized_count
