from sqlalchemy.orm import Session

from ..celery_app import celery_app
from ..db import get_db
from ..repositories.categories_repository import CategoriesRepository
from ..repositories.transactions_repository import TransactionsRepository
from ..services.categorizer import TransactionCategorizer
from ..services.transaction_categorization_service import TransactionCategorizationService


@celery_app.task(name="src.app.tasks.categorization.categorize_pending_transactions")
def categorize_pending_transactions(batch_size: int = 10):
    """
    Celery task to categorize pending transactions
    
    Args:
        batch_size: Maximum number of transactions to process in one batch
        
    Returns:
        Number of transactions categorized
    """
    # Create a new database session
    db = next(get_db())
    
    try:
        # Initialize repositories and services
        categories_repository = CategoriesRepository(db)
        transactions_repository = TransactionsRepository(db)
        categorizer = TransactionCategorizer(categories_repository)
        
        # Create categorization service
        categorization_service = TransactionCategorizationService(
            transactions_repository, 
            categorizer
        )
        
        # Process pending transactions
        categorized_count = categorization_service.categorize_pending_transactions(batch_size)
        
        return categorized_count
    finally:
        # Close the database session
        db.close()


def manually_trigger_categorization(batch_size: int = 10):
    return categorize_pending_transactions.delay(batch_size)
