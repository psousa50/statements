from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import categories, transactions, upload, sources
from .db import engine
from . import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bank Statement API",
    description="API for processing and categorizing bank statements",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(upload.router)
app.include_router(sources.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Bank Statement API",
        "docs": "/docs",
        "endpoints": [
            {"path": "/categories", "methods": ["GET", "POST"]},
            {"path": "/transactions", "methods": ["GET"]},
            {"path": "/upload", "methods": ["POST"]},
            {"path": "/sources", "methods": ["GET", "POST"]},
        ]
    }
