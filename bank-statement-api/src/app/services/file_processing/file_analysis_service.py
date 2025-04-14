import hashlib
import logging
from typing import Dict, List, Optional

import pandas as pd

from src.app.schemas import ColumnMapping, FileAnalysisResponse
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_type_detector import FileType, FileTypeDetector
from src.app.services.file_processing.statement_statistics_calculator import StatementStatisticsCalculator
from src.app.services.file_processing.transactions_builder import StatementTransaction, TransactionsBuilder
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner

logger = logging.getLogger("app")


class StatementSchemaRepository:
    def find_by_column_hash(self, column_hash: str):
        pass

    def save(self, schema):
        pass


class StatementRepository:
    def save(self, file_content: bytes, file_name: str) -> str:
        pass


class ParserFactory:
    def create_parser(self, file_type: FileType):
        pass


class FileAnalysisService:
    def __init__(
        self,
        file_type_detector: FileTypeDetector,
        parser_factory: ParserFactory,
        column_normalizer: ColumnNormalizer,
        transaction_cleaner: TransactionsCleaner,
        transactions_builder: TransactionsBuilder,
        statistics_calculator: StatementStatisticsCalculator,
        statement_repository: StatementRepository,
        statement_schema_repository: StatementSchemaRepository,
    ):
        self.file_type_detector = file_type_detector
        self.parser_factory = parser_factory
        self.column_normalizer = column_normalizer
        self.transaction_cleaner = transaction_cleaner
        self.transactions_builder = transactions_builder
        self.statistics_calculator = statistics_calculator
        self.statement_repository = statement_repository
        self.statement_schema_repository = statement_schema_repository

    def analyze_file(self, file_content: bytes, file_name: str) -> FileAnalysisResponse:
        try:
            # Step 1: Save the uploaded file to the database
            statement_id = self.statement_repository.save(file_content, file_name)
            
            # Step 2: Detect file type and parse the file
            file_type = self.file_type_detector.detect_file_type(file_name)
            parser = self.parser_factory.create_parser(file_type)
            df = parser.parse(file_content)
            
            # Step 3: Normalize columns
            conversion_model = self.column_normalizer.normalize_columns(df)
            
            # Step 4: Calculate column hash
            column_hash = self._calculate_column_hash(df.columns.tolist())
            
            # Step 5: Look for existing schema
            existing_schema = self.statement_schema_repository.find_by_column_hash(column_hash)
            source_id = None
            
            if existing_schema:
                # Use existing schema
                source_id = existing_schema.source_id
            else:
                # Create new schema if none exists
                self.statement_schema_repository.save({
                    "column_hash": column_hash,
                    "column_mapping": conversion_model.column_map,
                    "file_type": file_type,
                })
            
            # Step 6: Clean transactions
            cleaned_df = self.transaction_cleaner.clean(df, conversion_model)
            
            # Step 7: Build transactions
            transactions = self.transactions_builder.build_transactions(cleaned_df)
            
            # Step 8: Calculate statistics
            statistics = self.statistics_calculator.calc_statistics(transactions)
            
            # Step 9: Prepare preview rows (first 10)
            preview_rows = self._prepare_preview_rows(transactions[:10])
            
            # Step 10: Create response
            response = FileAnalysisResponse(
                source_id=source_id,
                total_transactions=statistics.total_transactions,
                total_amount=float(statistics.total_amount),
                date_range_start=statistics.date_range_start,
                date_range_end=statistics.date_range_end,
                column_mappings=ColumnMapping(**conversion_model.column_map),
                start_row=conversion_model.start_row,
                file_id=statement_id,
                preview_rows=preview_rows,
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}")
            raise ValueError(f"Error analyzing file: {str(e)}")
    
    def _calculate_column_hash(self, columns: List[str]) -> str:
        columns_str = ",".join(sorted(columns))
        return hashlib.sha256(columns_str.encode()).hexdigest()
    
    def _prepare_preview_rows(self, transactions: List[StatementTransaction]) -> List[Dict]:
        return [transaction.model_dump() for transaction in transactions]
