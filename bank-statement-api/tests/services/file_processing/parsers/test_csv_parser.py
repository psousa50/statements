import os
import tempfile
import textwrap

import pandas as pd

from src.app.services.file_processing.parsers.csv_parser import CSVParser


class TestCSVParser:
    def test_parse_csv_file(self):
        csv_content = textwrap.dedent(
            """
                        Date,Description,Amount,Balance
                        2023-01-01,Salary,1000.00,1000.00
                        2023-01-02,Groceries,-50.00,950.00
                        2023-01-03,Rent,-500.00,450.00
                    """
        )
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write(csv_content)
            temp_file_path = f.name

        try:
            parser = CSVParser()
            file_content = open(temp_file_path, "rb").read()
            df = parser.parse(file_content)

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3

            assert set(df.columns) == {"Date", "Description", "Amount", "Balance"}

            assert df.iloc[0]["Date"] == "2023-01-01"
            assert df.iloc[0]["Description"] == "Salary"
            assert df.iloc[0]["Amount"] == 1000.00
            assert df.iloc[0]["Balance"] == 1000.00

            assert df.iloc[1]["Date"] == "2023-01-02"
            assert df.iloc[1]["Description"] == "Groceries"
            assert df.iloc[1]["Amount"] == -50.00
            assert df.iloc[1]["Balance"] == 950.00

            assert df.iloc[2]["Date"] == "2023-01-03"
            assert df.iloc[2]["Description"] == "Rent"
            assert df.iloc[2]["Amount"] == -500.00
            assert df.iloc[2]["Balance"] == 450.00
        finally:
            os.unlink(temp_file_path)

    def test_parse_csv_with_missing_columns(self):
        csv_content = textwrap.dedent(
            """
                        Date,Description,Amount
                        2023-01-01,Salary,1000.00
                        2023-01-02,Groceries,-50.00
                        2023-01-03,Rent,-500.00
                    """
        )
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write(csv_content)
            temp_file_path = f.name

        try:
            parser = CSVParser()
            file_content = open(temp_file_path, "rb").read()
            df = parser.parse(file_content)

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3

            assert set(df.columns) == {"Date", "Description", "Amount"}

            assert "Balance" not in df.columns
        finally:
            os.unlink(temp_file_path)
