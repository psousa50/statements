from typing import List, Callable, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
import csv
import io

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
            raise HTTPException(status_code=409, detail=f"Category {category.category_name} already exists")
        
        # Create the category using the repository
        new_category = self.categories_repository.create(category)
        
        # Notify about the change
        self._notify_change("create", [new_category])
        
        return new_category
    
    async def import_categories_from_csv(self, file: UploadFile = File(...)):
        """Import categories from a CSV file"""
        try:
            contents = await file.read()
            csv_file = io.StringIO(contents.decode('utf-8'))
            csv_reader = csv.reader(csv_file)
            
            # Skip header row
            next(csv_reader)
            
            categories_created = []
            subcategories_to_create = []
            
            # First pass: create all main categories
            for row in csv_reader:
                if not row or not row[0].strip():
                    continue
                
                # Create main category
                main_category_name = row[0].strip()
                main_category = self.categories_repository.get_by_name(main_category_name)
                
                if not main_category:
                    main_category = Category(
                        category_name=main_category_name,
                        parent_category_id=None
                    )
                    main_category = self.categories_repository.create(main_category, autocommit=True)
                    categories_created.append(main_category)
                
                # Store subcategories for later processing
                if len(row) > 1 and row[1].strip():
                    subcategories = row[1].split("|")
                    for sub_name in subcategories:
                        sub_name = sub_name.strip()
                        if sub_name:
                            subcategories_to_create.append((main_category, sub_name))
            
            # Second pass: create all subcategories now that main categories have IDs
            for main_category, sub_name in subcategories_to_create:
                # Create a unique name for the subcategory that includes the parent category
                unique_sub_name = f"{main_category.category_name}: {sub_name}"
                
                # Check if subcategory exists
                sub = self.categories_repository.get_by_name(unique_sub_name)
                
                if not sub:
                    # Create subcategory with parent relationship
                    sub = Category(
                        category_name=unique_sub_name,
                        parent_category_id=main_category.id
                    )
                    sub = self.categories_repository.create(sub, autocommit=True)
                    categories_created.append(sub)
            
            if categories_created:
                self._notify_change("import", categories_created)
            
            return {"message": f"Successfully imported {len(categories_created)} categories"}
            
        except Exception as e:
            self.categories_repository.rollback()
            raise HTTPException(status_code=400, detail=f"Error importing categories: {str(e)}")
