from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Source
from ..schemas import SourceCreate

class SourcesRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Source]:
        return self.db.query(Source).offset(skip).limit(limit).all()
    
    def get_by_id(self, source_id: int) -> Optional[Source]:
        return self.db.query(Source).filter(Source.id == source_id).first()

    def get_by_name(self, source_name: str) -> Optional[Source]:
        return self.db.query(Source).filter(Source.name == source_name).first()
    
    def create(self, source: SourceCreate) -> Source:
        db_source = Source(name=source.name, description=source.description)
        self.db.add(db_source)
        self.db.commit()
        return db_source
    
    def update(self, source: Source) -> Source:
        self.db.add(source)
        self.db.commit()
        return source
    
    def delete(self, source: Source) -> None:
        self.db.delete(source)
        self.db.commit()