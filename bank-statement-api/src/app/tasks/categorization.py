import asyncio
from typing import Callable

from ..celery_app import celery_app
from ..services.transaction_categorization_service import TransactionCategorizationService
from ..repositories.transactions_repository import TransactionsRepository
from ..repositories.categories_repository import CategoriesRepository
from ..services.categorizers.groq import GroqTransactionCategorizer
from ..db import get_db


@celery_app.task(name="src.app.tasks.categorization.categorize_pending_transactions")
def categorize_pending_transactions(batch_size: int = 10):
    db = next(get_db())
    
    service = TransactionCategorizationService(
        TransactionsRepository(db),
        GroqTransactionCategorizer(CategoriesRepository(db))
    )
    
    return asyncio.run(service.categorize_pending_transactions(batch_size))


def manually_trigger_categorization(batch_size: int = 10):
    return categorize_pending_transactions.delay(batch_size)
