import os
import tempfile

import pandas as pd

from src.app.services.file_processing.parsers.csv_parser import CSVParser


class TestCSVParser:
    def test_parse_csv_file(self):
        # Create a temporary CSV file
        csv_content = """Date,Description,Amount,Balance
2023-01-01,Salary,1000.00,1000.00
2023-01-02,Groceries,-50.00,950.00
2023-01-03,Rent,-500.00,450.00
"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write(csv_content)
            temp_file_path = f.name

        try:
            # Parse the CSV file
            parser = CSVParser()
            df = parser.parse(temp_file_path)

            # Verify the results
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3

            # Check column names
            assert set(df.columns) == {'Date', 'Description', 'Amount', 'Balance'}

            # Check first row
            assert df.iloc[0]['Date'] == '2023-01-01'
            assert df.iloc[0]['Description'] == 'Salary'
            assert df.iloc[0]['Amount'] == 1000.00
            assert df.iloc[0]['Balance'] == 1000.00

            # Check second row
            assert df.iloc[1]['Date'] == '2023-01-02'
            assert df.iloc[1]['Description'] == 'Groceries'
            assert df.iloc[1]['Amount'] == -50.00
            assert df.iloc[1]['Balance'] == 950.00

            # Check third row
            assert df.iloc[2]['Date'] == '2023-01-03'
            assert df.iloc[2]['Description'] == 'Rent'
            assert df.iloc[2]['Amount'] == -500.00
            assert df.iloc[2]['Balance'] == 450.00
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_parse_csv_with_missing_columns(self):
        # Create a temporary CSV file with missing columns
        csv_content = """Date,Description,Amount
2023-01-01,Salary,1000.00
2023-01-02,Groceries,-50.00
2023-01-03,Rent,-500.00
"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write(csv_content)
            temp_file_path = f.name

        try:
            # Parse the CSV file
            parser = CSVParser()
            df = parser.parse(temp_file_path)

            # Verify the results
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3

            # Check column names
            assert set(df.columns) == {'Date', 'Description', 'Amount'}

            # Verify that Balance column is not present
            assert 'Balance' not in df.columns
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
