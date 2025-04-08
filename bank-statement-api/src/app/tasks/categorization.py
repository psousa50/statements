from sqlalchemy.orm import Session

from ..celery_app import celery_app
from ..db import get_db
from ..repositories.transactions_repository import TransactionsRepository
from ..services.categorizer import TransactionCategorizer
from ..services.transaction_categorization_service import TransactionCategorizationService


@celery_app.task(name="src.app.tasks.categorization.categorize_pending_transactions")
def categorize_pending_transactions(batch_size: int = 10):
    db = next(get_db())
    try:
        return process_categorization_with_dependencies(db, batch_size)
    finally:
        db.close()


def process_categorization_with_dependencies(db: Session, batch_size: int) -> int:
    from ..repositories.categories_repository import CategoriesRepository
    
    transactions_repository = TransactionsRepository(db)
    categories_repository = CategoriesRepository(db)
    categorizer = TransactionCategorizer(categories_repository)
    
    categorization_service = TransactionCategorizationService(
        transactions_repository,
        categorizer,
    )
    
    return categorization_service.categorize_pending_transactions(batch_size)


def manually_trigger_categorization(batch_size: int = 10):
    return categorize_pending_transactions.delay(batch_size)
