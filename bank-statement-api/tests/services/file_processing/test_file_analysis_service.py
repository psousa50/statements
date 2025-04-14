import uuid
from datetime import date
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.app.schemas import FileAnalysisResponse, ColumnMapping
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_analysis_service import FileAnalysisService
from src.app.services.file_processing.file_type_detector import FileType, FileTypeDetector
from src.app.services.file_processing.transactions_builder import StatementTransaction, TransactionsBuilder
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner
from src.app.services.file_processing.statement_statistics_calculator import StatementStatisticsCalculator


class TestFileAnalysisService:
    def test_analyze_file(self):
        # Arrange
        # Sample data for testing
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
            "Currency": ["EUR", "EUR"],
            "Balance": [1000.00, 950.00],
        }
        df = pd.DataFrame(data)
        file_content = df.to_csv(index=False).encode("utf-8")
        file_name = "sample.csv"
        
        # Mock dependencies
        file_type_detector = MagicMock()
        file_type_detector.detect_file_type.return_value = FileType.CSV
        
        statement_parser = MagicMock()
        statement_parser.parse.return_value = df
        
        parser_factory = MagicMock()
        parser_factory.create_parser.return_value = statement_parser
            
        # Mock column normalizer
        column_normalizer = MagicMock()
        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance"
            },
            header_row=0,
            start_row=1
        )
        column_normalizer.normalize_columns.return_value = conversion_model
        
        # Mock transaction cleaner
        transaction_cleaner = MagicMock()
        cleaned_df = df.copy()
        transaction_cleaner.clean.return_value = cleaned_df
        
        # Mock transactions builder
        transactions_builder = MagicMock()
        transactions = [
            StatementTransaction(
                date=date(2023, 1, 1),
                description="Salary",
                amount=1000.00,
                currency="EUR"
            ),
            StatementTransaction(
                date=date(2023, 1, 2),
                description="Groceries",
                amount=-50.00,
                currency="EUR"
            )
        ]
        transactions_builder.build_transactions.return_value = transactions
        
        # Mock statistics calculator
        statistics_calculator = MagicMock()
        statistics = MagicMock()
        statistics.total_transactions = 2
        statistics.total_amount = 950.00
        statistics.date_range_start = date(2023, 1, 1)
        statistics.date_range_end = date(2023, 1, 2)
        statistics_calculator.calc_statistics.return_value = statistics
        
        # Mock statement repository
        statement_repository = MagicMock()
        statement_id = str(uuid.uuid4())
        statement_repository.save.return_value = statement_id
        
        # Mock statement schema repository
        statement_schema_repository = MagicMock()
        statement_schema_repository.find_by_column_hash.return_value = None
        
        # Create service under test
        service = FileAnalysisService(
            file_type_detector=file_type_detector,
            parser_factory=parser_factory,
            column_normalizer=column_normalizer,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statistics_calculator=statistics_calculator,
            statement_repository=statement_repository,
            statement_schema_repository=statement_schema_repository
        )
        
        # Act
        result = service.analyze_file(file_content, file_name)
        
        # Assert
        assert isinstance(result, FileAnalysisResponse)
        assert result.file_id == statement_id
        assert result.total_transactions == 2
        assert result.total_amount == 950.00
        assert result.date_range_start == date(2023, 1, 1)
        assert result.date_range_end == date(2023, 1, 2)
        
        # Verify column mappings
        assert isinstance(result.column_mappings, ColumnMapping)
        assert result.column_mappings.date == "Date"
        assert result.column_mappings.description == "Description"
        assert result.column_mappings.amount == "Amount"
        assert result.column_mappings.currency == "Currency"
        assert result.column_mappings.balance == "Balance"
        
        # Verify preview rows
        assert len(result.preview_rows) > 0
        assert len(result.preview_rows) <= 10  # Should show at most 10 rows
        
        # Verify interactions with dependencies
        file_type_detector.detect_file_type.assert_called_once_with(file_name)
        parser_factory.create_parser.assert_called_once_with(FileType.CSV)
        statement_parser.parse.assert_called_once_with(file_content)
        column_normalizer.normalize_columns.assert_called_once_with(df)
        transaction_cleaner.clean.assert_called_once_with(df, conversion_model)
        transactions_builder.build_transactions.assert_called_once_with(cleaned_df)
        statistics_calculator.calc_statistics.assert_called_once_with(transactions)
        statement_repository.save.assert_called_once()
        statement_schema_repository.find_by_column_hash.assert_called_once()
    
    def test_analyze_file_with_existing_schema(self):
        # Arrange
        # Sample data for testing
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
            "Currency": ["EUR", "EUR"],
            "Balance": [1000.00, 950.00],
        }
        df = pd.DataFrame(data)
        file_content = df.to_csv(index=False).encode("utf-8")
        file_name = "sample.csv"
        
        # Mock dependencies
        file_type_detector = MagicMock()
        file_type_detector.detect_file_type.return_value = FileType.CSV
        
        statement_parser = MagicMock()
        statement_parser.parse.return_value = df
        
        parser_factory = MagicMock()
        parser_factory.create_parser.return_value = statement_parser
            
        # Mock column normalizer
        column_normalizer = MagicMock()
        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance"
            },
            header_row=0,
            start_row=1
        )
        column_normalizer.normalize_columns.return_value = conversion_model
        
        # Mock transaction cleaner
        transaction_cleaner = MagicMock()
        cleaned_df = df.copy()
        transaction_cleaner.clean.return_value = cleaned_df
        
        # Mock transactions builder
        transactions_builder = MagicMock()
        transactions = [
            StatementTransaction(
                date=date(2023, 1, 1),
                description="Salary",
                amount=1000.00,
                currency="EUR"
            ),
            StatementTransaction(
                date=date(2023, 1, 2),
                description="Groceries",
                amount=-50.00,
                currency="EUR"
            )
        ]
        transactions_builder.build_transactions.return_value = transactions
        
        # Mock statistics calculator
        statistics_calculator = MagicMock()
        statistics = MagicMock()
        statistics.total_transactions = 2
        statistics.total_amount = 950.00
        statistics.date_range_start = date(2023, 1, 1)
        statistics.date_range_end = date(2023, 1, 2)
        statistics_calculator.calc_statistics.return_value = statistics
        
        # Mock statement repository
        statement_repository = MagicMock()
        statement_id = str(uuid.uuid4())
        statement_repository.save.return_value = statement_id
        
        # Mock statement schema repository with existing schema
        statement_schema_repository = MagicMock()
        existing_schema = MagicMock()
        existing_schema.column_mapping = {
            "date": "Date",
            "description": "Description",
            "amount": "Amount",
            "currency": "Currency",
            "balance": "Balance"
        }
        existing_schema.source_id = 1
        statement_schema_repository.find_by_column_hash.return_value = existing_schema
        
        # Create service under test
        service = FileAnalysisService(
            file_type_detector=file_type_detector,
            parser_factory=parser_factory,
            column_normalizer=column_normalizer,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statistics_calculator=statistics_calculator,
            statement_repository=statement_repository,
            statement_schema_repository=statement_schema_repository
        )
        
        # Act
        result = service.analyze_file(file_content, file_name)
        
        # Assert
        assert isinstance(result, FileAnalysisResponse)
        assert result.file_id == statement_id
        assert result.source_id == 1  # Should use the source_id from existing schema
        
        # Verify interactions with dependencies
        statement_schema_repository.find_by_column_hash.assert_called_once()
        statement_schema_repository.save.assert_not_called()  # Should not save a new schema
