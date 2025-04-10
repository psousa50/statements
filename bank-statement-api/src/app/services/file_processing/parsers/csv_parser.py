from io import BytesIO

import pandas as pd

from src.app.services.file_processing.parsers.statement_parser import StatementParser


class CSVParser(StatementParser):
    def parse(self, file_content: bytes) -> pd.DataFrame:
        file_obj = BytesIO(file_content)
        df = pd.read_csv(file_obj)

        return df
