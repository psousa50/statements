import os
from pathlib import Path

import pandas as pd

from src.app.services.file_processing.file_processor import FileProcessor

TEST_RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"


class TestFileProcessor:
    def test_process_csv_file(self):
        test_file_path = os.path.join(TEST_RESOURCES_DIR, "sample.csv")
        file_content = open(test_file_path, "rb").read()
        file_processor = FileProcessor()
        df = file_processor.process_file(file_content, test_file_path)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert {"date", "description", "amount", "currency", "balance"}.issubset(
            set(df.columns)
        )

    def test_process_excel_file(self):
        test_file_path = os.path.join(TEST_RESOURCES_DIR, "sample.xlsx")
        file_content = open(test_file_path, "rb").read()
        file_processor = FileProcessor()
        df = file_processor.process_file(file_content, test_file_path)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert {"date", "description", "amount", "currency", "balance"}.issubset(
            set(df.columns)
        )
