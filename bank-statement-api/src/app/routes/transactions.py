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
from ..services.file_processing.file_analysis_service import FileAnalysisService
from ..services.file_processing.upload_file_service import UploadFileService, UploadFileSpec

logger_content = logging.getLogger("app.llm.big")
logger = logging.getLogger("app")


class TransactionRouter:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        transaction_uploader: TransactionUploader,
        file_analysis_service: FileAnalysisService,
        upload_file_service: UploadFileService,
        on_change_callback: Optional[Callable[[str, List[Transaction]], None]] = None,
    ):
        self.router = APIRouter(
            prefix="/transactions",
            tags=["transactions"],
        )
        self.transaction_repository = transactions_repository
        self.transaction_uploader = transaction_uploader
        self.file_analysis_service = file_analysis_service
        self.upload_file_service = upload_file_service
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
        spec: UploadFileSpec,
        auto_categorize: bool = Query(
            False, description="Automatically trigger categorization after upload"
        ),
    ):
        try:
            # Use the UploadFileService to process the file with the provided spec
            result = self.upload_file_service.upload_file(spec)
            
            # Trigger auto-categorization if requested
            if auto_categorize and result.transactions_processed > 0:
                from ..tasks.categorization import manually_trigger_categorization
                task = manually_trigger_categorization(batch_size=100)
                result.categorization_task_id = task.id
                result.message = "File processed successfully and categorization triggered"
            
            return result
        except Exception as e:
            log_exception(f"Error processing file: {str(e)}")
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
            # Use the FileAnalysisService to analyze the file
            response = self.file_analysis_service.analyze_file(file_content, filename)
            
            logger_content.debug(
                jsonable_encoder(response),
                extra={"prefix": "file_analysis_service.analyze_file.response", "ext": "json"},
            )

            return response

        except Exception as e:
            log_exception(f"Error analyzing file: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Error analyzing file: {str(e)}"
            )
