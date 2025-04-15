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


class StatementSchema(BaseModel):
    id: str
    source_id: Optional[int] = None
    file_type: str
    column_mapping: ColumnMapping
    column_names: List[str] = []
    start_row: int = 1
    header_row: int = 0

    model_config = ConfigDict(from_attributes=True)


class FileAnalysisResponse(BaseModel):
    statement_schema: StatementSchema
    preview_rows: List[List[str]] = []
    total_transactions: int
    total_amount: float
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    file_id: str


class UploadFileSpec(BaseModel):
    statement_id: str
    statement_schema: StatementSchema

    # For backward compatibility
    @property
    def column_mapping(self) -> ColumnMapping:
        return self.statement_schema.column_mapping

    @property
    def source_id(self) -> Optional[int]:
        return self.statement_schema.source_id

    # For backward compatibility with code that uses schema
    @property
    def schema(self) -> StatementSchema:
        return self.statement_schema

    # For backward compatibility with code that uses start_row
    @property
    def start_row(self) -> int:
        return self.statement_schema.start_row
