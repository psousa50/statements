from typing import Optional

import pandas as pd

from src.app.services.file_processing.parsers.statement_parser import StatementParser


class ExcelParser(StatementParser):
    def parse(self, file_path: str, sheet_name: Optional[str] = 0) -> pd.DataFrame:
        """
        Parse an Excel file and return a pandas DataFrame.

        Args:
            file_path: Path to the Excel file
            sheet_name: Optional name or index of the sheet to read.
                        Defaults to 0 (first sheet).

        Returns:
            pandas DataFrame containing the Excel data
        """
        # Read the Excel file directly into a pandas DataFrame
        # Use sheet_name=0 by default to get the first sheet as a DataFrame
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        return df
