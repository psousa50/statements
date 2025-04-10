import re
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import HTTPException, Query

from ..models import Source, Transaction
from ..repositories.sources_repository import SourcesRepository
from ..repositories.transactions_repository import (
    TransactionsFilter,
    TransactionsRepository,
)
from ..schemas import FileUploadResponse
from ..schemas import Transaction as TransactionSchema
from ..schemas import TransactionCreate
from ..services.categorizers.transaction_categorizer import TransactionCategorizer


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

    def map_columns(self, df):
        required_columns = ["date", "description", "amount"]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}",
            )

        return df

    def normalize_description(self, description):
        if pd.isna(description):
            return ""

        description = str(description).lower()

        description = re.sub(r"[^\w\s]", " ", description)
        description = re.sub(r"\s+", " ", description).strip()

        return description

    def process_transactions(self, df, source_id):
        transactions = []
        skipped_count = 0

        for i, row in df.iterrows():
            try:
                description = row["description"]
                if pd.isna(description):
                    continue
                description = str(description)
                normalized_description = self.normalize_description(description)

                transaction_date = row["date"]

                try:
                    filter = TransactionsFilter(
                        start_date=transaction_date,
                        end_date=transaction_date,
                        source_id=source_id,
                        search=description,
                    )
                    existing_transaction = self.transactions_repository.get_all(filter)

                    if existing_transaction:
                        skipped_count += 1
                        continue
                except Exception as e:
                    print(f"Error checking for duplicate transaction: {str(e)}")

                amount = row["amount"]
                if pd.isna(amount):
                    continue

                new_transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    normalized_description=normalized_description,
                    amount=amount,
                    currency="EUR",
                    source_id=source_id,
                    categorization_status="pending",
                )

                if "currency" in row and pd.notna(row["currency"]):
                    new_transaction.currency = str(row["currency"])

                transactions.append(new_transaction)

            except Exception as e:
                print(f"Error processing row: {row}. Error: {str(e)}")

        return transactions, skipped_count

    async def upload_file(
        self,
        df: pd.DataFrame,
        source_id: Optional[int] = Query(None),
    ):
        if source_id is None:
            default_source = self.sources_repository.get_by_name("unknown")
            if default_source is None:
                default_source = Source(
                    name="unknown",
                    description="Default source for transactions with unknown origin",
                )
                self.sources_repository.create(default_source)
            source_id = default_source.id

        transactions, skipped_count = self.process_transactions(df, source_id)
        print(
            f"Processed {len(transactions)} transactions, skipped {skipped_count} duplicates"
        )

        transaction_ids = []
        for transaction in transactions:
            transaction_create = TransactionCreate(
                date=transaction.date,
                description=transaction.description,
                amount=transaction.amount,
                source_id=source_id,
                category_id=None,
                categorization_status="pending",
                normalized_description=transaction.normalized_description,
            )
            db_transaction = self.transactions_repository.create(
                transaction_create, auto_commit=False
            )
            transaction_ids.append(db_transaction.id)

        self.transactions_repository.commit()

        db_transactions = self.transactions_repository.get_by_ids(transaction_ids)

        transaction_schemas = [
            TransactionSchema.model_validate(t, from_attributes=True)
            for t in db_transactions
        ]

        return FileUploadResponse(
            message="File processed successfully",
            transactions_processed=len(transactions),
            transactions=transaction_schemas,
            skipped_duplicates=skipped_count,
        )
