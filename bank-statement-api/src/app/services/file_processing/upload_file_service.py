import logging
from typing import Dict, List, Optional

import pandas as pd

from src.app.schemas import ColumnMapping, FileUploadResponse, UploadFileSpec, TransactionCreate
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_type_detector import FileType
from src.app.services.file_processing.transactions_builder import StatementTransaction, TransactionsBuilder
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner

logger = logging.getLogger("app")


class StatementRepository:
    def get_by_id(self, statement_id: str) -> Dict:
        pass


class TransactionsRepository:
    def find_duplicates(self, transactions: List[StatementTransaction]) -> List[StatementTransaction]:
        pass
    
    def create_many(self, transactions: List[TransactionCreate]) -> List:
        pass


class ParserFactory:
    def create_parser(self, file_type: FileType):
        pass


class UploadFileService:
    def __init__(
        self,
        parser_factory: ParserFactory,
        transaction_cleaner: TransactionsCleaner,
        transactions_builder: TransactionsBuilder,
        statement_repository: StatementRepository,
        transactions_repository: TransactionsRepository,
    ):
        self.parser_factory = parser_factory
        self.transaction_cleaner = transaction_cleaner
        self.transactions_builder = transactions_builder
        self.statement_repository = statement_repository
        self.transactions_repository = transactions_repository

    def upload_file(self, spec: UploadFileSpec) -> FileUploadResponse:
        try:
            # Step 1: Load file content from the statements table
            statement = self.statement_repository.get_by_id(spec.statement_id)
            file_content = statement["content"]
            file_name = statement["file_name"]
            
            # Step 2: Determine file type and parse file
            file_type = self._determine_file_type(file_name)
            parser = self.parser_factory.create_parser(file_type)
            df = parser.parse(file_content)
            
            # Step 3: Create conversion model from the provided column mapping
            conversion_model = self._create_conversion_model(spec.column_mapping, spec.start_row)
            
            # Step 4: Clean transactions
            cleaned_df = self.transaction_cleaner.clean(df, conversion_model)
            
            # Step 5: Build transaction objects
            transactions = self.transactions_builder.build_transactions(cleaned_df)
            
            # Step 6: Check for duplicates
            duplicates = self.transactions_repository.find_duplicates(transactions)
            unique_transactions = [t for t in transactions if t not in duplicates]
            
            # Step 7: Create transaction records
            transaction_creates = self._create_transaction_models(unique_transactions, spec.source_id)
            created_transactions = self.transactions_repository.create_many(transaction_creates)
            
            # Step 8: Prepare response
            response = FileUploadResponse(
                message="File processed successfully",
                transactions_processed=len(unique_transactions),
                transactions=created_transactions,
                skipped_duplicates=len(duplicates),
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise ValueError(f"Error uploading file: {str(e)}")
    
    def _determine_file_type(self, file_name: str) -> FileType:
        extension = file_name.split(".")[-1].lower()
        if extension == "csv":
            return FileType.CSV
        elif extension in ["xlsx", "xls"]:
            return FileType.EXCEL
        elif extension == "pdf":
            return FileType.PDF
        else:
            return FileType.UNKNOWN
    
    def _create_conversion_model(self, column_mapping: ColumnMapping, start_row: int) -> ConversionModel:
        column_map = column_mapping.model_dump()
        return ConversionModel(
            column_map=column_map,
            header_row=0,  # Assuming header is always the first row
            start_row=start_row
        )
    
    def _create_transaction_models(
        self, transactions: List[StatementTransaction], source_id: int
    ) -> List[TransactionCreate]:
        return [
            TransactionCreate(
                date=transaction.date,
                description=transaction.description,
                amount=float(transaction.amount),
                currency=transaction.currency,
                source_id=source_id,
                category_id=None,
                categorization_status="pending",
                normalized_description=self._normalize_description(transaction.description)
            )
            for transaction in transactions
        ]
    
    def _normalize_description(self, description: str) -> str:
        import re
        
        if not description:
            return ""
            
        description = str(description).lower()
        description = re.sub(r"[^\w\s]", " ", description)
        description = re.sub(r"\s+", " ", description).strip()
        
        return description
