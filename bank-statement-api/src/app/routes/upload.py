from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, Query
import pandas as pd
import io
import re
from datetime import datetime

from ..models import Transaction, Source
from ..schemas import Transaction as TransactionSchema, FileUploadResponse, TransactionCreate
from ..services.categorizer import TransactionCategorizer
from ..repositories.transactions_repository import TransactionsRepository
from ..repositories.sources_repository import SourcesRepository


class TransactionUploadRouter:
    def __init__(self, 
                 transactions_repository: TransactionsRepository, 
                 sources_repository: SourcesRepository, 
                 categorizer: TransactionCategorizer):
        self.transactions_repository = transactions_repository
        self.sources_repository = sources_repository
        self.categorizer = categorizer
        self.router = APIRouter(
            prefix="/upload",
            tags=["upload"],
        )
        
        self.router.add_api_route("", self.upload_file, methods=["POST"], response_model=FileUploadResponse)
    
    def detect_file_format(self, file_content, filename):
        if filename.endswith('.csv'):
            return 'csv'
        elif filename.endswith(('.xls', '.xlsx')):
            return 'excel'
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel files.")

    def parse_file(self, file_content, file_format):
        try:
            if file_format == 'csv':
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_format == 'excel':
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format")
            
            return df
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

    def map_columns(self, df):
        required_columns = ['date', 'description', 'amount']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        return df

    def normalize_description(self, description):
        if pd.isna(description):
            return ""
        
        description = str(description).lower()
        
        # Remove special characters and extra spaces
        description = re.sub(r'[^\w\s]', ' ', description)
        description = re.sub(r'\s+', ' ', description).strip()
        
        return description

    def process_transactions(self, df, source_id):
        transactions = []
        skipped_count = 0
        
        for _, row in df.iterrows():
            try:
                # Extract and validate date
                date_str = row['date']
                if pd.isna(date_str):
                    continue
                
                # Try different date formats
                transaction_date = None
                date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
                
                if isinstance(date_str, str):
                    for date_format in date_formats:
                        try:
                            transaction_date = datetime.strptime(date_str, date_format).date()
                            break
                        except ValueError:
                            continue
                elif isinstance(date_str, datetime):
                    transaction_date = date_str.date()
                
                if transaction_date is None:
                    continue
                
                # Extract and validate description
                description = row['description']
                if pd.isna(description):
                    continue
                description = str(description)
                normalized_description = self.normalize_description(description)
                
                # Extract and validate amount
                amount = row['amount']
                if pd.isna(amount):
                    continue
                
                # Convert amount to float
                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    # Try to handle amount with currency symbols or commas
                    amount_str = str(amount).replace(',', '.').strip()
                    # Extract only digits and decimal point
                    amount_str = re.sub(r'[^\d.-]', '', amount_str)
                    try:
                        amount = float(amount_str)
                    except ValueError:
                        continue
                
                # Check for duplicate transaction
                try:
                    existing_transaction = self.transactions_repository.get_by_source_id(source_id).filter(
                        Transaction.date == transaction_date,
                        Transaction.description == description,
                        Transaction.amount == amount,
                        Transaction.source_id == source_id
                    ).first()
                    
                    if existing_transaction:
                        skipped_count += 1
                        continue
                except Exception as e:
                    print(f"Error checking for duplicate transaction: {str(e)}")
                    # Continue without duplicate check if it fails
                
                # Create new transaction
                new_transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    normalized_description=normalized_description,
                    amount=amount,
                    source_id=source_id
                )
                
                # Add currency if available
                if 'currency' in row and pd.notna(row['currency']):
                    new_transaction.currency = str(row['currency'])
                
                # Categorize transaction using the categorizer
                try:
                    category_id, confidence = self.categorizer.categorize_transaction(description)
                    if category_id is not None:
                        new_transaction.category_id = category_id
                except Exception as e:
                    print(f"Error categorizing transaction: {str(e)}")
                    # Continue without categorization if it fails
                
                transactions.append(new_transaction)
                
            except Exception as e:
                # Log the error but continue processing other rows
                print(f"Error processing row: {row}. Error: {str(e)}")
        
        return transactions, skipped_count

    async def upload_file(
        self,
        file: UploadFile = File(...),
        source_id: Optional[int] = Query(None),
    ):
        # Debug info
        print(f"Received source_id: {source_id}, type: {type(source_id)}")
        
        # Read file content
        file_content = await file.read()
        
        # Determine file type and parse accordingly
        file_format = self.detect_file_format(file_content, file.filename)
        print(f"File format detected: {file_format}")
        
        df = self.parse_file(file_content, file_format)
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        
        # Check if columns need to be normalized
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ['date', 'data', 'transaction date', 'transaction_date']:
                column_mapping[col] = 'date'
            elif col_lower in ['description', 'desc', 'details', 'transaction', 'memo']:
                column_mapping[col] = 'description'
            elif col_lower in ['amount', 'value', 'sum', 'total']:
                column_mapping[col] = 'amount'
            elif col_lower in ['currency', 'curr']:
                column_mapping[col] = 'currency'
        
        # Rename columns if needed
        if column_mapping:
            df = df.rename(columns=column_mapping)
            print(f"Renamed columns to: {df.columns.tolist()}")
        
        # Validate required columns
        required_columns = ['date', 'description', 'amount']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns. File must contain: {', '.join(required_columns)}"
            )
        
        if source_id is None:
            default_source = self.sources_repository.get_by_name("unknown")
            if default_source is None:
                default_source = Source(name="unknown", description="Default source for transactions with unknown origin")
                self.sources_repository.create(default_source)
            source_id = default_source.id
        
        print(f"Using source_id: {source_id}")
        transactions, skipped_count = self.process_transactions(df, source_id)
        print(f"Processed {len(transactions)} transactions, skipped {skipped_count} duplicates")
        
        transaction_ids = []
        for transaction in transactions:
            print(f"Creating transaction: {transaction.date}, {transaction.description}, {transaction.amount}")
            transaction_create = TransactionCreate(
                date=transaction.date,
                description=transaction.description,
                amount=transaction.amount,
                source_id=source_id
            )
            db_transaction = self.transactions_repository.create(transaction_create, auto_commit=False)
            transaction_ids.append(db_transaction.id)
        
        self.transactions_repository.commit()
        
        # Fetch the transactions with their IDs
        db_transactions = self.transactions_repository.get_by_ids(transaction_ids)
        
        transaction_schemas = [TransactionSchema.model_validate(t, from_attributes=True) for t in db_transactions]
        
        return FileUploadResponse(
            message="File processed successfully",
            transactions_processed=len(transactions),
            transactions=transaction_schemas,
            skipped_duplicates=skipped_count
        )
