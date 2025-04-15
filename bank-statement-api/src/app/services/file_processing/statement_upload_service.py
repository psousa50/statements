import json
import logging
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from src.app.repositories.statement_repository import StatementRepository
from src.app.repositories.transactions_repository import TransactionsRepository
from src.app.repositories.statement_schema_repository import StatementSchemaRepository
from src.app.schemas import (
    ColumnMapping,
    FileUploadResponse,
    TransactionCreate,
    UploadFileSpec,
)
from src.app.services.file_processing.conversion_model import ConversionModel
from src.app.services.file_processing.file_type_detector import FileType
from src.app.services.file_processing.parsers.parser_factory import ParserFactory
from src.app.services.file_processing.transactions_builder import (
    StatementTransaction,
    TransactionsBuilder,
)
from src.app.services.file_processing.transactions_cleaner import TransactionsCleaner

logger_content = logging.getLogger("app.llm.big")
logger = logging.getLogger("app")


class StatementUploadService:
    def __init__(
        self,
        parser_factory: ParserFactory,
        transaction_cleaner: TransactionsCleaner,
        transactions_builder: TransactionsBuilder,
        statement_repository: StatementRepository,
        transactions_repository: TransactionsRepository,
        statement_schema_repository: StatementSchemaRepository,
    ):
        self.parser_factory = parser_factory
        self.transaction_cleaner = transaction_cleaner
        self.transactions_builder = transactions_builder
        self.statement_repository = statement_repository
        self.transactions_repository = transactions_repository
        self.statement_schema_repository = statement_schema_repository

    def upload_statement(self, spec: UploadFileSpec) -> FileUploadResponse:
        try:
            statement = self.statement_repository.get_by_id(spec.statement_id)
            if not statement:
                raise ValueError(f"Statement with ID {spec.statement_id} not found")

            file_content = statement["content"]

            file_type_str = spec.statement_schema.file_type
            if file_type_str == "CSV":
                file_type = FileType.CSV
            elif file_type_str == "EXCEL":
                file_type = FileType.EXCEL
            elif file_type_str == "PDF":
                file_type = FileType.PDF
            else:
                file_type = FileType.UNKNOWN

            parser = self.parser_factory.create_parser(file_type)
            df = parser.parse(file_content)

            conversion_model = self._create_conversion_model(
                spec.statement_schema.column_mapping,
                spec.statement_schema.start_row,
                spec.statement_schema.header_row,
            )

            cleaned_df = self.transaction_cleaner.clean(df, conversion_model)

            transactions = self.transactions_builder.build_transactions(cleaned_df)

            duplicates = self.transactions_repository.find_duplicates(transactions)
            unique_transactions = [t for t in transactions if t not in duplicates]

            transaction_creates = self._create_transaction_models(
                unique_transactions, spec.statement_schema.source_id
            )
            created_transactions = self.transactions_repository.create_many(
                transaction_creates
            )

            logger_content.debug(
                jsonable_encoder(spec.statement_schema),
                extra={
                    "prefix": "statement_upload_service.upload_statement.statement_schema",
                    "ext": "json",
                },
            )

            # Prepare the schema data in the format expected by the repository
            schema_data = {
                "id": spec.statement_schema.id,
                "statement_hash": spec.statement_schema.statement_hash,
                "schema_data": jsonable_encoder(spec.statement_schema),
                "statement_id": spec.statement_id
            }

            # Update the schema
            self.statement_schema_repository.update(
                spec.statement_schema.id, schema_data
            )

            response = FileUploadResponse(
                message="File processed successfully",
                transactions_processed=len(unique_transactions),
                transactions=created_transactions,
                skipped_duplicates=len(duplicates),
            )

            return response

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise ValueError(f"Error uploading file: {str(e)}")

    def _determine_file_type(self, file_name: str) -> FileType:
        extension = file_name.split(".")[-1].lower()
        if extension == "csv":
            return FileType.CSV
        elif extension in ["xlsx", "xls"]:
            return FileType.EXCEL
        elif extension == "pdf":
            return FileType.PDF
        else:
            return FileType.UNKNOWN

    def _create_conversion_model(
        self, column_mapping: ColumnMapping, start_row: int, header_row: int = 0
    ) -> ConversionModel:
        column_map = column_mapping.model_dump()
        return ConversionModel(
            column_map=column_map, header_row=header_row, start_row=start_row
        )

    def _create_transaction_models(
        self, transactions: List[StatementTransaction], source_id: Optional[int] = None
    ) -> List[TransactionCreate]:
        actual_source_id = source_id if source_id is not None else 1

        return [
            TransactionCreate(
                date=transaction.date,
                description=transaction.description,
                amount=float(transaction.amount),
                currency=transaction.currency,
                source_id=actual_source_id,
                category_id=None,
                categorization_status="pending",
                normalized_description=self._normalize_description(
                    transaction.description
                ),
            )
            for transaction in transactions
        ]

    def _normalize_description(self, description: str) -> str:
        import re

        if not description:
            return ""

        description = str(description).lower()
        description = re.sub(r"[^\w\s]", " ", description)
        description = re.sub(r"\s+", " ", description).strip()

        return description
