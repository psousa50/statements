from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import relationship

from .db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, unique=True, index=True)
    parent_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    parent_category = relationship(
        "Category", remote_side=[id], back_populates="subcategories"
    )

    subcategories = relationship("Category", back_populates="parent_category")

    transactions = relationship(
        "Transaction", foreign_keys="Transaction.category_id", back_populates="category"
    )
    sub_transactions = relationship(
        "Transaction", foreign_keys="Transaction.sub_category_id", viewonly=True
    )


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="source")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    dt_created = Column(DateTime, server_default=func.now())
    dt_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sub_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    date = Column(Date, index=True)
    amount = Column(Numeric(10, 2))
    currency = Column(String, default="EUR")
    description = Column(String)
    normalized_description = Column(String, index=True)
    categorization_status = Column(
        Enum("pending", "categorized", "failed", name="categorization_status"),
        default="pending",
        index=True,
    )
    statement_id = Column(String, ForeignKey("statements.id"), nullable=True)

    category = relationship(
        "Category", foreign_keys=[category_id], back_populates="transactions"
    )
    sub_category = relationship("Category", foreign_keys=[sub_category_id])
    source = relationship("Source", back_populates="transactions")
    statement = relationship("Statement", back_populates="transactions")


class Statement(Base):
    __tablename__ = "statements"

    id = Column(String, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    content = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    transactions = relationship("Transaction", back_populates="statement")
    schema = relationship("StatementSchema", back_populates="statement", uselist=False)


class StatementSchema(Base):
    __tablename__ = "statement_schemas"

    id = Column(String, primary_key=True, index=True)
    statement_id = Column(String, ForeignKey("statements.id"), nullable=True)
    statement_hash = Column(String, unique=True, index=True)
    schema_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    statement = relationship("Statement", back_populates="schema")
