import json
import logging
import uuid
from datetime import date
from typing import Callable, List, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.encoders import jsonable_encoder

from ..models import Transaction
from ..repositories.transactions_repository import (
    TransactionsFilter,
    TransactionsRepository,
)
from ..routes.transactions_upload import TransactionUploader
from ..schemas import ColumnMapping, FileAnalysisResponse, FileUploadResponse
from ..schemas import Transaction as TransactionSchema
from ..services.file_processing.conversion_model import ConversionModel
from ..services.file_processing.file_processor import FileProcessor

logger_content = logging.getLogger("app.llm.big")
logger = logging.getLogger("app")


class TransactionRouter:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        transaction_uploader: TransactionUploader,
        file_processor: FileProcessor,
        on_change_callback: Optional[Callable[[str, List[Transaction]], None]] = None,
    ):
        self.router = APIRouter(
            prefix="/transactions",
            tags=["transactions"],
        )
        self.transaction_repository = transactions_repository
        self.transaction_uploader = transaction_uploader
        self.file_processor = file_processor
        self.on_change_callback = on_change_callback

        self.router.add_api_route(
            "",
            self.get_transactions,
            methods=["GET"],
            response_model=List[TransactionSchema],
        )
        self.router.add_api_route(
            "/{transaction_id}",
            self.get_transaction,
            methods=["GET"],
            response_model=TransactionSchema,
        )
        self.router.add_api_route(
            "/{transaction_id}/categorize",
            self.categorize_transaction,
            methods=["PUT"],
            response_model=TransactionSchema,
        )
        self.router.add_api_route(
            "/upload",
            self.upload_file,
            methods=["POST"],
            response_model=FileUploadResponse,
        )
        self.router.add_api_route(
            "/analyze",
            self.analyze_file,
            methods=["POST"],
            response_model=FileAnalysisResponse,
        )

    def _notify_change(self, action: str, transactions: List[Transaction]):
        if self.on_change_callback:
            self.on_change_callback(action, transactions)

    async def get_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        sub_category_id: Optional[int] = None,
        source_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ):
        filter = TransactionsFilter(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            sub_category_id=sub_category_id,
            source_id=source_id,
            search=search,
        )
        transactions = self.transaction_repository.get_all(
            filter, skip=skip, limit=limit
        )
        return transactions

    async def get_transaction(
        self,
        transaction_id: int,
    ):
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction

    async def categorize_transaction(
        self,
        transaction_id: int,
        category_id: int,
        sub_category_id: Optional[int] = None,
    ):
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        transaction.category_id = category_id
        transaction.sub_category_id = sub_category_id
        self.transaction_repository.update(transaction)

        self._notify_change("update", [transaction])

        return transaction

    async def upload_file(
        self,
        file: UploadFile = File(...),
        source_id: Optional[int] = Query(None),
        auto_categorize: bool = Query(
            False, description="Automatically trigger categorization after upload"
        ),
    ):
        file_content = await file.read()
        filename = file.filename

        try:
            df, conversion_model = self.file_processor.process_file(
                file_content, filename
            )
            df.columns = conversion_model.column_map.keys()

            result = await self.transaction_uploader.upload_file(
                df, source_id, auto_categorize
            )

            return result
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error processing file: {str(e)}"
            )

    async def analyze_file(
        self,
        file: UploadFile = File(...),
    ):
        file_content = await file.read()
        filename = file.filename

        try:
            df, conversion_model = self.file_processor.process_file(
                file_content, filename
            )

            file_id = str(uuid.uuid4())

            total_amount = 0
            if "amount" in df.columns:
                numeric_amounts = pd.to_numeric(df["amount"], errors="coerce")
                total_amount = float(numeric_amounts.sum(skipna=True))

            date_range_start = None
            date_range_end = None
            if "date" in df.columns and not df["date"].empty:
                dates = pd.to_datetime(df["date"], errors="coerce")
                valid_dates = dates.dropna()
                if not valid_dates.empty:
                    date_range_start = valid_dates.min().date()
                    date_range_end = valid_dates.max().date()

            preview_rows = []
            for _, row in df.head(10).iterrows():
                row_dict = row.to_dict()
                for key, value in row_dict.items():
                    if isinstance(value, (np.float64, np.float32)):
                        if np.isnan(value):
                            row_dict[key] = None
                        else:
                            row_dict[key] = float(value)
                    if isinstance(value, (np.int64, np.int32)):
                        if np.isnan(value):
                            row_dict[key] = None
                        else:
                            row_dict[key] = int(value)
                preview_rows.append(row_dict)

            source = None

            column_mapping_dict = {
                "date": conversion_model.column_map.get("date", ""),
                "description": conversion_model.column_map.get("description", ""),
                "amount": conversion_model.column_map.get("amount", ""),
                "debit_amount": conversion_model.column_map.get("debit_amount", ""),
                "credit_amount": conversion_model.column_map.get("credit_amount", ""),
                "amount_column": conversion_model.column_map.get("amount_column", ""),
                "currency": conversion_model.column_map.get("currency", ""),
                "balance": conversion_model.column_map.get("balance", ""),
            }

            logger_content.debug(
                df.head(5).to_dict(orient="records"),
                extra={"prefix": "file_processor.preview", "ext": "json"},
            )

            rename_dict = {
                col: std_col
                for std_col, col in conversion_model.column_map.items()
                if col and col in df.columns
            }
            df = df.rename(columns=rename_dict)

            logger_content.debug(
                json.dumps(column_mapping_dict),
                extra={"prefix": "file_processor.column_mapping", "ext": "json"},
            )

            logger_content.debug(
                df.head(5).to_dict(orient="records"),
                extra={
                    "prefix": "file_processor.preview_after_renaming",
                    "ext": "json",
                },
            )

            response = FileAnalysisResponse(
                source=source,
                total_transactions=len(df),
                total_amount=float(total_amount),
                date_range_start=date_range_start,
                date_range_end=date_range_end,
                column_mappings=ColumnMapping(**column_mapping_dict),
                start_row=conversion_model.start_row,
                file_id=file_id,
                preview_rows=df.head(5)
                .replace({np.nan: None})
                .astype(object)
                .to_dict(orient="records"),
            )
            logger_content.debug(
                json.dumps(jsonable_encoder(response)),
                extra={"prefix": "file_processor.analyze_file.response", "ext": "json"},
            )

            return response

        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Error analyzing file: {str(e)}"
            )
