from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io

from ..db import get_db
from ..models import Category
from ..schemas import Category as CategorySchema, CategoryCreate

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

@router.get("/", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@router.get("/{category_id}", response_model=CategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategorySchema)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category_name == category.category_name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.post("/import", status_code=201)
def import_categories_from_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import categories from a CSV file.
    
    The CSV should have two columns:
    - category: The main category name
    - sub_categories: Subcategories separated by pipe (|) characters
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Read the CSV file
    contents = file.file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(contents))
    
    # Process the categories
    result = {
        "categories_created": 0,
        "subcategories_created": 0,
        "errors": []
    }
    
    # First pass: Create all main categories
    main_categories = {}
    for row in csv_reader:
        if 'category' not in row or not row['category']:
            result["errors"].append(f"Missing category in row: {row}")
            continue
        
        category_name = row['category'].strip()
        
        # Check if category already exists
        db_category = db.query(Category).filter(Category.category_name == category_name).first()
        if not db_category:
            # Create new category
            db_category = Category(category_name=category_name, parent_category_id=None)
            db.add(db_category)
            db.flush()  # Get the ID without committing
            result["categories_created"] += 1
        
        main_categories[category_name] = db_category.id
    
    # Reset file pointer to beginning for second pass
    file.file.seek(0)
    contents = file.file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(contents))
    
    # Second pass: Create subcategories
    for row in csv_reader:
        if 'category' not in row or 'sub_categories' not in row:
            continue
        
        category_name = row['category'].strip()
        if category_name not in main_categories:
            continue
        
        parent_id = main_categories[category_name]
        
        # Process subcategories
        if row['sub_categories']:
            subcategories = row['sub_categories'].split('|')
            for subcategory_name in subcategories:
                subcategory_name = subcategory_name.strip()
                if not subcategory_name:
                    continue
                
                # Check if subcategory already exists
                db_subcategory = db.query(Category).filter(
                    Category.category_name == subcategory_name
                ).first()
                
                if not db_subcategory:
                    # Create new subcategory
                    db_subcategory = Category(
                        category_name=subcategory_name,
                        parent_category_id=parent_id
                    )
                    db.add(db_subcategory)
                    result["subcategories_created"] += 1
                elif db_subcategory.parent_category_id != parent_id:
                    # Update parent if different
                    db_subcategory.parent_category_id = parent_id
    
    # Commit all changes
    db.commit()
    
    return result
