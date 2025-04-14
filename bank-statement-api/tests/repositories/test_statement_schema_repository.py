import uuid
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from src.app.models import StatementSchema
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
            "column_hash": "abc123",
            "column_mapping": {
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance"
            },
            "file_type": FileType.CSV,
            "source_id": 1
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
        assert isinstance(schema, StatementSchema)
        assert schema.column_hash == schema_data["column_hash"]
        assert schema.column_mapping == schema_data["column_mapping"]
        assert schema.file_type == schema_data["file_type"].name
        assert schema.source_id == schema_data["source_id"]
        assert schema.id is not None
    
    def test_find_by_column_hash(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)
        
        # Create mock schema
        schema_id = str(uuid.uuid4())
        mock_schema = MagicMock(spec=StatementSchema)
        mock_schema.id = schema_id
        mock_schema.column_hash = "abc123"
        mock_schema.column_mapping = {
            "date": "Date",
            "description": "Description",
            "amount": "Amount",
            "currency": "Currency",
            "balance": "Balance"
        }
        mock_schema.file_type = "CSV"
        mock_schema.source_id = 1
        
        # Configure session to return the mock schema
        session.query.return_value.filter.return_value.first.return_value = mock_schema
        
        # Create repository
        repository = StatementSchemaRepository(session)
        
        # Act
        result = repository.find_by_column_hash("abc123")
        
        # Assert
        assert result is not None
        assert result.id == schema_id
        assert result.column_hash == mock_schema.column_hash
        assert result.column_mapping == mock_schema.column_mapping
        assert result.file_type == mock_schema.file_type
        assert result.source_id == mock_schema.source_id
        
        # Verify session interactions
        session.query.assert_called_once_with(StatementSchema)
        session.query.return_value.filter.assert_called_once()
    
    def test_find_by_column_hash_not_found(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)
        
        # Configure session to return None (schema not found)
        session.query.return_value.filter.return_value.first.return_value = None
        
        # Create repository
        repository = StatementSchemaRepository(session)
        
        # Act
        result = repository.find_by_column_hash("nonexistent")
        
        # Assert
        assert result is None
        
        # Verify session interactions
        session.query.assert_called_once_with(StatementSchema)
        session.query.return_value.filter.assert_called_once()
