import uuid
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.app.models import StatementSchemaMapping
from src.app.repositories.statement_schema_repository import StatementSchemaRepository
from src.app.services.file_processing.file_type_detector import FileType


class TestStatementSchemaRepository:
    def test_save_schema(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)

        # Create repository
        repository = StatementSchemaRepository(session)

        # Test data
        schema_data = {
            "statement_hash": "abc123",
            "schema_data": {
                "column_mapping": {
                    "date": "Date",
                    "description": "Description",
                    "amount": "Amount",
                    "currency": "Currency",
                    "balance": "Balance",
                },
                "file_type": FileType.CSV.name,
                "source_id": 1,
            },
        }

        # Act
        schema_id = repository.save(schema_data)

        # Assert
        assert isinstance(schema_id, str)

        # Verify session interactions
        session.add.assert_called_once()
        session.commit.assert_called_once()

        # Verify the schema was created with correct attributes
        schema = session.add.call_args[0][0]
        assert isinstance(schema, StatementSchemaMapping)
        assert schema.statement_hash == schema_data["statement_hash"]
        assert schema.schema_data == schema_data["schema_data"]
        assert schema.id is not None

    def test_find_by_statement_hash(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)

        # Mock schema
        schema = MagicMock(spec=StatementSchemaMapping)
        schema.id = str(uuid.uuid4())
        schema.statement_hash = "abc123"
        schema.schema_data = {
            "column_mapping": {
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance",
            },
            "file_type": FileType.CSV.name,
            "source_id": 1,
        }

        # Configure session to return the mock schema
        session.query.return_value.filter.return_value.first.return_value = schema

        # Create repository
        repository = StatementSchemaRepository(session)

        # Act
        result = repository.find_by_statement_hash("abc123")

        # Assert
        assert result is not None
        assert result.id == schema.id
        assert result.statement_hash == schema.statement_hash
        assert result.schema_data == schema.schema_data

        # Verify session interactions
        session.query.assert_called_once_with(StatementSchemaMapping)
        session.query.return_value.filter.assert_called_once()

    def test_find_by_statement_hash_not_found(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)

        # Configure session to return None (schema not found)
        session.query.return_value.filter.return_value.first.return_value = None

        # Create repository
        repository = StatementSchemaRepository(session)

        # Act
        result = repository.find_by_statement_hash("nonexistent")

        # Assert
        assert result is None

        # Verify session interactions
        session.query.assert_called_once_with(StatementSchemaMapping)
        session.query.return_value.filter.assert_called_once()

    def test_statement_schema_mapping_has_statement_hash(self):
        schema = StatementSchemaMapping(
            id="test_id",
            statement_hash="test_hash",
            schema_data={}
        )
        assert hasattr(schema, "statement_hash")
        assert schema.statement_hash == "test_hash"
