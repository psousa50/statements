import io
from datetime import date
from typing import Callable, List, Optional

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from ..models import Transaction
from ..repositories.transactions_repository import (
    TransactionsFilter,
    TransactionsRepository,
)
from ..routes.transactions_upload import TransactionUploader
from ..schemas import FileUploadResponse
from ..schemas import Transaction as TransactionSchema


class TransactionRouter:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        transaction_uploader: TransactionUploader,
        on_change_callback: Optional[Callable[[str, List[Transaction]], None]] = None,
    ):
        self.router = APIRouter(
            prefix="/transactions",
            tags=["transactions"],
        )
        self.transaction_repository = transactions_repository
        self.transaction_uploader = transaction_uploader
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

    def _notify_change(self, action: str, transactions: List[Transaction]):
        if self.on_change_callback:
            self.on_change_callback(action, transactions)

    async def get_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        source_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ):
        filter = TransactionsFilter(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
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
    ):
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        transaction.category_id = category_id
        self.transaction_repository.update(transaction)

        self._notify_change("update", [transaction])

        return transaction

    async def upload_file(
        self,
        file: UploadFile = File(...),
        source_id: Optional[int] = Query(None),
    ):
        file_content = await file.read()
        file_format = self.detect_file_format(file.filename)
        df = self.parse_file(file_content, file_format)

        return await self.transaction_uploader.upload_file(df, source_id)

    def detect_file_format(self, filename):
        if filename.endswith(".csv"):
            return "csv"
        elif filename.endswith((".xls", ".xlsx")):
            return "excel"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload CSV or Excel files.",
            )

    def parse_file(self, file_content, file_format):
        try:
            if file_format == "csv":
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_format == "excel":
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format")

            return df
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
