from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..repositories.categories_repository import CategoriesRepository
from ..repositories.transactions_repository import TransactionsRepository
from ..services.categorizer import TransactionCategorizer
from ..services.transaction_categorization_service import TransactionCategorizationService
from ..tasks.categorization import manually_trigger_categorization

router = APIRouter(
    prefix="/categorization",
    tags=["categorization"],
)


@router.post("/trigger")
def trigger_categorization(batch_size: int = 10):
    """
    Trigger the categorization process for pending transactions
    
    Args:
        batch_size: Maximum number of transactions to process in one batch
        
    Returns:
        Message indicating that categorization has been triggered
    """
    task = manually_trigger_categorization(batch_size)
    return {"message": "Categorization process triggered", "task_id": task.id}


@router.get("/status/{task_id}")
def get_categorization_status(task_id: str):
    """
    Get the status of a categorization task
    
    Args:
        task_id: ID of the categorization task
        
    Returns:
        Status of the categorization task
    """
    from ..celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'status': task.state,
            'message': 'Task is pending'
        }
    elif task.state == 'FAILURE':
        response = {
            'status': task.state,
            'message': str(task.info)
        }
    else:
        response = {
            'status': task.state,
            'result': task.result
        }
    
    return response


@router.post("/process-now")
def process_categorization_now(
    batch_size: int = 100,
    db: Session = Depends(get_db)
):
    """
    Process categorization immediately without using Celery
    
    Args:
        batch_size: Maximum number of transactions to process in one batch
        db: Database session
        
    Returns:
        Number of transactions categorized
    """
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
    
    return {"message": "Categorization completed", "categorized_count": categorized_count}
