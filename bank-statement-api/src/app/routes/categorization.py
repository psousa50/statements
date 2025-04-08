from fastapi import APIRouter
from typing import Optional

from ..repositories.categories_repository import CategoriesRepository
from ..repositories.transactions_repository import TransactionsRepository
from ..services.transaction_categorizer import TransactionCategorizer
from ..services.transaction_categorization_service import (
    TransactionCategorizationService,
)
from ..tasks.categorization import manually_trigger_categorization


class CategorizationRouter:
    def __init__(
        self,
        transactions_repository: Optional[TransactionsRepository] = None,
        categories_repository: Optional[CategoriesRepository] = None,
    ):
        self.router = APIRouter(
            prefix="/categorization",
            tags=["categorization"],
        )
        
        # Register routes
        self.router.add_api_route(
            "/trigger",
            self.trigger_categorization,
            methods=["POST"],
        )
        self.router.add_api_route(
            "/status/{task_id}",
            self.get_categorization_status,
            methods=["GET"],
        )
        self.router.add_api_route(
            "/process-now",
            self.process_categorization_now,
            methods=["POST"],
        )
        
        # Initialize repositories if provided
        self.transactions_repository = transactions_repository
        self.categories_repository = categories_repository
        
    async def trigger_categorization(self, batch_size: int = 10):
        task = manually_trigger_categorization(batch_size)
        return {"message": "Categorization process triggered", "task_id": task.id}
    
    async def get_categorization_status(self, task_id: str):
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
    
    async def process_categorization_now(self, batch_size: int = 10):
        categorizer = TransactionCategorizer(self.categories_repository)
        categorization_service = TransactionCategorizationService(
            self.transactions_repository, categorizer
        )
        
        categorized_count = categorization_service.categorize_pending_transactions(
            batch_size
        )
        
        return {
            "message": "Categorization completed",
            "categorized_count": categorized_count,
        }


router = CategorizationRouter().router
