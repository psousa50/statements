from typing import List, Optional
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

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)

def detect_file_format(file_content, filename):
    if filename.endswith('.csv'):
        return 'csv'
    elif filename.endswith(('.xls', '.xlsx')):
        return 'excel'
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel files.")

def parse_file(file_content, file_format):
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

def map_columns(df):
    # This is a simplified mapping - in a real application, you would need
    # to detect the column mapping or allow the user to specify it
    required_columns = ['date', 'description', 'amount']
    
    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    # Convert date column to datetime
    try:
        df['date'] = pd.to_datetime(df['date']).dt.date
    except Exception:
        raise HTTPException(status_code=400, detail="Error parsing date column")
    
    return df

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format")

def normalize_description(description):
    if not description:
        return ""
    # Convert to lowercase
    normalized = description.lower()
    # Remove punctuation
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    source_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    # Debug info
    print(f"Received source_id: {source_id}, type: {type(source_id)}")
    
    # Read file content
    file_content = await file.read()
    
    # Determine file type and parse accordingly
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
    elif file.filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(io.BytesIO(file_content))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or Excel file.")
    
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
    transactions = []
    skipped_count = 0
    
    for _, row in df.iterrows():
        try:
            # Parse date
            transaction_date = parse_date(row['date'])
            
            # Get amount
            amount = float(row['amount'])
            
            # Normalize description
            description = str(row['description'])
            normalized_description = normalize_description(description)
            
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
                new_transaction.currency = row['currency']
            
            # Categorize transaction
            categorizer = TransactionCategorizer(db)
            category = categorizer.categorize(description)
            if category:
                new_transaction.category_id = category.id
            
            db.add(new_transaction)
            transactions.append(new_transaction)
            
        except Exception as e:
            # Log the error but continue processing other rows
            print(f"Error processing row: {row}. Error: {str(e)}")
    
    # Commit all transactions at once
    if transactions:
        db.commit()
        for transaction in transactions:
            db.refresh(transaction)
    
    # Convert to schema
    transaction_schemas = [TransactionSchema.model_validate(t, from_attributes=True) for t in transactions]
    
    return FileUploadResponse(
        message="File processed successfully",
        transactions_processed=len(transactions),
        transactions=transaction_schemas,
        skipped_duplicates=skipped_count
    )
