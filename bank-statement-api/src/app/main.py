import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.app.services.categorizers.existing_transactions_categorizer import (
    ExistingTransactionsCategorizer,
)
from src.app.services.file_processing.statement_statistics_calculator import (
    StatementStatisticsCalculator,
)
from src.app.services.file_processing.transactions_builder import TransactionsBuilder

from .ai.gemini_ai import GeminiAI
from .db import get_db
from .logging.config import init_logging
from .repositories.categories_repository import CategoriesRepository
from .repositories.sources_repository import SourcesRepository
from .repositories.statement_repository import StatementRepository
from .repositories.statement_schema_repository import StatementSchemaRepository
from .repositories.transactions_repository import TransactionsRepository
from .routes.categories import CategoryRouter
from .routes.categorization import CategorizationRouter
from .routes.sources import SourceRouter
from .routes.transactions import TransactionRouter
from .services.categorizers.llm_transaction_categorizer import LLMTransactionCategorizer
from .services.categorizers.transaction_categorizer import TransactionCategorizer
from .services.file_processing.column_normalizer import ColumnNormalizer
from .services.file_processing.file_type_detector import FileTypeDetector
from .services.file_processing.parsers.parser_factory import ParserFactory
from .services.file_processing.statement_analysis_service import (
    StatementAnalysisService,
)
from .services.file_processing.statement_upload_service import StatementUploadService
from .services.file_processing.transactions_cleaner import TransactionsCleaner

init_logging()
logger = logging.getLogger("app")


class App:
    def __init__(
        self,
        db_session: Optional[Session] = None,
        categories_repository: Optional[CategoriesRepository] = None,
        sources_repository: Optional[SourcesRepository] = None,
        transactions_repository: Optional[TransactionsRepository] = None,
        statement_repository: Optional[StatementRepository] = None,
        statement_schema_repository: Optional[StatementSchemaRepository] = None,
        categorizer: Optional[TransactionCategorizer] = None,
    ):
        logger.info("Initializing app...")

        self.app = FastAPI(
            title="Bank Statement API",
            description="API for processing and categorizing bank statements",
            version="0.1.0",
        )

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        if db_session is None:
            db = next(get_db())
        else:
            db = db_session

        self.categories_repository = categories_repository or CategoriesRepository(db)
        self.sources_repository = sources_repository or SourcesRepository(db)
        self.transactions_repository = (
            transactions_repository or TransactionsRepository(db)
        )
        self.statement_repository = statement_repository or StatementRepository(db)
        self.statement_schema_repository = (
            statement_schema_repository or StatementSchemaRepository(db)
        )

        llm_client = GeminiAI()
        groq_categorizer = categorizer or LLMTransactionCategorizer(
            self.categories_repository, llm_client
        )

        self.categorizer = ExistingTransactionsCategorizer(
            transactions_repository=self.transactions_repository,
            fallback_categorizer=groq_categorizer,
        )

        def on_category_change(action, categories):
            self.categorizer.refresh_rules()

        category_router = CategoryRouter(
            self.categories_repository, on_change_callback=on_category_change
        )
        source_router = SourceRouter(self.sources_repository)
        file_type_detector = FileTypeDetector()
        column_normalizer = ColumnNormalizer(llm_client)
        transaction_cleaner = TransactionsCleaner()
        transactions_builder = TransactionsBuilder()
        statistics_calculator = StatementStatisticsCalculator()
        parser_factory = ParserFactory()
        statement_analysis_service = StatementAnalysisService(
            file_type_detector=file_type_detector,
            parser_factory=parser_factory,
            column_normalizer=column_normalizer,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statistics_calculator=statistics_calculator,
            statement_repository=self.statement_repository,
            statement_schema_repository=self.statement_schema_repository,
        )
        statement_upload_service = StatementUploadService(
            parser_factory=parser_factory,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statement_repository=self.statement_repository,
            transactions_repository=self.transactions_repository,
            statement_schema_repository=self.statement_schema_repository,
        )
        transaction_router = TransactionRouter(
            transactions_repository=self.transactions_repository,
            statement_analysis_service=statement_analysis_service,
            statement_upload_service=statement_upload_service,
            statement_repository=self.statement_repository,
        )
        categorization_router = CategorizationRouter(
            transactions_repository=self.transactions_repository,
            categories_repository=self.categories_repository,
            categorizer=self.categorizer,
        )

        self.app.include_router(category_router.router)
        self.app.include_router(source_router.router)
        self.app.include_router(transaction_router.router)
        self.app.include_router(categorization_router.router)

        @self.app.get("/")
        def read_root():
            return {
                "message": "Welcome to the Bank Statement API",
                "docs": "/docs",
                "endpoints": [
                    {"path": "/categories", "methods": ["GET", "POST"]},
                    {"path": "/transactions", "methods": ["GET", "POST"]},
                    {"path": "/sources", "methods": ["GET", "POST", "PUT", "DELETE"]},
                    {"path": "/categorization", "methods": ["POST", "GET"]},
                ],
            }


# Create the default app instance
def create_default_app():
    app_instance = App()
    return app_instance.app


# Only create the app when this module is run directly, not when imported
app = create_default_app()
