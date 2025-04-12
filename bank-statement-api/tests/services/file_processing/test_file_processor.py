import os
from pathlib import Path
from unittest.mock import MagicMock

from src.app.ai.llm_client import LLMClient
from src.app.services.file_processing.file_type_detector import FileTypeDetector
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.transaction_cleaner import TransactionCleaner
from src.app.services.file_processing.conversion_model import ConversionModel

import pandas as pd

from src.app.services.file_processing.file_processor import FileProcessor

TEST_RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"


class TestFileProcessor:
    def test_process_file(self):
        data = {
            "Source": ["Source1", "Source1"],
            "Data Lanc.": ["2023-01-01", "01/01/2023"],
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
        transaction_cleaner = TransactionCleaner()
        file_processor = FileProcessor(
            file_type_detector, column_normalizer, transaction_cleaner
        )
        df, conversion_model = file_processor.process_file(file_content, file_name)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert df.columns.tolist() == [
            "Source",
            "date",
            "description",
            "amount",
            "currency",
            "balance",
            "Type",
        ]

        assert conversion_model.header_row == 0
        assert conversion_model.start_row == 1
        assert conversion_model.column_map == {
            "date": "Data Lanc.",
            "description": "Descrição",
            "amount": "Valor",
            "currency": "Moeda",
            "balance": "Saldo",
        }
