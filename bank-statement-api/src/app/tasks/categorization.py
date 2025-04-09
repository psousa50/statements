import asyncio

from ..celery_app import celery_app
from ..db import get_db
from ..repositories.categories_repository import CategoriesRepository
from ..repositories.transactions_repository import TransactionsRepository
from ..services.categorizers.existing_transactions_categorizer import (
    ExistingTransactionsCategorizer,
)
from ..services.categorizers.groq import GroqTransactionCategorizer
from ..services.transaction_categorization_service import (
    TransactionCategorizationService,
)


@celery_app.task(name="src.app.tasks.categorization.categorize_pending_transactions")
def categorize_pending_transactions(batch_size: int = 10):
    db = next(get_db())

    groq_categorizer = GroqTransactionCategorizer(CategoriesRepository(db))

    categorizer = ExistingTransactionsCategorizer(
        transactions_repository=TransactionsRepository(db),
        fallback_categorizer=groq_categorizer,
    )

    service = TransactionCategorizationService(TransactionsRepository(db), categorizer)

    return asyncio.run(service.categorize_pending_transactions(batch_size))


def manually_trigger_categorization(batch_size: int = 10):
    return categorize_pending_transactions.delay(batch_size)
