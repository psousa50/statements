import uuid
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models import StatementSchema


class StatementSchemaRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, schema_data: Dict) -> str:
        schema_id = str(uuid.uuid4())
        
        schema = StatementSchema(
            id=schema_id,
            column_hash=schema_data["column_hash"],
            column_mapping=schema_data["column_mapping"],
            file_type=schema_data["file_type"].name if hasattr(schema_data["file_type"], "name") else schema_data["file_type"],
            source_id=schema_data.get("source_id")
        )
        
        if "statement_id" in schema_data:
            schema.statement_id = schema_data["statement_id"]
        
        self.db.add(schema)
        self.db.commit()
        
        return schema_id
    
    def find_by_column_hash(self, column_hash: str) -> Optional[StatementSchema]:
        return self.db.query(StatementSchema).filter(StatementSchema.column_hash == column_hash).first()
    
    def get_by_id(self, schema_id: str) -> Optional[StatementSchema]:
        return self.db.query(StatementSchema).filter(StatementSchema.id == schema_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[StatementSchema]:
        return self.db.query(StatementSchema).order_by(StatementSchema.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(self, schema_id: str, schema_data: Dict) -> Optional[StatementSchema]:
        schema = self.get_by_id(schema_id)
        
        if not schema:
            return None
        
        if "column_mapping" in schema_data:
            schema.column_mapping = schema_data["column_mapping"]
        
        if "file_type" in schema_data:
            schema.file_type = schema_data["file_type"].name if hasattr(schema_data["file_type"], "name") else schema_data["file_type"]
        
        if "source_id" in schema_data:
            schema.source_id = schema_data["source_id"]
        
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
