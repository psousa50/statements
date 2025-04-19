import hashlib
import json
import logging
import uuid
from typing import Dict, List

import pandas as pd
from fastapi.encoders import jsonable_encoder

from src.app.repositories.statement_repository import StatementRepository
from src.app.repositories.statement_schema_repository import StatementSchemaRepository
from src.app.schemas import (
    ColumnMapping,
    StatementAnalysisResponse,
    StatementSchemaDefinition,
)
from src.app.services.file_processing.column_normalizer import ColumnNormalizer
from src.app.services.file_processing.file_type_detector import (
    FileType,
    FileTypeDetector,
)
from src.app.services.file_processing.parsers.parser_factory import ParserFactory
from src.app.services.file_processing.statement_statistics_calculator import (
    StatementStatisticsCalculator,
)
from src.app.services.file_processing.transactions_builder import (
    StatementTransaction,
    TransactionsBuilder,
)
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner

logger_content = logging.getLogger("app.llm.big")
logger = logging.getLogger("app")


class StatementAnalysisService:
    def __init__(
        self,
        file_type_detector: FileTypeDetector,
        parser_factory: ParserFactory,
        column_normalizer: ColumnNormalizer,
        transaction_cleaner: TransactionsCleaner,
        transactions_builder: TransactionsBuilder,
        statistics_calculator: StatementStatisticsCalculator,
        statement_repository: StatementRepository,
        statement_schema_repository: StatementSchemaRepository,
    ):
        self.file_type_detector = file_type_detector
        self.parser_factory = parser_factory
        self.column_normalizer = column_normalizer
        self.transaction_cleaner = transaction_cleaner
        self.transactions_builder = transactions_builder
        self.statistics_calculator = statistics_calculator
        self.statement_repository = statement_repository
        self.statement_schema_repository = statement_schema_repository

    def analyze_statement(
        self, file_content: bytes, file_name: str
    ) -> StatementAnalysisResponse:
        try:
            statement_id = self.statement_repository.save(file_content, file_name)

            file_type = self.file_type_detector.detect_file_type(file_name)
            parser = self.parser_factory.create_parser(file_type)
            df = parser.parse(file_content)

            conversion_model = self.column_normalizer.normalize_columns(df)

            logger_content.debug(
                json.dumps(jsonable_encoder(conversion_model)),
                extra={
                    "prefix": "statement_analysis_service.conversion_model",
                    "ext": "json",
                },
            )

            statement_hash = self._calculate_statement_hash(
                df.columns.tolist(), file_type
            )

            existing_schema = self.statement_schema_repository.find_by_statement_hash(
                statement_hash
            )
            source_id = None

            if existing_schema:
                schema_data = existing_schema.schema_data

                file_type_value = schema_data.get("file_type")
                if isinstance(file_type_value, int):
                    try:
                        file_type_str = FileType(file_type_value).name
                    except ValueError:
                        file_type_str = str(file_type_value)
                else:
                    file_type_str = str(file_type_value)

                statement_schema = StatementSchemaDefinition(
                    id=existing_schema.id,
                    source_id=schema_data.get("source_id"),
                    file_type=file_type_str,
                    column_mapping=ColumnMapping(
                        **schema_data.get("column_mapping", {})
                    ),
                    start_row=schema_data.get("start_row", 1),
                    header_row=schema_data.get("header_row", 0),
                    column_names=schema_data.get("column_names", []),
                )
                source_id = schema_data.get("source_id")
            else:
                column_names = (
                    df.columns.tolist()
                    if conversion_model.header_row == 0
                    else df.iloc[conversion_model.header_row - 1].tolist()
                )
                logger.debug(
                    column_names,
                    extra={
                        "prefix": "statement_analysis_service.column_names",
                    },
                )

                column_names = [str(col) for col in column_names]

                schema_id = str(uuid.uuid4())
                statement_schema = StatementSchemaDefinition(
                    id=schema_id,
                    source_id=source_id,
                    file_type=file_type.name,
                    column_mapping=ColumnMapping(**conversion_model.column_map),
                    start_row=conversion_model.start_row,
                    header_row=conversion_model.header_row,
                    column_names=column_names,
                )

                schema_data = {
                    "id": schema_id,
                    "source_id": source_id,
                    "file_type": file_type.name,
                    "column_mapping": conversion_model.column_map,
                    "start_row": conversion_model.start_row,
                    "header_row": conversion_model.header_row,
                    "column_names": column_names,
                }

                self.statement_schema_repository.save(
                    {
                        "id": schema_id,
                        "statement_hash": statement_hash,
                        "schema_data": schema_data,
                    }
                )

            cleaned_df = self.transaction_cleaner.clean(df, conversion_model)
            logger_content.debug(
                cleaned_df.to_csv(index=False),
                extra={"prefix": "statement_analysis_service.cleaned_df", "ext": "csv"},
            )

            transactions = self.transactions_builder.build_transactions(cleaned_df)

            statistics = self.statistics_calculator.calc_statistics(transactions)

            preview_df = pd.DataFrame(
                [df.columns.tolist()] + df.iloc[:9].values.tolist()
            )

            preview_rows = []
            for _, row in preview_df.iterrows():
                row_values = []
                for col in preview_df.columns:
                    value = row[col]
                    if pd.isna(value):
                        row_values.append("")
                    else:
                        row_values.append(str(value))
                preview_rows.append(row_values)

            response = StatementAnalysisResponse(
                statementSchema=statement_schema,
                statementId=statement_id,
                totalTransactions=statistics.total_transactions,
                totalAmount=float(statistics.total_amount),
                dateRangeStart=statistics.date_range_start,
                dateRangeEnd=statistics.date_range_end,
                preview_rows=preview_rows,
            )

            return response

        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}")
            raise ValueError(f"Error analyzing file: {str(e)}")

    def _calculate_statement_hash(self, columns: List[str], file_type: FileType) -> str:
        columns_str = ",".join(sorted(columns))
        hash_input = f"{columns_str}|{file_type.name}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def _prepare_preview_rows(
        self, transactions: List[StatementTransaction]
    ) -> List[Dict]:
        return [transaction.model_dump() for transaction in transactions]
