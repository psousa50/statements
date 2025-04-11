import json
import logging

import pandas as pd

from src.app.ai.gemini_ai import GeminiAI
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.file_type_detector import FileTypeDetector
from src.app.services.file_processing.parsers.statement_parser_factory import (
    create_parser,
)
from src.app.services.file_processing.transaction_cleaner import TransactionCleaner

logger_content = logging.getLogger("app.llm.big")


class FileProcessor:

    def process_file(self, file_content: bytes, file_name: str) -> pd.DataFrame:
        file_type = FileTypeDetector().detect_file_type(file_name)
        parser = create_parser(file_type)
        df = parser.parse(file_content)
        logger_content.debug(
            df.to_csv(index=False),
            extra={"prefix": "file_processor.raw"},
        )
        llm_client = GeminiAI()
        conversion_model = ColumnNormalizer(llm_client).normalize_columns(df)
        logger_content.debug(
            json.dumps(conversion_model.__dict__),
            extra={"prefix": "file_processor.conversion_model"},
        )
        df = TransactionCleaner(conversion_model).clean(df)
        logger_content.debug(
            df.to_csv(index=False),
            extra={"prefix": "file_processor.clean"},
        )
        return df
