from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..repositories.categories_repository import CategoriesRepository
from ..repositories.transactions_repository import TransactionsRepository
from ..services.transaction_categorizer import TransactionCategorizer
from ..services.transaction_categorization_service import (
    TransactionCategorizationService,
)
from ..tasks.categorization import manually_trigger_categorization

router = APIRouter(prefix="/categorization", tags=["categorization"])


@router.post("/trigger")
def trigger_categorization(batch_size: int = 10):
    task = manually_trigger_categorization(batch_size)
    return {"message": "Categorization process triggered", "task_id": task.id}


@router.get("/status/{task_id}")
def get_categorization_status(task_id: str):
    from ..celery_app import celery_app

    task = celery_app.AsyncResult(task_id)
    response = {"status": task.state}
    if task.state == "PENDING":
        response["message"] = "Task is pending"
    elif task.state == "FAILURE":
        response["message"] = str(task.info)
    else:
        response["result"] = task.result
    return response


@router.post("/process-now")
def process_categorization_now(batch_size: int = 100, db: Session = Depends(get_db)):
    categories_repository = CategoriesRepository(db)
    transactions_repository = TransactionsRepository(db)
    categorizer = TransactionCategorizer(categories_repository)
    categorization_service = TransactionCategorizationService(
        transactions_repository, categorizer
    )
    categorized_count = categorization_service.categorize_pending_transactions(
        batch_size
    )
    return {
        "message": "Categorization completed",
        "categorized_count": categorized_count,
    }
