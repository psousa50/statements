import pandas as pd

from src.app.services.file_processing.parsers.statement_parser import StatementParser


class CSVParser(StatementParser):
    def parse(self, file_path: str) -> pd.DataFrame:
        """
        Parse a CSV file and return a pandas DataFrame.

        Args:
            file_path: Path to the CSV file

        Returns:
            pandas DataFrame containing the CSV data
        """
        # Read the CSV file directly into a pandas DataFrame
        df = pd.read_csv(file_path)

        return df
