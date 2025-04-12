import os
import uuid
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from src.app.ai.llm_client import LLMClient
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_processor import FileProcessor, ProcessedFile
from src.app.services.file_processing.file_type_detector import (
    FileType,
    FileTypeDetector,
)
from src.app.services.file_processing.statement_statistics_calculator import (
    StatementStatisticsCalculator,
)
from src.app.services.file_processing.transactions_builder import (
    StatementTransaction,
    TransactionsBuilder,
)
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner


class TestFileProcessor:
    def test_process_file(self):
        data = {
            "Source": ["Source1", "Source1"],
            "Data Lanc.": ["2023-01-01", "02-01-2023"],
            "Descrição": ["Salary", "Groceries"],
            "Valor": [1000.00, -50.00],
            "Moeda": ["EUR", "EUR"],
            "Saldo": [1000.00, 950.00],
            "Type": ["Income", "Expense"],
        }
        df = pd.DataFrame(data)
        file_content = df.to_csv(index=False).encode("utf-8")
        file_name = "sample.csv"

        file_type_detector = FileTypeDetector()
        llm_client: LLMClient = MagicMock()
        llm_client.generate.return_value = """
        {
            "header_row": 0,
            "start_row": 1,
            "column_map": {            
                "date": "Data Lanc.",
                "description": "Descrição",
                "amount": "Valor",
                "currency": "Moeda",
                "balance": "Saldo"
            }
        }
        """
        column_normalizer = ColumnNormalizer(llm_client)
        transaction_cleaner = TransactionsCleaner()
        transactions_builder = TransactionsBuilder()
        statistics_calculator = StatementStatisticsCalculator()

        file_processor = FileProcessor(
            file_type_detector,
            column_normalizer,
            transaction_cleaner,
            transactions_builder,
            statistics_calculator,
        )

        processed_file = file_processor.process_file(file_content, file_name)

        assert isinstance(processed_file, ProcessedFile)
        assert processed_file.file_name == file_name
        assert processed_file.file_type == FileType.CSV

        assert processed_file.conversion_model.header_row == 0
        assert processed_file.conversion_model.start_row == 1
        assert processed_file.conversion_model.column_map == {
            "date": "Data Lanc.",
            "description": "Descrição",
            "amount": "Valor",
            "currency": "Moeda",
            "balance": "Saldo",
        }

        assert len(processed_file.transactions) == 2
        assert processed_file.transactions == [
            StatementTransaction(
                date="2023-01-01",
                description="Salary",
                amount=Decimal("1000.00"),
                currency="EUR",
                balance=Decimal("1000.00"),
                type="Income",
            ),
            StatementTransaction(
                date="2023-01-02",
                description="Groceries",
                amount=Decimal("-50.00"),
                currency="EUR",
                balance=Decimal("950.00"),
                type="Expense",
            ),
        ]
