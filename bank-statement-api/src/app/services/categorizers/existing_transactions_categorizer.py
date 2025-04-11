import logging
from typing import List

from src.app.repositories.transactions_repository import TransactionsRepository
from src.app.services.categorizers.transaction_categorizer import (
    CategorisationData,
    CategorizationResult,
    TransactionCategorizer,
)

logger = logging.getLogger("app")


class ExistingTransactionsCategorizer(TransactionCategorizer):
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        fallback_categorizer: TransactionCategorizer,
    ):
        self.transactions_repository = transactions_repository
        self.fallback_categorizer = fallback_categorizer

    async def categorize_transaction(
        self, transactions: List[CategorisationData]
    ) -> List[CategorizationResult]:
        results = []
        transactions_for_fallback = []

        description_category_pairs = (
            self.transactions_repository.get_unique_normalized_descriptions(100)
        )
        for desc, sub_category_id in description_category_pairs:
            logger.debug(f"Found existing category for {desc}")

        description_to_category = {
            desc: sub_category_id
            for desc, sub_category_id in description_category_pairs
        }

        for transaction in transactions:
            if transaction.normalized_description in description_to_category:
                logger.debug(
                    f"Found existing category for {transaction.normalized_description}"
                )
                sub_category_id = description_to_category[
                    transaction.normalized_description
                ]
                results.append(
                    CategorizationResult(
                        transaction_id=transaction.transaction_id,
                        sub_category_id=sub_category_id,
                        confidence=1.0,
                    )
                )
            else:
                transactions_for_fallback.append(transaction)

        if transactions_for_fallback:
            logger.debug(
                f"Falling back to {self.fallback_categorizer.__class__.__name__} for {len(transactions_for_fallback)} transactions"
            )
            fallback_results = await self.fallback_categorizer.categorize_transaction(
                transactions_for_fallback
            )
            results.extend(fallback_results)

        return results

    def refresh_rules(self):
        # Pass through to the fallback categorizer
        return self.fallback_categorizer.refresh_rules()
