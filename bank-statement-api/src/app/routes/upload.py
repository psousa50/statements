from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from ..db import get_db
from ..models import Transaction
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

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Read file content
    file_content = await file.read()
    
    # Detect file format
    file_format = detect_file_format(file_content, file.filename)
    
    # Parse file
    df = parse_file(file_content, file_format)
    
    # Map columns
    df = map_columns(df)
    
    # Create transactions
    transactions = []
    for _, row in df.iterrows():
        transaction = Transaction(
            date=row['date'],
            description=row['description'],
            amount=float(row['amount']),
            currency=row.get('currency', 'EUR')
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
