import pandas as pd

from src.app.ai.groq_ai import GroqAI
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.file_type_detector import FileTypeDetector
from src.app.services.file_processing.parsers.statement_parser_factory import (
    create_parser,
)
from src.app.services.file_processing.transaction_cleaner import TransactionCleaner


class FileProcessor:

    def process_file(self, file_content: bytes, file_name: str) -> pd.DataFrame:
        file_type = FileTypeDetector().detect_file_type(file_name)
        parser = create_parser(file_type)
        df = parser.parse(file_content)
        llm_client = GroqAI()
        column_map = ColumnNormalizer(llm_client).normalize_columns(df)
        df = TransactionCleaner(column_map).clean(df)
        return df
