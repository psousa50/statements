from typing import Dict, List, Optional

from src.app.repositories.transactions_repository import TransactionsRepository
from src.app.services.categorizers.transaction_categorizer import (
    CategorizableTransaction,
    CategorizationResult,
    TransactionCategorizer,
)


class ExistingTransactionsCategorizer(TransactionCategorizer):
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        fallback_categorizer: TransactionCategorizer,
    ):
        self.transactions_repository = transactions_repository
        self.fallback_categorizer = fallback_categorizer

    async def categorize_transaction(
        self, transactions: List[CategorizableTransaction]
    ) -> List[CategorizationResult]:
        results = []
        transactions_for_fallback = []

        for transaction in transactions:
            existing_transactions = self.transactions_repository.get_transactions_by_normalized_description(
                transaction.normalized_description, 100
            )

            if existing_transactions:
                category_id = existing_transactions[0].category_id
                results.append(
                    CategorizationResult(
                        id=transaction.id,
                        category_id=category_id,
                        confidence=1.0,
                    )
                )
            else:
                transactions_for_fallback.append(transaction)

        if transactions_for_fallback:
            fallback_results = await self.fallback_categorizer.categorize_transaction(
                transactions_for_fallback
            )
            results.extend(fallback_results)

        # Sort results to match the original transaction order
        id_to_result = {result.id: result for result in results}
        return [id_to_result[transaction.id] for transaction in transactions]

    def refresh_rules(self):
        # Pass through to the fallback categorizer
        return self.fallback_categorizer.refresh_rules()
