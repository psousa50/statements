from datetime import date
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class RequestModel(CamelModel):
    pass


class ResponseModel(CamelModel):
    pass


class CategoryBase(ResponseModel):
    category_name: str
    parent_category_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SourceBase(ResponseModel):
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionBase(ResponseModel):
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


class FileUploadResponse(ResponseModel):
    message: str
    transactions_processed: int
    transactions: List[Transaction]
    skipped_duplicates: int = 0
    categorization_task_id: Optional[str] = None


class ColumnMapping(ResponseModel):
    date: str
    description: str
    amount: str
    debit_amount: Optional[str] = ""
    credit_amount: Optional[str] = ""
    currency: Optional[str] = ""
    balance: Optional[str] = ""


class StatementSchemaDefinition(RequestModel, ResponseModel):
    id: str
    source_id: Optional[int] = None
    file_type: str
    column_mapping: ColumnMapping
    start_row: int = 1
    header_row: int = 0

    model_config = ConfigDict(from_attributes=True)


class StatementAnalysisRequest(RequestModel):
    file_content: bytes
    file_name: str


class StatementAnalysisResponse(ResponseModel):
    statement_id: str
    statement_schema: StatementSchemaDefinition
    total_transactions: int
    total_amount: float
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    preview_rows: List[List[str]] = []


class UploadFileSpec(RequestModel, ResponseModel):
    statement_id: str
    statement_schema: StatementSchemaDefinition


class StatementTransaction(BaseModel):
    date: date
    description: str
    amount: Decimal
    currency: str


class UploadStatementRequest(RequestModel):
    statement_id: str
    statement_schema: StatementSchemaDefinition
