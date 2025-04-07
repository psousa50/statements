from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Transaction
from ..schemas import TransactionCreate

class TransactionsRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction).offset(skip).limit(limit).all()
    
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_by_source_id(self, source_id: int):
        return self.db.query(Transaction).filter(Transaction.source_id == source_id)

    def get_by_ids(self, transaction_ids: List[int]) -> List[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id.in_(transaction_ids)).all()

    def create(self, transaction: TransactionCreate, auto_commit: bool = True) -> Transaction:
        db_transaction = Transaction(
            date=transaction.date,
            description=transaction.description,
            amount=transaction.amount,
            currency=transaction.currency,
            source_id=transaction.source_id,
            category_id=transaction.category_id
        )
        self.db.add(db_transaction)
        if auto_commit:
            self.db.commit()
        return db_transaction
    
    def update(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        return transaction
    
    def delete(self, transaction: Transaction) -> None:
        self.db.delete(transaction)
        self.db.commit()

    def commit(self) -> None:
        self.db.commit()