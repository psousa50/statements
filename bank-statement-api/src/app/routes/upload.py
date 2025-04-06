from typing import List, Optional, Callable, Tuple
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
import pandas as pd
import io
import re
from datetime import datetime

from ..db import get_db
from ..models import Transaction, Source, Category
from ..schemas import Transaction as TransactionSchema, FileUploadResponse
from ..services.categorizer import TransactionCategorizer

class UploadRouter:
    def __init__(self, get_categorizer: Callable):
        self.get_categorizer = get_categorizer
        self.router = APIRouter(
            prefix="/upload",
            tags=["upload"],
        )
        
        # Register routes
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
            raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing_columns)}")
        
        try:
            df['date'] = pd.to_datetime(df['date']).dt.date
        except Exception:
            raise HTTPException(status_code=400, detail="Error parsing date column")
        
        return df

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format")

    def normalize_description(self, description):
        if not description:
            return ""
        normalized = description.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def process_transactions(self, df, source_id, db: Session):
        transactions = []
        skipped_count = 0
        
        for _, row in df.iterrows():
            try:
                # Parse date
                transaction_date = self.parse_date(str(row['date']))
                
                # Get amount
                amount = float(row['amount'])
                
                # Normalize description
                description = str(row['description'])
                normalized_description = self.normalize_description(description)
                
                # Check for duplicates using the normalized_description field
                existing_transaction = db.query(Transaction).filter(
                    Transaction.date == transaction_date,
                    Transaction.amount == amount,
                    Transaction.source_id == source_id,
                    Transaction.normalized_description == normalized_description
                ).first()
                
                if existing_transaction:
                    skipped_count += 1
                    continue
                
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
                
                # Categorize transaction using the injected categorizer
                try:
                    categorizer = self.get_categorizer(db)
                    category_id, confidence = categorizer.categorize_transaction(description)
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
        db: Session = Depends(get_db)
    ):
        # Debug info
        print(f"Received source_id: {source_id}, type: {type(source_id)}")
        
        # Read file content
        file_content = await file.read()
        
        # Determine file type and parse accordingly
        file_format = self.detect_file_format(file_content, file.filename)
        df = self.parse_file(file_content, file_format)
        
        # Validate required columns
        required_columns = ['date', 'description', 'amount']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns. File must contain: {', '.join(required_columns)}"
            )
        
        # Get default source if source_id is not provided
        if source_id is None:
            default_source = db.query(Source).filter(Source.name == "unknown").first()
            if default_source is None:
                # Create default source if it doesn't exist
                default_source = Source(name="unknown", description="Default source for transactions with unknown origin")
                db.add(default_source)
                db.commit()
                db.refresh(default_source)
            source_id = default_source.id
        
        # Process transactions
        transactions, skipped_count = self.process_transactions(df, source_id, db)
        
        # Save transactions to database
        for transaction in transactions:
            db.add(transaction)
        
        db.commit()
        
        # Convert to schema
        transaction_schemas = [TransactionSchema.model_validate(t, from_attributes=True) for t in transactions]
        
        return FileUploadResponse(
            message="File processed successfully",
            transactions_processed=len(transactions),
            transactions=transaction_schemas,
            skipped_duplicates=skipped_count
        )
