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

models.Base.metadata.create_all(bind=engine)

def on_category_change(categorizer: TransactionCategorizer, action: str, changed_categories: list[models.Category]):
    categorizer.refresh_rules()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    categories_repository = CategoriesRepository(db)
    sources_repository = SourcesRepository(db)
    transactions_repository = TransactionsRepository(db)
    
    categorizer = TransactionCategorizer(categories_repository)
    
    upload_router = TransactionUploadRouter(
        transactions_repository =transactions_repository, 
        sources_repository =sources_repository,
        categorizer =categorizer
    )
    category_router = CategoryRouter(categories_repository, on_change_callback=lambda action, categories: on_category_change(categorizer, action, categories))
    source_router = SourceRouter(sources_repository)
    transaction_router = TransactionRouter(transactions_repository)
    
    app.include_router(category_router.router)
    app.include_router(transaction_router.router)
    app.include_router(upload_router.router)
    app.include_router(source_router.router)
    
    yield

app = FastAPI(
    title="Bank Statement API",
    description="API for processing and categorizing bank statements",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
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
