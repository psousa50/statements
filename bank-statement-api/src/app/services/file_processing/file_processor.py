import json
import logging

import pandas as pd

from src.app.ai.llm_client import LLMClient
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.file_type_detector import FileTypeDetector
from src.app.services.file_processing.parsers.statement_parser_factory import (
    create_parser,
)
from src.app.services.file_processing.transaction_cleaner import TransactionCleaner

from src.app.services.file_processing.conversion_model import ConversionModel


logger_content = logging.getLogger("app.llm.big")


class FileProcessor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def process_file(
        self, file_content: bytes, file_name: str
    ) -> (pd.DataFrame, ConversionModel, list[str]):
        file_type = FileTypeDetector().detect_file_type(file_name)
        parser = create_parser(file_type)
        df = parser.parse(file_content)
        logger_content.debug(
            df.to_csv(index=False),
            extra={"prefix": "file_processor.raw"},
        )
        conversion_model = ColumnNormalizer(self.llm_client).normalize_columns(df)
        logger_content.debug(
            json.dumps(conversion_model.__dict__),
            extra={"prefix": "file_processor.conversion_model"},
        )
        df, column_names = TransactionCleaner(conversion_model).clean(df)
        logger_content.debug(
            df.to_csv(index=False),
            extra={"prefix": "file_processor.clean"},
        )
        return df, conversion_model, column_names
