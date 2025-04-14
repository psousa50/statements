import uuid
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models import Statement


class StatementRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, file_content: bytes, file_name: str) -> str:
        statement_id = str(uuid.uuid4())
        statement = Statement(
            id=statement_id,
            file_name=file_name,
            content=file_content
        )
        
        self.db.add(statement)
        self.db.commit()
        
        return statement_id
    
    def get_by_id(self, statement_id: str) -> Optional[Dict]:
        statement = self.db.query(Statement).filter(Statement.id == statement_id).first()
        
        if not statement:
            return None
        
        return {
            "id": statement.id,
            "file_name": statement.file_name,
            "content": statement.content,
            "created_at": statement.created_at
        }
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[Statement]:
        return self.db.query(Statement).order_by(Statement.created_at.desc()).offset(skip).limit(limit).all()
    
    def delete(self, statement_id: str) -> bool:
        statement = self.db.query(Statement).filter(Statement.id == statement_id).first()
        
        if not statement:
            return False
        
        self.db.delete(statement)
        self.db.commit()
        
        return True
