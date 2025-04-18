import pandas as pd
import pytest

from src.app.ai.gemini_ai import GeminiAI
from src.app.services.file_processing.column_normalizer import ColumnNormalizer


@pytest.mark.integration
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

        llm_client = GeminiAI()
        normalizer = ColumnNormalizer(llm_client)

        response = normalizer.normalize_columns(df)

        assert response.column_map["date"] == "Date"
        assert response.column_map["description"] == "Description"
        assert response.column_map["amount"] == "Amount"
        assert response.column_map["currency"] == "Currency"
        assert response.column_map["balance"] == "Balance"
        assert response.header_row == 0
        assert response.start_row == 1

    def test_normalize_with_debit_and_credit(self):
        data = {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Salary", "Groceries"],
            "Debit": [1000.00, 50.00],
            "Credit": [500.00, 5.00],
            "Currency": ["EUR", "EUR"],
            "Balance": [1000.00, 950.00],
        }
        df = pd.DataFrame(data)

        llm_client = GeminiAI()
        normalizer = ColumnNormalizer(llm_client)

        response = normalizer.normalize_columns(df)

        assert response.column_map["date"] == "Date"
        assert response.column_map["description"] == "Description"
        assert response.column_map["amount"] == ""
        assert response.column_map["debit_amount"] == "Debit"
        assert response.column_map["credit_amount"] == "Credit"
        assert response.column_map["currency"] == "Currency"
        assert response.column_map["balance"] == "Balance"
        assert response.header_row == 0
        assert response.start_row == 1

    def test_with_portuguese_columns_and_extra_rows(self):
        data = {
            "HISTÓRICO DE CONTA NÚMERO 45621121287": [
                "Moeda:",
                "",
                "Tipo:",
                "Data de:",
                "Data até:",
                "",
                "Data Lanc.",
                "2024-12-02 00:00:00",
                "2024-12-02 00:00:00",
                "2024-12-02 00:00:00",
                "2024-12-02 00:00:00",
                "2024-12-05 00:00:00",
            ],
            "Unnamed: 1": [
                "EUR",
                "",
                "Todos",
                "2024-12-01 00:00:00",
                "2025-05-10 00:00:00",
                "",
                "Data Valor",
                "2024-12-02 00:00:00",
                "2024-12-02 00:00:00",
                "2024-12-02 00:00:00",
                "2024-12-02 00:00:00",
                "2024-12-05 00:00:00",
            ],
            "Unnamed: 2": [
                "",
                "",
                "",
                "",
                "",
                "",
                "Descrição",
                "DD PT67106686 GOLD ENERGY - C 00195433",
                "DD PT67106686 GOLD ENERGY - C 00195433",
                "TRF P/ REAL VIDA",
                "PAG BXVAL- 9078 VIAVERDE",
                "DD PT10100825 VODAFONE PORTUG 07100180668",
            ],
            "Unnamed: 3": [
                "",
                "",
                "",
                "",
                "",
                "",
                "Valor",
                "-27.71",
                "-112.89",
                "-150",
                "-9.4",
                "-123.04",
            ],
            "Unnamed: 4": [
                "",
                "",
                "",
                "",
                "",
                "",
                "Saldo",
                "3014.51",
                "2901.62",
                "2751.62",
                "2742.22",
                "2619.18",
            ],
        }
        df = pd.DataFrame(data)

        llm_client = GeminiAI()
        normalizer = ColumnNormalizer(llm_client)

        response = normalizer.normalize_columns(df)

        assert response.column_map["date"] == "Data Lanc."
        assert response.column_map["description"] == "Descrição"
        assert response.column_map["amount"] == "Valor"
        assert response.column_map["currency"] == ""
        assert response.column_map["balance"] == "Saldo"
        assert response.header_row == 7
        assert response.start_row == 8
