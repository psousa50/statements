import uuid
from datetime import date
from typing import List
from unittest.mock import MagicMock

import pandas as pd

from src.app.models import StatementSchemaMapping
from src.app.repositories.statement_repository import StatementRepository
from src.app.repositories.statement_schema_repository import StatementSchemaRepository
from src.app.schemas import (
    ColumnMapping,
    StatementAnalysisResponse,
)
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_type_detector import (
    FileType,
    FileTypeDetector,
)
from src.app.services.file_processing.parsers.parser_factory import ParserFactory
from src.app.services.file_processing.parsers.statement_parser import StatementParser
from src.app.services.file_processing.statement_analysis_service import (
    StatementAnalysisService,
)
from src.app.services.file_processing.statement_statistics_calculator import (
    StatementStatistics,
    StatementStatisticsCalculator,
)
from src.app.services.file_processing.transactions_builder import (
    StatementTransaction,
    TransactionsBuilder,
)
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner


class TestFileAnalysisService:
    def test_analyze_file(self):
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "Description": ["Salary", "Groceries"],
                "Amount": [1000.00, -50.00],
                "Currency": ["EUR", "EUR"],
                "Balance": [1000.00, 950.00],
            }
        )
        file_content = df.to_csv(index=False).encode("utf-8")
        file_name = "sample.csv"

        service = createStatementAnalysisService(df=df)
        result = service.analyze_statement(file_content, file_name)

        assert isinstance(result, StatementAnalysisResponse)
        assert result.statement_id is not None
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
        assert len(result.preview_rows) <= 10
        assert result.preview_rows[0] == list(df.columns)

    def test_analyze_file_with_existing_schema(self):
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "Description": ["Salary", "Groceries"],
                "Amount": [1000.00, -50.00],
                "Currency": ["EUR", "EUR"],
                "Balance": [1000.00, 950.00],
            }
        )
        file_content = df.to_csv(index=False).encode("utf-8")
        file_name = "sample.csv"

        service = createStatementAnalysisService(df=df)
        result = service.analyze_statement(file_content, file_name)

        assert isinstance(result, StatementAnalysisResponse)
        assert result.statement_id is not None
        assert result.statement_schema.source_id == 1

    def test_analyze_file_with_header_row_at_first(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
            "Currency": ["EUR", "EUR"],
            "Balance": [1000.00, 950.00],
        }

        df = pd.DataFrame(data)
        file_content = df.to_csv(index=False).encode("utf-8")
        file_name = "header_not_first.csv"

        service = createStatementAnalysisService(
            df=df,
            conversion_model=ConversionModel(
                column_map={
                    "date": "Date",
                    "description": "Description",
                    "amount": "Amount",
                    "currency": "Currency",
                    "balance": "Balance",
                },
                header_row=0,
                start_row=1,
            ),
        )

        result = service.analyze_statement(file_content, file_name)

        assert result.statement_schema.column_mapping.date == "Date"
        assert result.statement_schema.column_mapping.description == "Description"
        assert result.statement_schema.column_mapping.amount == "Amount"
        assert result.statement_schema.column_mapping.currency == "Currency"
        assert result.statement_schema.column_mapping.balance == "Balance"

        assert result.preview_rows[0] == [
            "Date",
            "Description",
            "Amount",
            "Currency",
            "Balance",
        ]
        assert result.preview_rows[1] == [
            "2023-01-01",
            "Salary",
            "1000.0",
            "EUR",
            "1000.0",
        ]
        assert result.preview_rows[2] == [
            "2023-01-02",
            "Groceries",
            "-50.0",
            "EUR",
            "950.0",
        ]

    def test_analyze_file_with_header_row_not_first(self):
        data = {
            "Not Header": ["something", "Date", "2023-01-02"],
            "Not Description": ["something", "Description", "Groceries"],
            "Not Amount": ["something", "Amount", -50.00],
            "Not Currency": ["something", "Currency", "EUR"],
            "Not Balance": ["something", "Balance", 950.00],
        }
        df = pd.DataFrame(data)
        file_content = df.to_csv(index=False).encode("utf-8")
        file_name = "header_not_first.csv"

        service = createStatementAnalysisService(
            df=df,
            conversion_model=ConversionModel(
                column_map={
                    "date": "Date",
                    "description": "Description",
                    "amount": "Amount",
                    "currency": "Currency",
                    "balance": "Balance",
                },
                header_row=2,
                start_row=3,
            ),
        )

        result = service.analyze_statement(file_content, file_name)

        assert isinstance(result, StatementAnalysisResponse)
        assert result.statement_id is not None
        assert isinstance(result.statement_schema.column_mapping, ColumnMapping)
        assert result.statement_schema.column_mapping.date == "Date"
        assert result.statement_schema.column_mapping.description == "Description"
        assert result.statement_schema.column_mapping.amount == "Amount"
        assert result.statement_schema.column_mapping.currency == "Currency"
        assert result.statement_schema.column_mapping.balance == "Balance"
        assert len(result.preview_rows) > 0
        assert len(result.preview_rows) <= 10
        assert result.preview_rows[0] == [
            "Not Header",
            "Not Description",
            "Not Amount",
            "Not Currency",
            "Not Balance",
        ]
        assert result.preview_rows[1] == [
            "something",
            "something",
            "something",
            "something",
            "something",
        ]
        assert result.preview_rows[2] == [
            "Date",
            "Description",
            "Amount",
            "Currency",
            "Balance",
        ]
        assert result.preview_rows[3] == [
            "2023-01-02",
            "Groceries",
            "-50.0",
            "EUR",
            "950.0",
        ]


def createStatementAnalysisService(
    df: pd.DataFrame = None,
    conversion_model: ConversionModel = None,
    transactions: List[StatementTransaction] = None,
    statistics: StatementStatistics = None,
    existing_state_schema_mappings: StatementSchemaMapping = None,
    file_type_detector: FileTypeDetector = None,
    statement_id: str = None,
    statement_parser: StatementParser = None,
    parser_factory: ParserFactory = None,
    column_normalizer: ColumnNormalizer = None,
    transaction_cleaner: TransactionsCleaner = None,
    transactions_builder: TransactionsBuilder = None,
    statistics_calculator: StatementStatisticsCalculator = None,
    statement_repository: StatementRepository = None,
    statement_schema_repository: StatementSchemaRepository = None,
) -> StatementAnalysisService:
    if conversion_model is None:
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
    if df is None:
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "Description": ["Salary", "Groceries"],
                "Amount": [1000.00, -50.00],
                "Currency": ["EUR", "EUR"],
                "Balance": [1000.00, 950.00],
            }
        )
    if transactions is None:
        transactions = [
            StatementTransaction(
                date=date(2023, 1, 1),
                description="Salary",
                amount=1000.00,
                currency="EUR",
            ),
        ]
    if statement_id is None:
        statement_id = str(uuid.uuid4())
    if statistics is None:
        statistics = StatementStatistics(
            total_transactions=2,
            total_amount=950.00,
            date_range_start=date(2023, 1, 1),
            date_range_end=date(2023, 1, 2),
        )
    if existing_state_schema_mappings is None:
        existing_state_schema_mappings = StatementSchemaMapping(
            id=str(uuid.uuid4()),
            statement_hash="existing-statement-hash",
            schema_data={
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
                "column_names": [
                    "Date",
                    "Description",
                    "Amount",
                    "Currency",
                    "Balance",
                ],
            },
        )
    if file_type_detector is None:
        file_type_detector = MagicMock()
        file_type_detector.detect_file_type.return_value = FileType.CSV
    if statement_parser is None:
        statement_parser = MagicMock()
        statement_parser.parse.return_value = df
    if parser_factory is None:
        parser_factory = MagicMock()
        parser_factory.create_parser.return_value = statement_parser
    if column_normalizer is None:
        column_normalizer = MagicMock()
        column_normalizer.normalize_columns.return_value = conversion_model
    if transaction_cleaner is None:
        transaction_cleaner = MagicMock()
        cleaned_df = df.copy()
        transaction_cleaner.clean.return_value = cleaned_df
    if transactions_builder is None:
        transactions_builder = MagicMock()
        transactions_builder.build_transactions.return_value = transactions
    if statistics_calculator is None:
        statistics_calculator = MagicMock()
        statistics_calculator.calc_statistics.return_value = statistics
    if statement_repository is None:
        statement_repository = MagicMock()
        statement_repository.save.return_value = statement_id
    if statement_schema_repository is None:
        statement_schema_repository = MagicMock()
        statement_schema_repository.find_by_statement_hash.return_value = (
            existing_state_schema_mappings
        )
    return StatementAnalysisService(
        file_type_detector=file_type_detector,
        parser_factory=parser_factory,
        column_normalizer=column_normalizer,
        transaction_cleaner=transaction_cleaner,
        transactions_builder=transactions_builder,
        statistics_calculator=statistics_calculator,
        statement_repository=statement_repository,
        statement_schema_repository=statement_schema_repository,
    )
