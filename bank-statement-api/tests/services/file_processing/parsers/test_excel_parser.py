import os
import tempfile

import pandas as pd

from src.app.services.file_processing.parsers.excel_parser import ExcelParser


class TestExcelParser:
    def test_parse_excel_file(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Description": ["Salary", "Groceries", "Rent"],
            "Amount": [1000.00, -50.00, -500.00],
            "Balance": [1000.00, 950.00, 450.00],
        }
        df_to_write = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_file_path = f.name

        # Write the DataFrame to the Excel file
        df_to_write.to_excel(temp_file_path, index=False, engine="openpyxl")

        try:
            parser = ExcelParser()
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

    def test_parse_excel_with_multiple_sheets(self):
        data1 = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
            "Balance": [1000.00, 950.00],
        }

        data2 = {
            "Date": ["2023-02-01", "2023-02-02"],
            "Description": ["Bonus", "Utilities"],
            "Amount": [500.00, -100.00],
            "Balance": [1450.00, 1350.00],
        }

        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_file_path = f.name

        with pd.ExcelWriter(temp_file_path, engine="openpyxl") as writer:
            df1.to_excel(writer, sheet_name="January", index=False)
            df2.to_excel(writer, sheet_name="February", index=False)

        try:
            parser = ExcelParser()
            file_content = open(temp_file_path, "rb").read()
            df = parser.parse(file_content)

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert df.iloc[0]["Description"] == "Salary"

            df_feb = parser.parse(file_content, sheet_name="February")

            assert isinstance(df_feb, pd.DataFrame)
            assert len(df_feb) == 2
            assert df_feb.iloc[0]["Description"] == "Bonus"
        finally:
            os.unlink(temp_file_path)

    def test_parse_excel_with_missing_columns(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Description": ["Salary", "Groceries", "Rent"],
            "Amount": [1000.00, -50.00, -500.00],
        }
        df_to_write = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_file_path = f.name

        df_to_write.to_excel(temp_file_path, index=False, engine="openpyxl")

        try:
            parser = ExcelParser()
            file_content = open(temp_file_path, "rb").read()
            df = parser.parse(file_content)

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3

            assert set(df.columns) == {"Date", "Description", "Amount"}

            assert "Balance" not in df.columns
        finally:
            os.unlink(temp_file_path)
