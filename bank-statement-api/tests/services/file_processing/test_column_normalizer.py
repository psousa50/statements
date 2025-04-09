import numpy as np
import pandas as pd
import pytest

from src.app.services.file_processing.column_normalizer import ColumnNormalizer


class TestColumnNormalizer:
    def test_normalize_standard_columns(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
            "Currency": ["EUR", "EUR"],
            "Balance": [1000.00, 950.00],
        }
        df = pd.DataFrame(data)

        normalizer = ColumnNormalizer()
        column_map = normalizer.normalize_columns(df)

        expected_map = {
            "Date": "date",
            "Description": "description",
            "Amount": "amount",
            "Currency": "currency",
            "Balance": "balance",
        }
        assert column_map == expected_map

    def test_normalize_non_standard_column_names(self):
        data = {
            "Transaction Date": ["2023-01-01", "2023-01-02"],
            "Transaction Details": ["Salary", "Groceries"],
            "Debit/Credit": [1000.00, -50.00],
            "Curr.": ["EUR", "EUR"],
            "Available Balance": [1000.00, 950.00],
        }
        df = pd.DataFrame(data)

        normalizer = ColumnNormalizer()
        column_map = normalizer.normalize_columns(df)

        expected_map = {
            "Transaction Date": "date",
            "Transaction Details": "description",
            "Debit/Credit": "amount",
            "Curr.": "currency",
            "Available Balance": "balance",
        }
        assert column_map == expected_map

    def test_normalize_with_missing_columns(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Amount": [1000.00, -50.00],
        }
        df = pd.DataFrame(data)

        normalizer = ColumnNormalizer()
        column_map = normalizer.normalize_columns(df)

        expected_map = {
            "Date": "date",
            "Description": "description",
            "Amount": "amount",
            "currency": "",
            "balance": "",
        }
        assert column_map == expected_map

    def test_normalize_with_multiple_possible_matches(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Transaction Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Details": ["Salary payment", "Grocery shopping"],
            "Amount": [1000.00, -50.00],
            "Value": [1000.00, -50.00],
        }
        df = pd.DataFrame(data)

        normalizer = ColumnNormalizer()
        column_map = normalizer.normalize_columns(df)

        expected_map = {
            "Date": "date",
            "Transaction Date": "date",
            "Description": "description",
            "Details": "description",
            "Amount": "amount",
            "Value": "amount",
            "currency": "",
            "balance": "",
        }
        assert column_map == expected_map

    def test_normalize_with_separate_debit_credit_columns(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Description": ["Salary", "Groceries", "Rent"],
            "Debit": [0.00, 50.00, 500.00],  # Money going out
            "Credit": [1000.00, 0.00, 0.00],  # Money coming in
            "Balance": [1000.00, 950.00, 450.00],
        }
        df = pd.DataFrame(data)

        normalizer = ColumnNormalizer()
        column_map = normalizer.normalize_columns(df)

        expected_map = {
            "Date": "date",
            "Description": "description",
            "Debit": "amount",
            "Credit": "amount",
            "Balance": "balance",
            "currency": "",
        }
        assert column_map == expected_map
