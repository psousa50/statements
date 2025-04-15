import logging
import re

import pandas as pd

from ..models import Source
from ..repositories.sources_repository import SourcesRepository
from ..repositories.transactions_repository import (
    TransactionsFilter,
    TransactionsRepository,
)
from ..schemas import FileUploadResponse
from ..schemas import Transaction as TransactionSchema
from ..schemas import TransactionCreate
from ..services.categorizers.transaction_categorizer import TransactionCategorizer
from ..services.file_processing.file_processor import ProcessedFile

logger = logging.getLogger("app")


class TransactionUploader:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        sources_repository: SourcesRepository,
        categorizer: TransactionCategorizer,
    ):
        self.transactions_repository = transactions_repository
        self.sources_repository = sources_repository
        self.categorizer = categorizer

    def normalize_description(self, description):
        if pd.isna(description):
            return ""

        description = str(description).lower()

        description = re.sub(r"[^\w\s]", " ", description)
        description = re.sub(r"\s+", " ", description).strip()

        return description

    def process_transactions(self, processed_file: ProcessedFile):
        new_transactions = []
        for transaction in processed_file.transactions:
            filter = TransactionsFilter(
                start_date=transaction.date,
                end_date=transaction.date,
                source_id=processed_file.source_id,
                search=transaction.description,
            )
            existing_transaction = self.transactions_repository.get_all(filter)

            if not existing_transaction:
                new_transaction = TransactionCreate(
                    date=transaction.date,
                    description=transaction.description,
                    normalized_description=self.normalize_description(
                        transaction.description
                    ),
                    amount=transaction.amount,
                    currency=transaction.currency,
                    source_id=processed_file.source_id,
                    category_id=None,
                    categorization_status="pending",
                )

                new_transactions.append(new_transaction)

        return new_transactions

    async def upload_file(
        self,
        processed_file: ProcessedFile,
        auto_categorize: bool = False,
    ):
        if processed_file.source_id is None:
            default_source = self.sources_repository.get_by_name("unknown")
            if default_source is None:
                default_source = Source(
                    name="unknown",
                    description="Default source for transactions with unknown origin",
                )
                self.sources_repository.create(default_source)
            processed_file.source_id = default_source.id

        new_transactions = self.process_transactions(processed_file)
        skipped_count = len(processed_file.transactions) - len(new_transactions)
        logger.info(
            f"Processed {len(new_transactions)} transactions, skipped {skipped_count} duplicates"
        )

        transaction_ids = []
        try:
            for transaction in new_transactions:
                db_transaction = self.transactions_repository.create(
                    transaction, auto_commit=False
                )
                transaction_ids.append(db_transaction.id)

            self.transactions_repository.commit()
        except:
            self.transactions_repository.rollback()
            raise

        db_transactions = self.transactions_repository.get_by_ids(transaction_ids)

        transaction_schemas = [
            TransactionSchema.model_validate(t, from_attributes=True)
            for t in db_transactions
        ]

        response = FileUploadResponse(
            message="File processed successfully",
            transactions_processed=len(new_transactions),
            transactions=transaction_schemas,
            skipped_duplicates=skipped_count,
        )

        if auto_categorize and transaction_ids:
            from ..tasks.categorization import manually_trigger_categorization

            task = manually_trigger_categorization(batch_size=100)
            response.categorization_task_id = task.id
            response.message = (
                "File processed successfully and categorization triggered"
            )

        return response
