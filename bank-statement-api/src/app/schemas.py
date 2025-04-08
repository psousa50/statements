from datetime import date
from typing import List, Optional, Literal

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    category_name: str
    parent_category_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    date: date
    description: str
    amount: float
    currency: str = "EUR"
    source_id: int


class TransactionCreate(TransactionBase):
    category_id: Optional[int] = None
    categorization_status: Literal["pending", "categorized", "failed"] = "pending"


class Transaction(TransactionBase):
    id: int
    category_id: Optional[int] = None
    category: Optional[Category] = None
    source: Optional[Source] = None
    categorization_status: Literal["pending", "categorized", "failed"] = "pending"

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    message: str
    transactions_processed: int
    transactions: List[Transaction]
    skipped_duplicates: int = 0
