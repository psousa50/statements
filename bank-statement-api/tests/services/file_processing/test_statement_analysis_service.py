import uuid
from datetime import date
from unittest.mock import MagicMock

import pandas as pd

from src.app.schemas import ColumnMapping, FileAnalysisResponse
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_type_detector import (
    FileType,
)
from src.app.services.file_processing.statement_analysis_service import (
    StatementAnalysisService,
)
from src.app.services.file_processing.transactions_builder import (
    StatementTransaction,
)


class TestFileAnalysisService:
    def test_analyze_file(self):
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

        file_type_detector = MagicMock()
        file_type_detector.detect_file_type.return_value = FileType.CSV

        statement_parser = MagicMock()
        statement_parser.parse.return_value = df

        parser_factory = MagicMock()
        parser_factory.create_parser.return_value = statement_parser

        column_normalizer = MagicMock()
        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance",
            },
            header_row=0,
            start_row=1,
        )
        column_normalizer.normalize_columns.return_value = conversion_model

        transaction_cleaner = MagicMock()
        cleaned_df = df.copy()
        transaction_cleaner.clean.return_value = cleaned_df

        transactions_builder = MagicMock()
        transactions = [
            StatementTransaction(
                date=date(2023, 1, 1),
                description="Salary",
                amount=1000.00,
                currency="EUR",
            ),
            StatementTransaction(
                date=date(2023, 1, 2),
                description="Groceries",
                amount=-50.00,
                currency="EUR",
            ),
        ]
        transactions_builder.build_transactions.return_value = transactions

        statistics_calculator = MagicMock()
        statistics = MagicMock()
        statistics.total_transactions = 2
        statistics.total_amount = 950.00
        statistics.date_range_start = date(2023, 1, 1)
        statistics.date_range_end = date(2023, 1, 2)
        statistics_calculator.calc_statistics.return_value = statistics

        statement_repository = MagicMock()
        statement_id = str(uuid.uuid4())
        statement_repository.save.return_value = statement_id

        statement_schema_repository = MagicMock()
        statement_schema_repository.find_by_statement_hash.return_value = None

        service = StatementAnalysisService(
            file_type_detector=file_type_detector,
            parser_factory=parser_factory,
            column_normalizer=column_normalizer,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statistics_calculator=statistics_calculator,
            statement_repository=statement_repository,
            statement_schema_repository=statement_schema_repository,
        )

        result = service.analyze_statement(file_content, file_name)

        assert isinstance(result, FileAnalysisResponse)
        assert result.file_id == statement_id
        assert result.total_transactions == 2
        assert result.total_amount == 950.00
        assert result.date_range_start == date(2023, 1, 1)
        assert result.date_range_end == date(2023, 1, 2)

        assert isinstance(result.statement_schema.column_mapping, ColumnMapping)
        assert result.statement_schema.column_mapping.date == "Date"
        assert result.statement_schema.column_mapping.description == "Description"
        assert result.statement_schema.column_mapping.amount == "Amount"
        assert result.statement_schema.column_mapping.currency == "Currency"
        assert result.statement_schema.column_mapping.balance == "Balance"

        assert len(result.preview_rows) > 0
        assert len(result.preview_rows) <= 10  # Should show at most 10 rows

        file_type_detector.detect_file_type.assert_called_once_with(file_name)
        parser_factory.create_parser.assert_called_once_with(FileType.CSV)
        statement_parser.parse.assert_called_once_with(file_content)
        column_normalizer.normalize_columns.assert_called_once_with(df)
        transaction_cleaner.clean.assert_called_once_with(df, conversion_model)
        transactions_builder.build_transactions.assert_called_once_with(cleaned_df)
        statistics_calculator.calc_statistics.assert_called_once_with(transactions)
        statement_repository.save.assert_called_once()
        statement_schema_repository.find_by_statement_hash.assert_called_once()

    def test_analyze_file_with_existing_schema(self):
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

        file_type_detector = MagicMock()
        file_type_detector.detect_file_type.return_value = FileType.CSV

        statement_parser = MagicMock()
        statement_parser.parse.return_value = df

        parser_factory = MagicMock()
        parser_factory.create_parser.return_value = statement_parser

        column_normalizer = MagicMock()
        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance",
            },
            header_row=0,
            start_row=1,
        )
        column_normalizer.normalize_columns.return_value = conversion_model

        transaction_cleaner = MagicMock()
        cleaned_df = df.copy()
        transaction_cleaner.clean.return_value = cleaned_df

        transactions_builder = MagicMock()
        transactions = [
            StatementTransaction(
                date=date(2023, 1, 1),
                description="Salary",
                amount=1000.00,
                currency="EUR",
            ),
            StatementTransaction(
                date=date(2023, 1, 2),
                description="Groceries",
                amount=-50.00,
                currency="EUR",
            ),
        ]
        transactions_builder.build_transactions.return_value = transactions

        statistics_calculator = MagicMock()
        statistics = MagicMock()
        statistics.total_transactions = 2
        statistics.total_amount = 950.00
        statistics.date_range_start = date(2023, 1, 1)
        statistics.date_range_end = date(2023, 1, 2)
        statistics_calculator.calc_statistics.return_value = statistics

        statement_repository = MagicMock()
        statement_id = str(uuid.uuid4())
        statement_repository.save.return_value = statement_id

        existing_schema = MagicMock()
        existing_schema.id = "existing-schema-id"

        schema_data = {
            "id": "existing-schema-id",
            "source_id": 1,
            "file_type": "CSV",
            "column_mapping": {
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance",
            },
            "start_row": 1,
            "header_row": 0,
            "column_names": ["Date", "Description", "Amount", "Currency", "Balance"],
        }

        existing_schema.schema_data = schema_data
        statement_schema_repository = MagicMock()
        statement_schema_repository.find_by_statement_hash.return_value = (
            existing_schema
        )

        service = StatementAnalysisService(
            file_type_detector=file_type_detector,
            parser_factory=parser_factory,
            column_normalizer=column_normalizer,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statistics_calculator=statistics_calculator,
            statement_repository=statement_repository,
            statement_schema_repository=statement_schema_repository,
        )

        result = service.analyze_statement(file_content, file_name)

        assert isinstance(result, FileAnalysisResponse)
        assert result.file_id == statement_id
        assert result.statement_schema.source_id == 1

        statement_schema_repository.find_by_statement_hash.assert_called_once()
        statement_schema_repository.save.assert_not_called()
