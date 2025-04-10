from datetime import date

import pandas as pd
import pytest

from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.transaction_cleaner import TransactionCleaner


class TestTransactionCleaner:
    def test_clean_standard_columns(self):
        data = {
            "Date": ["2023-01-01", "01/01/2023"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
            "Currency": ["EUR", "EUR"],
            "Balance": [1000.00, 950.00],
        }
        df = pd.DataFrame(data)

        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance",
            },
            header_row=0,
            start_row=1,
        )

        cleaner = TransactionCleaner(conversion_model)
        result_df = cleaner.clean(df)

        assert {
            "date",
            "description",
            "amount",
            "currency",
            "balance",
        }.issubset(set(result_df.columns))

        assert isinstance(result_df["date"].iloc[0], date)
        assert result_df["date"].iloc[0] == date(2023, 1, 1)

        assert result_df["amount"].iloc[0] == 1000.00
        assert result_df["amount"].iloc[1] == -50.00

    def test_clean_with_separate_debit_credit_columns(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Description": ["Salary", "Groceries", "Rent"],
            "Debit": [0.00, 50.00, 500.00],  # Money going out
            "Credit": [1000.00, 0.00, 0.00],  # Money coming in
            "Balance": [1000.00, 950.00, 450.00],
        }
        df = pd.DataFrame(data)

        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "",
                "debit_amount": "Debit",
                "credit_amount": "Credit",
                "balance": "Balance",
                "currency": "",
            },
            header_row=0,
            start_row=1,
        )

        cleaner = TransactionCleaner(conversion_model)
        result_df = cleaner.clean(df)

        assert set(result_df.columns) == {
            "date",
            "description",
            "amount",
            "balance",
            "currency",
        }

        assert isinstance(result_df["date"].iloc[0], date)

        assert result_df["amount"].iloc[0] == 1000.00
        assert result_df["amount"].iloc[1] == -50.00
        assert result_df["amount"].iloc[2] == -500.00

        assert result_df["currency"].iloc[0] == ""

    def test_clean_with_different_date_formats(self):
        data = {
            "Date": [
                "01/01/2023",
                "02-01-2023",
                "2023.01.03",
                "01/01/2023 10:11:12",
                "01/01/2023 10:11:12",
                "01/01/2023 10:11:12",
            ],
        }
        df = pd.DataFrame(data)

        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
            },
            header_row=0,
            start_row=1,
        )

        cleaner = TransactionCleaner(conversion_model)
        result_df = cleaner.clean(df)

        assert result_df["date"].tolist() == [
            date(2023, 1, 1),
            date(2023, 1, 2),
            date(2023, 1, 3),
            date(2023, 1, 1),
            date(2023, 1, 1),
            date(2023, 1, 1),
        ]

    def test_clean_with_missing_columns(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
        }
        df = pd.DataFrame(data)

        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "",
                "balance": "",
            },
            header_row=0,
            start_row=1,
        )

        cleaner = TransactionCleaner(conversion_model)
        result_df = cleaner.clean(df)

        assert "currency" in result_df.columns
        assert "balance" in result_df.columns
        assert result_df["currency"].iloc[0] == ""
        assert pd.isna(result_df["balance"].iloc[0])

    def test_clean_with_extra_rows(self):
        data = {
            "Date": ["1", "2023-01-01", "2023-01-02"],
            "Description": ["2", "Salary", "Groceries"],
            "Amount": ["3", 1000.00, -50.00],
            "Currency": ["4", "EUR", "USD"],
            "Balance": ["5", 1000.00, 950.00],
        }
        df = pd.DataFrame(data)

        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance",
            },
            header_row=0,
            start_row=2,
        )

        cleaner = TransactionCleaner(conversion_model)
        result_df = cleaner.clean(df)

        assert len(result_df) == 2

    def test_clean_with_header_row_inside_doc(self):
        data = {
            "Column1": ["1", "Date", "2023-01-01"],
            "Column2": ["2", "Description", "Salary"],
            "Column3": ["3", "Amount", 1000.00],
            "Column4": ["4", "Currency", "EUR"],
            "Column5": ["5", "Balance", 1000.00],
        }
        df = pd.DataFrame(data)

        conversion_model = ConversionModel(
            column_map={
                "date": "Date",
                "description": "Description",
                "amount": "Amount",
                "currency": "Currency",
                "balance": "Balance",
            },
            header_row=2,
            start_row=3,
        )

        cleaner = TransactionCleaner(conversion_model)
        result_df = cleaner.clean(df)

        assert len(result_df) == 1
        assert result_df["date"].iloc[0] == date(2023, 1, 1)
        assert result_df["description"].iloc[0] == "Salary"
        assert result_df["amount"].iloc[0] == 1000.00
        assert result_df["currency"].iloc[0] == "EUR"
        assert result_df["balance"].iloc[0] == 1000.00
        
            
