from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
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

    transactions = relationship("Transaction", back_populates="category")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="source")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    description = Column(String)
    normalized_description = Column(String, index=True)
    amount = Column(Numeric(10, 2))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    currency = Column(String, default="EUR")
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)

    category = relationship("Category", back_populates="transactions")
    source = relationship("Source", back_populates="transactions")
