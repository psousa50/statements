from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .routes.categories import CategoryRouter
from .routes.sources import SourceRouter
from .routes.transactions import TransactionRouter
from .routes.upload import TransactionUploadRouter
from .db import engine, get_db
from . import models
from .services.categorizer import TransactionCategorizer
from .repositories.categories_repository import CategoriesRepository
from .repositories.sources_repository import SourcesRepository
from .repositories.transactions_repository import TransactionsRepository

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

class App:
    def __init__(
        self, 
        db_session=None, 
        categories_repository=None, 
        sources_repository=None, 
        transactions_repository=None, 
        categorizer=None
    ):
        # Create the FastAPI app
        self.app = FastAPI(
            title="Bank Statement API",
            description="API for processing and categorizing bank statements",
            version="0.1.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # If no session is provided, use the default get_db
        if db_session is None:
            db = next(get_db())
            # We don't override the get_db dependency in this case
        else:
            db = db_session
            # Override the get_db dependency
            def override_get_db():
                try:
                    yield db
                finally:
                    pass
            self.app.dependency_overrides[get_db] = override_get_db
        
        # Create repositories if not provided
        self.categories_repository = categories_repository or CategoriesRepository(db)
        self.sources_repository = sources_repository or SourcesRepository(db)
        self.transactions_repository = transactions_repository or TransactionsRepository(db)
        
        # Create categorizer if not provided
        self.categorizer = categorizer or TransactionCategorizer(self.categories_repository)
        
        # Setup callback for category changes
        def on_category_change(action, categories):
            self.categorizer.refresh_rules()
        
        # Create and include routers
        category_router = CategoryRouter(
            self.categories_repository, 
            on_change_callback=on_category_change
        )
        source_router = SourceRouter(self.sources_repository)
        transaction_router = TransactionRouter(self.transactions_repository)
        upload_router = TransactionUploadRouter(
            transactions_repository=self.transactions_repository,
            sources_repository=self.sources_repository,
            categorizer=self.categorizer
        )
        
        self.app.include_router(category_router.router)
        self.app.include_router(source_router.router)
        self.app.include_router(transaction_router.router)
        self.app.include_router(upload_router.router)
        
        # Add a root endpoint
        @self.app.get("/")
        def read_root():
            return {
                "message": "Welcome to the Bank Statement API",
                "docs": "/docs",
                "endpoints": [
                    {"path": "/categories", "methods": ["GET", "POST"]},
                    {"path": "/transactions", "methods": ["GET"]},
                    {"path": "/upload", "methods": ["POST"]},
                    {"path": "/sources", "methods": ["GET", "POST", "PUT", "DELETE"]},
                ]
            }

# Create the default app instance
app_instance = App()
app = app_instance.app
