import json
from src.app.ai.groq_ai import GroqAI
import pandas as pd
from dataclasses import asdict

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
        df.to_csv("output.csv", index=False)
        llm_client = GroqAI()
        conversion_model = ColumnNormalizer(llm_client).normalize_columns(df)
        open("conversion_model.json", "w").write(json.dumps(asdict(conversion_model)))
        df = TransactionCleaner(conversion_model).clean(df)
        df.to_csv("output2.csv", index=False)
        return df
