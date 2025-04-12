import json
import logging
from datetime import date
from typing import Callable, List, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.encoders import jsonable_encoder

from ..logging.utils import log_exception
from ..models import Transaction
from ..repositories.transactions_repository import (
    TransactionsFilter,
    TransactionsRepository,
)
from ..routes.transactions_upload import TransactionUploader
from ..schemas import ColumnMapping, FileAnalysisResponse, FileUploadResponse
from ..schemas import Transaction as TransactionSchema
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
            processed_file = self.file_processor.process_file(file_content, filename)

            result = await self.transaction_uploader.upload_file(
                processed_file, auto_categorize
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
            processed_file = self.file_processor.process_file(file_content, filename)

            response = FileAnalysisResponse(
                source_id=processed_file.source_id,
                total_transactions=processed_file.statistics.total_transactions,
                total_amount=float(processed_file.statistics.total_amount),
                date_range_start=processed_file.statistics.date_range_start,
                date_range_end=processed_file.statistics.date_range_end,
                column_mappings=ColumnMapping(
                    **processed_file.conversion_model.column_map
                ),
                start_row=processed_file.conversion_model.start_row,
                file_id=processed_file.file_id,
                preview_rows=[t.dict() for t in processed_file.transactions[:5]],
            )
            logger_content.debug(
                jsonable_encoder(response),
                extra={"prefix": "file_processor.analyze_file.response", "ext": "json"},
            )

            return response

        except Exception as e:
            log_exception(f"Error analyzing file: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Error analyzing file: {str(e)}"
            )
