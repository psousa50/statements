import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pandas as pd

from src.app.schemas import (
    ColumnMapping,
    FileUploadResponse,
    StatementSchemaDefinition,
    Transaction,
    UploadFileSpec,
)
from src.app.services.file_processing.file_type_detector import (
    FileType,
)
from src.app.services.file_processing.statement_upload_service import (
    StatementUploadService,
)
from src.app.services.file_processing.transactions_builder import (
    StatementTransaction,
)


class TestStatementUploadService:
    def test_upload_file(self):
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
        statement_id = str(uuid.uuid4())

        # Mock dependencies
        file_type_detector = MagicMock()
        file_type_detector.detect_file_type.return_value = FileType.CSV

        statement_parser = MagicMock()
        statement_parser.parse.return_value = df

        parser_factory = MagicMock()
        parser_factory.create_parser.return_value = statement_parser

        # Mock statement repository
        statement_repository = MagicMock()
        statement_repository.get_by_id.return_value = {
            "id": statement_id,
            "content": file_content,
            "file_name": file_name,
        }

        # Mock column mapping
        column_mapping = ColumnMapping(
            date="Date",
            description="Description",
            amount="Amount",
            currency="Currency",
            balance="Balance",
        )

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
                amount=Decimal("1000.00"),
                currency="EUR",
            ),
            StatementTransaction(
                date=date(2023, 1, 2),
                description="Groceries",
                amount=Decimal("-50.00"),
                currency="EUR",
            ),
        ]
        transactions_builder.build_transactions.return_value = transactions

        # Mock transactions repository
        transactions_repository = MagicMock()
        transactions_repository.find_duplicates.return_value = []

        # Create proper Transaction objects for the response
        created_transactions = [
            Transaction(
                id=1,
                date=date(2023, 1, 1),
                description="Salary",
                amount=1000.00,
                currency="EUR",
                source_id=1,
                category_id=None,
                sub_category_id=None,
                categorization_status="pending",
                normalized_description="salary",
            ),
            Transaction(
                id=2,
                date=date(2023, 1, 2),
                description="Groceries",
                amount=-50.00,
                currency="EUR",
                source_id=1,
                category_id=None,
                sub_category_id=None,
                categorization_status="pending",
                normalized_description="groceries",
            ),
        ]
        transactions_repository.create_many.return_value = created_transactions

        # Mock statement schema repository
        statement_schema_repository = MagicMock()
        statement_schema_repository.update.return_value = None

        # Create service under test
        service = StatementUploadService(
            parser_factory=parser_factory,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statement_repository=statement_repository,
            transactions_repository=transactions_repository,
            statement_schema_repository=statement_schema_repository,
        )

        # Create upload spec
        upload_spec = UploadFileSpec(
            statement_id=statement_id,
            statement_schema=StatementSchemaDefinition(
                id=str(uuid.uuid4()),
                statement_hash=str(uuid.uuid4()),
                file_type="CSV",
                column_mapping=column_mapping,
                schema_data={
                    "column_mapping": column_mapping,
                    "source_id": 1,
                    "start_row": 1,
                    "file_type": "CSV",
                },
            ),
        )

        # Act
        result = service.upload_statement(upload_spec)

        # Assert
        assert isinstance(result, FileUploadResponse)
        assert result.transactions_processed == 2
        assert len(result.transactions) == 2
        assert result.skipped_duplicates == 0

        # Verify interactions with dependencies
        statement_repository.get_by_id.assert_called_once_with(statement_id)
        parser_factory.create_parser.assert_called_once()
        statement_parser.parse.assert_called_once_with(file_content)
        transaction_cleaner.clean.assert_called_once()
        transactions_builder.build_transactions.assert_called_once_with(cleaned_df)
        transactions_repository.create_many.assert_called_once()

    def test_statement_upload_service_with_duplicate_transactions(self):
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
        statement_id = str(uuid.uuid4())

        # Mock dependencies
        file_type_detector = MagicMock()
        file_type_detector.detect_file_type.return_value = FileType.CSV

        statement_parser = MagicMock()
        statement_parser.parse.return_value = df

        parser_factory = MagicMock()
        parser_factory.create_parser.return_value = statement_parser

        # Mock statement repository
        statement_repository = MagicMock()
        statement_repository.get_by_id.return_value = {
            "id": statement_id,
            "content": file_content,
            "file_name": file_name,
        }

        # Mock column mapping
        column_mapping = ColumnMapping(
            date="Date",
            description="Description",
            amount="Amount",
            currency="Currency",
            balance="Balance",
        )

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
                amount=Decimal("1000.00"),
                currency="EUR",
            ),
            StatementTransaction(
                date=date(2023, 1, 2),
                description="Groceries",
                amount=Decimal("-50.00"),
                currency="EUR",
            ),
        ]
        transactions_builder.build_transactions.return_value = transactions

        # Mock transactions repository - simulate duplicate detection
        transactions_repository = MagicMock()
        transactions_repository.find_duplicates.return_value = [
            transactions[0]
        ]  # First transaction is a duplicate

        # Create proper Transaction objects for the response
        created_transactions = [
            Transaction(
                id=2,
                date=date(2023, 1, 2),
                description="Groceries",
                amount=-50.00,
                currency="EUR",
                source_id=1,
                category_id=None,
                sub_category_id=None,
                categorization_status="pending",
                normalized_description="groceries",
            )
        ]
        transactions_repository.create_many.return_value = created_transactions

        # Mock statement schema repository
        statement_schema_repository = MagicMock()
        statement_schema_repository.update.return_value = None

        # Create service under test
        service = StatementUploadService(
            parser_factory=parser_factory,
            transaction_cleaner=transaction_cleaner,
            transactions_builder=transactions_builder,
            statement_repository=statement_repository,
            transactions_repository=transactions_repository,
            statement_schema_repository=statement_schema_repository,
        )

        # Create upload spec
        upload_spec = UploadFileSpec(
            statement_id=statement_id,
            statement_schema=StatementSchemaDefinition(
                id=str(uuid.uuid4()),
                statement_hash=str(uuid.uuid4()),
                file_type="CSV",
                column_mapping=column_mapping,
                schema_data={
                    "column_mapping": column_mapping,
                    "source_id": 1,
                    "start_row": 1,
                    "file_type": "CSV",
                },
            ),
        )

        # Act
        result = service.upload_statement(upload_spec)

        # Assert
        assert isinstance(result, FileUploadResponse)
        assert result.transactions_processed == 1  # Only one transaction processed
        assert len(result.transactions) == 1
        assert result.skipped_duplicates == 1  # One duplicate skipped

        # Verify interactions with dependencies
        transactions_repository.find_duplicates.assert_called_once()
        transactions_repository.create_many.assert_called_once()  # Only non-duplicate transactions created
