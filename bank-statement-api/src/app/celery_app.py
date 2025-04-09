from celery import Celery

REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "bank_statement_api",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.categorization"],
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_expires = 3600

celery_app.conf.beat_schedule = {
    "categorize-transactions-every-1-minute": {
        "task": "src.app.tasks.categorization.categorize_pending_transactions",
        "schedule": 60 * 1,
        "args": (10,),
    },
}
