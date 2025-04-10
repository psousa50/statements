from datetime import date, datetime

import numpy as np
import pandas as pd
import pytest

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

        column_map = {
            "Date": "date",
            "Description": "description",
            "Amount": "amount",
            "Currency": "currency",
            "Balance": "balance",
        }

        cleaner = TransactionCleaner(column_map)
        result_df = cleaner.clean(df)

        assert set(result_df.columns) == {
            "date",
            "description",
            "amount",
            "currency",
            "balance",
        }

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

        column_map = {
            "Date": "date",
            "Description": "description",
            "Debit": "amount",
            "Credit": "amount",
            "Balance": "balance",
            "currency": "",
        }

        cleaner = TransactionCleaner(column_map)
        result_df = cleaner.clean(df)

        # Check that the columns are renamed
        assert set(result_df.columns) == {
            "date",
            "description",
            "amount",
            "balance",
            "currency",
        }

        # Check that the date is parsed correctly
        assert isinstance(result_df["date"].iloc[0], date)

        # Check that the debit and credit columns are combined correctly
        assert result_df["amount"].iloc[0] == 1000.00  # Credit (positive)
        assert result_df["amount"].iloc[1] == -50.00  # Debit (negative)
        assert result_df["amount"].iloc[2] == -500.00  # Debit (negative)

        # Check that the currency is set to a default value
        assert result_df["currency"].iloc[0] == ""

    def test_clean_with_different_date_formats(self):
        data = {
            "date": ["01/01/2023", "02-01-2023", "2023.01.03", "01/01/2023 10:11:12", "01/01/2023 10:11:12", "01/01/2023 10:11:12"],
        }
        df = pd.DataFrame(data)

        column_map = {
            "date": "date",
        }

        cleaner = TransactionCleaner(column_map)
        result_df = cleaner.clean(df)

        assert result_df["date"].tolist() == [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3), date(2023, 1, 1), date(2023, 1, 1), date(2023, 1, 1)]

    def test_clean_with_missing_columns(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
        }
        df = pd.DataFrame(data)

        column_map = {
            "Date": "date",
            "Description": "description",
            "Amount": "amount",
            "currency": "",
            "balance": "",
        }

        cleaner = TransactionCleaner(column_map)
        result_df = cleaner.clean(df)

        # Check that missing columns are added with default values
        assert "currency" in result_df.columns
        assert "balance" in result_df.columns
        assert result_df["currency"].iloc[0] == ""
        assert pd.isna(result_df["balance"].iloc[0])
