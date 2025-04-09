import pandas as pd
from src.app.services.file_processing.file_type_detector import FileTypeDetector
from src.app.services.file_processing.parsers.statement_parser_factory import create_parser
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.transaction_cleaner import TransactionCleaner


class FileProcessor:
    def process_file(self, file_path: str) -> pd.DataFrame:
        file_type = FileTypeDetector().detect_file_type(file_path)
        parser = create_parser(file_type)
        df = parser.parse(file_path)
        column_map = ColumnNormalizer().normalize_columns(df)
        df = TransactionCleaner().clean(df, column_map)
        return df
        