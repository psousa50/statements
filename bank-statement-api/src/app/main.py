from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .db import engine, get_db
from .repositories.categories_repository import CategoriesRepository
from .repositories.sources_repository import SourcesRepository
from .repositories.transactions_repository import TransactionsRepository
from .routes.categories import CategoryRouter
from .routes.sources import SourceRouter
from .routes.transactions import TransactionRouter
from .routes.transactions_upload import TransactionUploader
from .services.categorizer import TransactionCategorizer

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
        self.app = FastAPI(
            title="Bank Statement API",
            description="API for processing and categorizing bank statements",
            version="0.1.0"
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
            def override_get_db():
                try:
                    yield db
                finally:
                    pass
            self.app.dependency_overrides[get_db] = override_get_db
        
        self.categories_repository = categories_repository or CategoriesRepository(db)
        self.sources_repository = sources_repository or SourcesRepository(db)
        self.transactions_repository = transactions_repository or TransactionsRepository(db)
        
        self.categorizer = categorizer or TransactionCategorizer(self.categories_repository)
        
        def on_category_change(action, categories):
            self.categorizer.refresh_rules()
        
        category_router = CategoryRouter(
            self.categories_repository, 
            on_change_callback=on_category_change
        )
        source_router = SourceRouter(self.sources_repository)
        transaction_uploader = TransactionUploader(
            transactions_repository=self.transactions_repository,
            sources_repository=self.sources_repository,
            categorizer=self.categorizer
        )
        transaction_router = TransactionRouter(
            self.transactions_repository, 
            transaction_uploader=transaction_uploader,
        )
        
        self.app.include_router(category_router.router)
        self.app.include_router(source_router.router)
        self.app.include_router(transaction_router.router)
        
        @self.app.get("/")
        def read_root():
            return {
                "message": "Welcome to the Bank Statement API",
                "docs": "/docs",
                "endpoints": [
                    {"path": "/categories", "methods": ["GET", "POST"]},
                    {"path": "/transactions", "methods": ["GET", "POST"]},
                    {"path": "/sources", "methods": ["GET", "POST", "PUT", "DELETE"]},
                ]
            }

# Create the default app instance
app_instance = App()
app = app_instance.app
