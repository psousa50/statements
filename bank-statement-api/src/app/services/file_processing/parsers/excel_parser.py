from io import BytesIO
from typing import Optional

import pandas as pd

from src.app.services.file_processing.parsers.statement_parser import StatementParser


class ExcelParser(StatementParser):
    def parse(self, file_content: bytes, sheet_name: Optional[str] = 0) -> pd.DataFrame:
        file_obj = BytesIO(file_content)
        df = pd.read_excel(file_obj, sheet_name=sheet_name)

        return df
