import json
import logging

import pandas as pd

from src.app.ai.llm_client import LLMClient
from src.app.common.json_utils import sanitize_json
from src.app.services.file_processing.conversion_model import ConversionModel

logger_content = logging.getLogger("app.llm.big")


class ColumnNormalizer:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def normalize_columns(self, df: pd.DataFrame) -> ConversionModel:
        prompt = self.get_prompt(df)
        response = self.llm_client.generate(prompt)
        logger_content.debug(
            response,
            extra={"prefix": "column_normalizer.response", "ext": "json"},
        )
        json_result = sanitize_json(response)
        logger_content.debug(
            json.dumps(json_result),
            extra={"prefix": "column_normalizer.json_result", "ext": "json"},
        )
        if not json_result:
            raise ValueError("Invalid JSON response")
        conversion_model: ConversionModel = ConversionModel(**json_result)
        logger_content.debug(
            json.dumps(conversion_model.__dict__),
            extra={"prefix": "column_normalizer.conversion_model", "ext": "json"},
        )
        return conversion_model

    def get_prompt(self, df: pd.DataFrame) -> str:
        return f"""
From this bank statement excerpt, extract the column map and header information in the following format:

{{
  "column_map": {{
    "date": "<column name for date>",
    "description": "<column name for description>",
    "amount": "<column name for amount>",
    "debit_amount": "<column name for debit amount>",
    "credit_amount": "<column name for credit amount>",
    "currency": "<column name for currency>",
    "balance": "<column name for balance>"
  }},
  "header_row": <0-based index of the header row>,
  "start_row": <0-based index of the first row of actual transaction data>
}}

Guidelines:
	•	Only use actual column names from the transaction table header row (not metadata or sample values).
	•	If a field is missing (e.g. no currency column), set its value to an empty string: "".
	•	header_row is the 0-based index of the row where the column headers (like “Date”, “Description”, etc.) appear.
	•	start_row is the 0-based index of the first row after the header that contains actual transaction data.
	•	Do not guess or generate column names—only use what’s present in the header row.
	•	Only output valid JSON matching the format above. No explanations. No extra text.
	•	Transaction rows contain actual dates and amounts; ignore rows that have empty fields, labels, or static information.

Example:
---------------------------------------------------------
Account Statement,,,,,
Currency: EUR,,,,,
Date Range: 2023-01-01 to 2023-01-31,,,,,

Transaction Date,Value Date,Details,Amount,Balance
2023-01-01,2023-01-01,Coffee Shop,-3.50,996.50
2023-01-02,2023-01-02,Grocery Store,-25.00,971.50

---------------------------------------------------------

{{
  "column_map": {{
    "date": "Transaction Date",
    "description": "Details",
    "amount": "Amount",
    "debit_amount": "",
    "credit_amount": "",
    "currency": "",
    "balance": "Balance"
  }},
  "header_row": 4,
  "start_row": 5
}}


---------------------------------------------------------
{df.iloc[:10].to_csv(index=False)}
---------------------------------------------------------
"""
