from typing import Callable
import asyncio

from ..celery_app import celery_app
from ..services.transaction_categorization_service import (
    TransactionCategorizationService,
)


class CategorizationTaskFactory:
    def __init__(self):
        self._service_factory = None

    def register_service_factory(
        self, factory: Callable[[], TransactionCategorizationService]
    ):
        self._service_factory = factory

    def get_service(self) -> TransactionCategorizationService:
        return self._service_factory()


categorization_factory = CategorizationTaskFactory()


@celery_app.task(name="src.app.tasks.categorization.categorize_pending_transactions")
def categorize_pending_transactions(batch_size: int = 10):
    service = categorization_factory.get_service()
    # Since the service method is async, we need to run it in an event loop
    return asyncio.run(service.categorize_pending_transactions(batch_size))


def manually_trigger_categorization(batch_size: int = 10):
    return categorize_pending_transactions.delay(batch_size)


def register_service_factory(factory: Callable[[], TransactionCategorizationService]):
    categorization_factory.register_service_factory(factory)
