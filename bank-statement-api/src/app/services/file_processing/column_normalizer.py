import json
from typing import Dict

import pandas as pd

from src.app.ai.llm_client import LLMClient


class ColumnNormalizer:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def normalize_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        prompt = self.get_prompt(df)
        response = self.llm_client.generate(prompt)
        response = (
            response.strip()
            .replace("\n", "")
            .replace("\r", "")
            .replace("`", "")
            .replace("json", "")
        )
        return self.parse_response(response)

    def parse_response(self, response: str) -> Dict[str, str]:
        return json.loads(response)

    def get_prompt(self, df: pd.DataFrame) -> str:
        return f"""
From this bank statement excerpt, extract the column map and header information in the following format:

{{
  "column_map": {{
    "date": "<column name for date>",
    "description": "<column name for description>",
    "amount": "<column name for amount>",
    "currency": "<column name for currency>",
    "balance": "<column name for balance>"
  }},
  "header_row": "<0-based index of the header row that contains column names>",
  "start_row": "<0-based index of the first row of actual transaction data>"

}}

Guidelines:
	•	Only use actual column names from the transaction table header row (not metadata or sample values).
	•	If a field is missing (e.g. no currency column), set its value to an empty string: "".
	•	header_row is the 0-based index of the row where the column headers (like “Data Lanc.”, “Descrição”, etc.) appear.
	•	start_row is the 0-based index of the first row immediately after the header that contains actual transaction data.
	•	Ignore any metadata rows (like account numbers, date ranges, or currency indicators) and blank rows.
	•	Do not guess or generate column names—only use what’s present in the header row.
	•	Only output valid JSON matching the format above. No explanations. No extra text.

---------------------------------------------------------
{df.to_csv()}
---------------------------------------------------------
"""
