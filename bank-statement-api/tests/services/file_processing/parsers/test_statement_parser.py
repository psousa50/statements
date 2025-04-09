from abc import ABC

import pytest

from src.app.services.file_processing.parsers.statement_parser import StatementParser


class TestStatementParser:
    def test_statement_parser_is_abstract(self):
        # Verify that StatementParser is an abstract base class
        assert issubclass(StatementParser, ABC)

        # Verify that it has abstract methods
        with pytest.raises(TypeError):
            StatementParser()
