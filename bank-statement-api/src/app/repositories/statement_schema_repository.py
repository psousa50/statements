import uuid
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models import StatementSchema


class StatementSchemaRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, schema_data: Dict) -> str:
        schema_id = schema_data.get("id", str(uuid.uuid4()))
        
        schema = StatementSchema(
            id=schema_id,
            statement_hash=schema_data["statement_hash"],
            schema_data=schema_data["schema_data"],
        )
        
        if "statement_id" in schema_data:
            schema.statement_id = schema_data["statement_id"]
        
        self.db.add(schema)
        self.db.commit()
        
        return schema_id
    
    def find_by_statement_hash(self, statement_hash: str) -> Optional[StatementSchema]:
        return self.db.query(StatementSchema).filter(StatementSchema.statement_hash == statement_hash).first()
    
    def get_by_id(self, schema_id: str) -> Optional[StatementSchema]:
        return self.db.query(StatementSchema).filter(StatementSchema.id == schema_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[StatementSchema]:
        return self.db.query(StatementSchema).order_by(StatementSchema.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(self, schema_id: str, schema_data: Dict) -> Optional[StatementSchema]:
        schema = self.get_by_id(schema_id)
        
        if not schema:
            return None
        
        if "schema" in schema_data:
            schema.schema_data = schema_data["schema"]
        
        if "statement_id" in schema_data:
            schema.statement_id = schema_data["statement_id"]
        
        self.db.commit()
        
        return schema
    
    def delete(self, schema_id: str) -> bool:
        schema = self.get_by_id(schema_id)
        
        if not schema:
            return False
        
        self.db.delete(schema)
        self.db.commit()
        
        return True
