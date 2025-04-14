from datetime import date
from typing import List, Literal, Optional

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
    sub_category_id: Optional[int] = None
    categorization_status: Literal["pending", "categorized", "failed"] = "pending"
    normalized_description: Optional[str] = None


class Transaction(TransactionBase):
    id: int
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    category: Optional[Category] = None
    source: Optional[Source] = None
    categorization_status: Literal["pending", "categorized", "failed"] = "pending"
    normalized_description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    message: str
    transactions_processed: int
    transactions: List[Transaction]
    skipped_duplicates: int = 0
    categorization_task_id: Optional[str] = None


class ColumnMapping(BaseModel):
    date: str
    description: str
    amount: str
    debit_amount: Optional[str] = ""
    credit_amount: Optional[str] = ""
    amount_column: Optional[str] = ""
    currency: Optional[str] = ""
    balance: Optional[str] = ""


class FileAnalysisResponse(BaseModel):
    source_id: Optional[int] = None
    total_transactions: int
    total_amount: float
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    column_mappings: ColumnMapping
    start_row: int
    file_id: str
    preview_rows: List[dict] = []


class UploadFileSpec(BaseModel):
    statement_id: str
    column_mapping: ColumnMapping
    source_id: int
    start_row: int = 1
