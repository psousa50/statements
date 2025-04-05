from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from ..db import get_db
from ..models import Transaction, Source
from ..schemas import FileUploadResponse, Transaction as TransactionSchema
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

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    source_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
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
    else:
        # Verify that the source exists
        source = db.query(Source).filter(Source.id == source_id).first()
        if source is None:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
    
    # Process transactions
    transactions = []
    for _, row in df.iterrows():
        # Parse date
        try:
            transaction_date = parse_date(row['date'])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {row['date']}")
        
        # Create transaction object
        transaction = Transaction(
            date=transaction_date,
            description=row['description'],
            amount=float(row['amount']),
            currency=row.get('currency', 'EUR'),
            source_id=source_id
        )
        
        db.add(transaction)
        transactions.append(transaction)
    
    db.commit()
    
    # Categorize transactions
    categorizer = TransactionCategorizer(db)
    categorizer.categorize_transactions(transactions)
    
    # Refresh transactions to get updated data
    for transaction in transactions:
        db.refresh(transaction)
    
    return FileUploadResponse(
        message="File processed successfully",
        transactions_processed=len(transactions),
        transactions=transactions
    )
