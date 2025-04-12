import json
import logging

import pandas as pd

from src.app.ai.llm_client import LLMClient
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_type_detector import FileTypeDetector
from src.app.services.file_processing.parsers.statement_parser_factory import (
    create_parser,
)
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner

logger_content = logging.getLogger("app.llm.big")


class FileProcessor:
    def __init__(
        self,
        file_type_detector: FileTypeDetector,
        column_normalizer: ColumnNormalizer,
        transaction_cleaner: TransactionsCleaner,
    ):
        self.file_type_detector = file_type_detector
        self.column_normalizer = column_normalizer
        self.transaction_cleaner = transaction_cleaner

    def process_file(
        self, file_content: bytes, file_name: str
    ) -> (pd.DataFrame, ConversionModel, list[str]):
        file_type = self.file_type_detector.detect_file_type(file_name)
        parser = create_parser(file_type)
        df = parser.parse(file_content)
        logger_content.debug(
            df.to_csv(index=False),
            extra={"prefix": "file_processor.raw", "ext": "csv"},
        )
        conversion_model = self.column_normalizer.normalize_columns(df)
        logger_content.debug(
            json.dumps(conversion_model.__dict__),
            extra={"prefix": "file_processor.conversion_model", "ext": "json"},
        )
        df = self.transaction_cleaner.clean(df, conversion_model)
        logger_content.debug(
            df.to_csv(index=False),
            extra={"prefix": "file_processor.clean", "ext": "csv"},
        )
        return df, conversion_model
