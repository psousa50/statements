from celery import Celery

celery_app = Celery(
    "bank_statement_api",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks.categorization"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "categorize-transactions-every-15-minutes": {
        "task": "src.app.tasks.categorization.categorize_pending_transactions",
        "schedule": 60 * 15,  # Every 15 minutes
        "args": (100,),  # Process 100 transactions at a time
    },
}
