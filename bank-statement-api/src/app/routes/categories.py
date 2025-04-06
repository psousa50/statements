from typing import List, Callable, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io

from ..db import get_db
from ..models import Category
from ..schemas import Category as CategorySchema, CategoryCreate
from ..repositories.categories_repository import CategoriesRepository

# Callback type for category changes
CategoryChangeCallback = Callable[[str, List[Category]], None]

class CategoryRouter:
    def __init__(self, categories_repository: CategoriesRepository, on_change_callback: Optional[CategoryChangeCallback] = None):
        self.router = APIRouter(
            prefix="/categories",
            tags=["categories"],
        )
        self.categories_repository = categories_repository
        self.on_change_callback = on_change_callback
        
        # Register routes with trailing slashes removed
        self.router.add_api_route("", self.get_categories, methods=["GET"], response_model=List[CategorySchema])
        self.router.add_api_route("/{category_id}", self.get_category, methods=["GET"], response_model=CategorySchema)
        self.router.add_api_route("", self.create_category, methods=["POST"], response_model=CategorySchema)
        self.router.add_api_route("/import", self.import_categories_from_csv, methods=["POST"], status_code=201)
    
    def _notify_change(self, action: str, categories: List[Category]):
        """Notify the callback about a category change"""
        if self.on_change_callback:
            self.on_change_callback(action, categories)
    
    async def get_categories(self):
        categories = self.categories_repository.get_all()
        return categories
    
    async def get_category(self, category_id: int):
        category = self.categories_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    
    async def create_category(self, category: CategoryCreate):
        db_category = self.categories_repository.get_by_name(category.category_name)
        if db_category:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        # Create main category
        new_category = Category(
            category_name=category.category_name,
            parent_category_id=category.parent_category_id
        )
        
        self.categories_repository.create(new_category)
        
        # Notify about the change
        self._notify_change("create", [new_category])
        
        return new_category
    
    async def import_categories_from_csv(self, file: UploadFile = File(...)):
        """Import categories from a CSV file"""
        content = await file.read()
        
        # Parse CSV
        categories_created = []
        try:
            csv_text = content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(csv_text))
            
            # Skip header row if present
            header = next(csv_reader, None)
            if not header or 'category' not in header[0].lower():
                # If no header or doesn't look like a header, reset to start
                csv_reader = csv.reader(io.StringIO(csv_text))
            
            for row in csv_reader:
                if not row or not row[0].strip():
                    continue  # Skip empty rows
                
                main_category_name = row[0].strip()
                
                # Check if main category exists
                main_category = self.categories_repository.get_by_name(main_category_name)
                
                if not main_category:
                    # Create main category
                    main_category = Category(
                        category_name=main_category_name
                    )
                    self.categories_repository.create(main_category, autocommit=False)
                    categories_created.append(main_category)
                
                # Process subcategories if present
                if len(row) > 1 and row[1].strip():
                    # Handle compact format with // separator
                    subcategories = row[1].split("//")
                    
                    for sub_name in subcategories:
                        sub_name = sub_name.strip()
                        if not sub_name:
                            continue
                            
                        # Check if subcategory exists
                        sub = self.categories_repository.get_by_name(sub_name)
                        
                        if not sub:
                            # Create subcategory
                            sub = Category(
                                category_name=sub_name,
                                parent_category_id=main_category.id
                            )
                            self.categories_repository.create(sub, autocommit=False)

            self.categories_repository.commit()
            
            if categories_created:
                self._notify_change("import", categories_created)
            
            return {"message": f"Successfully imported {len(categories_created)} categories"}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error importing categories: {str(e)}")
