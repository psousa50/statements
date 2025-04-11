from datetime import datetime
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models import Transaction
from ..schemas import TransactionCreate


@dataclass
class TransactionsFilter:
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    source_id: Optional[int] = None
    search: Optional[str] = None
    categorization_status: Optional[str] = None


class TransactionsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, filter: TransactionsFilter, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        query = self.db.query(Transaction)

        if filter.start_date:
            query = query.filter(Transaction.date >= filter.start_date)
        if filter.end_date:
            query = query.filter(Transaction.date <= filter.end_date)
        if filter.category_id:
            query = query.filter(Transaction.category_id == filter.category_id)
        if filter.sub_category_id:
            query = query.filter(Transaction.sub_category_id == filter.sub_category_id)
        if filter.source_id:
            query = query.filter(Transaction.source_id == filter.source_id)
        if filter.search:
            query = query.filter(Transaction.description.ilike(f"%{filter.search}%"))
        if filter.categorization_status:
            query = query.filter(
                Transaction.categorization_status == filter.categorization_status
            )

        query = query.order_by(Transaction.date.desc())

        return query.offset(skip).limit(limit).all()

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return (
            self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        )

    def get_by_source_id(self, source_id: int):
        return self.db.query(Transaction).filter(Transaction.source_id == source_id)

    def get_by_ids(self, transaction_ids: List[int]) -> List[Transaction]:
        return (
            self.db.query(Transaction).filter(Transaction.id.in_(transaction_ids)).all()
        )

    def create(
        self, transaction: TransactionCreate, auto_commit: bool = True
    ) -> Transaction:
        db_transaction = Transaction(
            dt_created=datetime.now(),
            dt_updated=datetime.now(),
            source_id=transaction.source_id,
            category_id=transaction.category_id,
            sub_category_id=transaction.sub_category_id,
            description=transaction.description,
            amount=transaction.amount,
            currency=transaction.currency,
            date=transaction.date,
            normalized_description=transaction.normalized_description,
            categorization_status=transaction.categorization_status,
        )
        self.db.add(db_transaction)
        if auto_commit:
            self.db.commit()
        return db_transaction

    def update(self, transaction: Transaction) -> Transaction:
        transaction.dt_updated = datetime.now()
        self.db.add(transaction)
        self.db.commit()
        return transaction

    def delete(self, transaction: Transaction) -> None:
        self.db.delete(transaction)
        self.db.commit()

    def commit(self) -> None:
        self.db.commit()

    def get_uncategorized_transactions(
        self, batch_size: int = 100
    ) -> List[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(Transaction.categorization_status == "pending")
            .limit(batch_size)
            .all()
        )

    def update_transaction_category(
        self,
        transaction_id: int,
        category_id: int,
        sub_category_id: Optional[int] = None,
        status: str = "categorized",
    ) -> Transaction:
        transaction = self.get_by_id(transaction_id)
        if transaction:
            transaction.category_id = category_id
            transaction.sub_category_id = sub_category_id
            transaction.categorization_status = status
            self.db.add(transaction)
            self.db.commit()
        return transaction

    def get_unique_normalized_descriptions(
        self, limit: int = 100
    ) -> List[Tuple[str, int]]:
        from sqlalchemy import func

        subquery = (
            self.db.query(
                Transaction.normalized_description,
                Transaction.sub_category_id,
                func.count().label("count"),
            )
            .filter(Transaction.categorization_status == "categorized")
            .filter(Transaction.sub_category_id is not None)
            .group_by(Transaction.normalized_description, Transaction.sub_category_id)
            .subquery()
        )

        query = (
            self.db.query(subquery.c.normalized_description, subquery.c.sub_category_id)
            .distinct(subquery.c.normalized_description)
            .order_by(subquery.c.normalized_description, subquery.c.count.desc())
            .limit(limit)
        )

        return [(result[0], result[1]) for result in query.all()]

    def get_transactions_by_normalized_description(
        self, normalized_description: str, limit: int = 100
    ) -> List[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(Transaction.normalized_description == normalized_description)
            .filter(Transaction.categorization_status == "categorized")
            .filter(Transaction.category_id is not None)
            .order_by(Transaction.date.desc())
            .limit(limit)
            .all()
        )
