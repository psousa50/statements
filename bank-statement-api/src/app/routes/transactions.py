from typing import List, Optional, Callable
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Transaction
from ..schemas import Transaction as TransactionSchema
from ..repositories.transactions_repository import TransactionsRepository

class TransactionRouter:
    def __init__(self, transactions_repository: TransactionsRepository, on_change_callback: Optional[Callable[[str, List[Transaction]], None]] = None):
        self.router = APIRouter(
            prefix="/transactions",
            tags=["transactions"],
        )
        self.transaction_repository = transactions_repository
        self.on_change_callback = on_change_callback
        
        # Register routes with trailing slashes removed
        self.router.add_api_route("", self.get_transactions, methods=["GET"], response_model=List[TransactionSchema])
        self.router.add_api_route("/{transaction_id}", self.get_transaction, methods=["GET"], response_model=TransactionSchema)
        self.router.add_api_route("/{transaction_id}/categorize", self.categorize_transaction, methods=["PUT"], response_model=TransactionSchema)
    
    def _notify_change(self, action: str, transactions: List[Transaction]):
        if self.on_change_callback:
            self.on_change_callback(action, transactions)
    
    async def get_transactions(
        self,
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
    
    async def get_transaction(
        self,
        transaction_id: int,
    ):
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    
    async def categorize_transaction(
        self,
        transaction_id: int,
        category_id: int,
    ):
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        transaction.category_id = category_id
        self.transaction_repository.update(transaction)
        
        # Notify about the change
        self._notify_change("update", [transaction])
        
        return transaction
