from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Category
from ..schemas import CategoryCreate


class CategoriesRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.db.query(Category).offset(skip).limit(limit).all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, category_name: str) -> Optional[Category]:
        return (
            self.db.query(Category)
            .filter(Category.category_name == category_name)
            .first()
        )

    def get_parent_category_id(self, sub_category_id: int) -> Optional[int]:
        return (
            self.db.query(Category)
            .filter(Category.id == sub_category_id)
            .first()
            .parent_category_id
        )

    def create(self, category: CategoryCreate, autocommit: bool = True) -> Category:
        db_category = Category(
            category_name=category.category_name,
            parent_category_id=category.parent_category_id,
        )
        self.db.add(db_category)
        if autocommit:
            self.db.commit()
            self.db.refresh(db_category)
        return db_category

    def update(self, category: Category, autocommit: bool = True) -> Category:
        self.db.add(category)
        if autocommit:
            self.db.commit()
        return category

    def delete(self, category: Category, autocommit: bool = True) -> None:
        self.db.delete(category)
        if autocommit:
            self.db.commit()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
