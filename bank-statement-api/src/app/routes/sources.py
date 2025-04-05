from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db import get_db
from src.app.models import Source
from src.app.schemas import Source as SourceSchema, SourceCreate

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
)


@router.get("/", response_model=List[SourceSchema])
def get_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all sources with pagination
    """
    sources = db.query(Source).offset(skip).limit(limit).all()
    return sources


@router.get("/{source_id}", response_model=SourceSchema)
def get_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific source by ID
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.post("/", response_model=SourceSchema)
def create_source(
    source: SourceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new source
    """
    # Check if source with the same name already exists
    db_source = db.query(Source).filter(Source.name == source.name).first()
    if db_source:
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    
    # Create new source
    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.put("/{source_id}", response_model=SourceSchema)
def update_source(
    source_id: int,
    source: SourceCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing source
    """
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Check if another source with the same name already exists
    existing_source = db.query(Source).filter(Source.name == source.name, Source.id != source_id).first()
    if existing_source:
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    
    # Update source
    for key, value in source.model_dump().items():
        setattr(db_source, key, value)
    
    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/{source_id}", response_model=SourceSchema)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a source
    """
    # Don't allow deleting the default 'unknown' source
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if db_source.name == "unknown":
        raise HTTPException(status_code=400, detail="Cannot delete the default 'unknown' source")
    
    # Check if any transactions are using this source
    if db_source.transactions:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete source that is used by transactions. Update transactions to use a different source first."
        )
    
    db.delete(db_source)
    db.commit()
    return db_source
