import re
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import File, HTTPException, Query, UploadFile

from ..models import Source, Transaction
from ..repositories.sources_repository import SourcesRepository
from ..repositories.transactions_repository import (
    TransactionsFilter,
    TransactionsRepository,
)
from ..schemas import FileUploadResponse
from ..schemas import Transaction as TransactionSchema
from ..schemas import TransactionCreate
from ..services.categorizer import TransactionCategorizer


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

        for _, row in df.iterrows():
            try:
                date_str = row["date"]
                if pd.isna(date_str):
                    continue

                transaction_date = None
                date_formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%d-%m-%Y",
                    "%m/%d/%Y",
                    "%d/%m/%Y",
                    "%Y/%m/%d",
                ]

                if isinstance(date_str, str):
                    for date_format in date_formats:
                        try:
                            transaction_date = datetime.strptime(
                                date_str, date_format
                            ).date()
                            break
                        except ValueError:
                            continue
                elif isinstance(date_str, datetime):
                    transaction_date = date_str.date()

                if transaction_date is None:
                    continue

                description = row["description"]
                if pd.isna(description):
                    continue
                description = str(description)
                normalized_description = self.normalize_description(description)

                amount = row["amount"]
                if pd.isna(amount):
                    continue

                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    amount_str = str(amount).replace(",", ".").strip()
                    amount_str = re.sub(r"[^\d.-]", "", amount_str)
                    try:
                        amount = float(amount_str)
                    except ValueError:
                        continue

                try:
                    filter = TransactionsFilter(
                        start_date=transaction_date,
                        end_date=transaction_date,
                        source_id=source_id,
                        search=description,
                    )
                    existing_transaction = self.transactions_repository.get_all(
                        filter
                    )

                    if existing_transaction:
                        skipped_count += 1
                        continue
                except Exception as e:
                    print(f"Error checking for duplicate transaction: {str(e)}")

                new_transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    normalized_description=normalized_description,
                    amount=amount,
                    currency="EUR",
                    source_id=source_id,
                )

                if "currency" in row and pd.notna(row["currency"]):
                    new_transaction.currency = str(row["currency"])

                try:
                    category_id, confidence = self.categorizer.categorize_transaction(
                        description
                    )
                    print(
                        f"Categorization category ID: {category_id} with confidence: {confidence}"
                    )
                    if category_id is not None:
                        new_transaction.category_id = category_id
                except Exception as e:
                    print(f"Error categorizing transaction: {str(e)}")

                transactions.append(new_transaction)

            except Exception as e:
                print(f"Error processing row: {row}. Error: {str(e)}")

        return transactions, skipped_count

    async def upload_file(
        self,
        df: pd.DataFrame,
        source_id: Optional[int] = Query(None),
    ):

        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ["date", "data", "transaction date", "transaction_date"]:
                column_mapping[col] = "date"
            elif col_lower in ["description", "desc", "details", "transaction", "memo"]:
                column_mapping[col] = "description"
            elif col_lower in ["amount", "value", "sum", "total"]:
                column_mapping[col] = "amount"
            elif col_lower in ["currency", "curr"]:
                column_mapping[col] = "currency"

        if column_mapping:
            df = df.rename(columns=column_mapping)
            print(f"Renamed columns to: {df.columns.tolist()}")

        required_columns = ["date", "description", "amount"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns. File must contain: {', '.join(required_columns)}",
            )

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
                category_id=transaction.category_id,
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
