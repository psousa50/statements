import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from src.app.models import Statement
from src.app.repositories.statement_repository import StatementRepository


class TestStatementRepository:
    def test_save_statement(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)

        # Create repository
        repository = StatementRepository(session)

        # Test data
        file_content = b"test,file,content\n1,2,3"
        file_name = "test.csv"

        # Act
        statement_id = repository.save(file_content, file_name)

        # Assert
        assert isinstance(statement_id, str)

        # Verify session interactions
        session.add.assert_called_once()
        session.commit.assert_called_once()

        # Verify the statement was created with correct attributes
        statement = session.add.call_args[0][0]
        assert isinstance(statement, Statement)
        assert statement.file_name == file_name
        assert statement.content == file_content
        assert statement.id is not None

    def test_get_by_id(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)

        # Create mock statement
        statement_id = str(uuid.uuid4())
        mock_statement = MagicMock(spec=Statement)
        mock_statement.id = statement_id
        mock_statement.file_name = "test.csv"
        mock_statement.content = b"test,file,content\n1,2,3"
        mock_statement.created_at = datetime.now()

        # Configure session to return the mock statement
        session.query.return_value.filter.return_value.first.return_value = (
            mock_statement
        )

        # Create repository
        repository = StatementRepository(session)

        # Act
        result = repository.get_by_id(statement_id)

        # Assert
        assert result is not None
        assert result["id"] == statement_id
        assert result["file_name"] == mock_statement.file_name
        assert result["content"] == mock_statement.content

        # Verify session interactions
        session.query.assert_called_once_with(Statement)
        session.query.return_value.filter.assert_called_once()

    def test_get_by_id_not_found(self):
        # Arrange
        # Mock session
        session = MagicMock(spec=Session)

        # Configure session to return None (statement not found)
        session.query.return_value.filter.return_value.first.return_value = None

        # Create repository
        repository = StatementRepository(session)

        # Act
        result = repository.get_by_id(str(uuid.uuid4()))

        # Assert
        assert result is None

        # Verify session interactions
        session.query.assert_called_once_with(Statement)
        session.query.return_value.filter.assert_called_once()
