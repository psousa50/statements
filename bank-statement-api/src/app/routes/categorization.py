from fastapi import APIRouter

from ..repositories.categories_repository import CategoriesRepository
from ..repositories.transactions_repository import TransactionsRepository
from ..services.categorizers.transaction_categorizer import TransactionCategorizer
from ..services.transaction_categorization_service import (
    TransactionCategorizationService,
)
from ..tasks.categorization import manually_trigger_categorization


class CategorizationRouter:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        categories_repository: CategoriesRepository,
        categorizer: TransactionCategorizer,
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

        self.transactions_repository = transactions_repository
        self.categories_repository = categories_repository
        self.categorizer = categorizer

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

    async def process_categorization_now(self):
        categorization_service = TransactionCategorizationService(
            self.categories_repository,
            self.transactions_repository,
            self.categorizer,
        )

        batch_size = 100
        categorized_count = (
            await categorization_service.categorize_pending_transactions(batch_size)
        )

        return {
            "message": "Categorization completed",
            "categorized_count": categorized_count,
        }
