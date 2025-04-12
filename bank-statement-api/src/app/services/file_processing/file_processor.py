import json
import logging
import uuid
from typing import List

import pandas as pd
from pydantic import BaseModel

from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_type_detector import FileTypeDetector
from src.app.services.file_processing.parsers.statement_parser_factory import (
    create_parser,
)
from src.app.services.file_processing.statement_statistics_calculator import (
    StatementStatistics,
    StatementStatisticsCalculator,
)
from src.app.services.file_processing.transactions_builder import (
    StatementTransaction,
    TransactionsBuilder,
)
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner
from src.app.services.file_processing.file_type_detector import FileType

logger_content = logging.getLogger("app.llm.big")


class ProcessedFile(BaseModel):
    file_id: str
    file_name: str
    file_type: FileType
    conversion_model: ConversionModel
    statistics: StatementStatistics
    transactions: List[StatementTransaction]


class FileProcessor:
    def __init__(
        self,
        file_type_detector: FileTypeDetector,
        column_normalizer: ColumnNormalizer,
        transaction_cleaner: TransactionsCleaner,
        transactions_builder: TransactionsBuilder,
        statistics_calculator: StatementStatisticsCalculator,
    ):
        self.file_type_detector = file_type_detector
        self.column_normalizer = column_normalizer
        self.transaction_cleaner = transaction_cleaner
        self.transactions_builder = transactions_builder
        self.statistics_calculator = statistics_calculator

    def process_file(self, file_content: bytes, file_name: str) -> ProcessedFile:
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

        transactions = self.transactions_builder.build_transactions(df)
        statistics = self.statistics_calculator.calc_statistics(transactions)

        return ProcessedFile(
            file_id=str(uuid.uuid4()),
            file_name=file_name,
            file_type=file_type,
            conversion_model=conversion_model,
            statistics=statistics,
            transactions=transactions,
        )
