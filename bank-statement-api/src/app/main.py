from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .routes import categories, transactions, sources
from .routes.categories import CategoryRouter
from .routes.upload import UploadRouter
from .db import engine, get_db
from . import models
from .services.categorizer import TransactionCategorizer

models.Base.metadata.create_all(bind=engine)

# Create a dependency for the categorizer
def get_categorizer(db: Session = Depends(get_db)):
    return TransactionCategorizer(db)

# Create a function to handle category changes
def on_category_change(categorizer: TransactionCategorizer, action: str, changed_categories: list[models.Category]):
    categorizer.refresh_rules()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize services and routers
    
    # Create the upload router with dependency injection
    upload_router = UploadRouter(get_categorizer)
    
    # Create the category router with a callback that uses the categorizer
    category_router = CategoryRouter(
        on_change_callback=lambda action, categories: on_category_change(get_categorizer(next(get_db())), action, categories)
    )
    
    # Include all routers
    app.include_router(category_router.router)
    app.include_router(transactions.router)
    app.include_router(upload_router.router)
    app.include_router(sources.router)
    
    yield
    
    # Shutdown: cleanup resources if needed
    # No cleanup needed for now

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
