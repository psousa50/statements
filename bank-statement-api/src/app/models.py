from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship

from .db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, unique=True, index=True)
    parent_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    transactions = relationship("Transaction", back_populates="category")
    subcategories = relationship("Category", 
                              backref="parent_category",
                              remote_side=[id])


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
    amount = Column(Numeric(10, 2))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    currency = Column(String, default="EUR")
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    
    category = relationship("Category", back_populates="transactions")
    source = relationship("Source", back_populates="transactions")
