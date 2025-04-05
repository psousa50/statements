from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Transaction
from ..schemas import Transaction as TransactionSchema

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

@router.get("/", response_model=List[TransactionSchema])
def get_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    source_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)
    
    # Apply filters
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if source_id:
        query = query.filter(Transaction.source_id == source_id)
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
    
    # Order by date (most recent first)
    query = query.order_by(Transaction.date.desc())
    
    # Apply pagination
    transactions = query.offset(skip).limit(limit).all()
    
    return transactions

@router.get("/{transaction_id}", response_model=TransactionSchema)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
