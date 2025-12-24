from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.features.categories.models.category import Category
from app.features.categories.schemas.category import CategoryCreate


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: CategoryCreate) -> Category:
        category_data = data.model_dump()
        # Set mock user_id values if not provided
        if category_data.get('created_by') is None:
            category_data['created_by'] = 1  # Mock user_id
        if category_data.get('updated_by') is None:
            category_data['updated_by'] = category_data.get('created_by', 1)  # Mock user_id
        new_category = Category(**category_data)
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name, Category.is_deleted == False).first()

    def get_categories(self) -> List[Category]:
        return self.db.query(Category).filter(Category.is_deleted == False).all()

    def update(self, category_id: int, data: CategoryCreate) -> Optional[Category]:
        category = self.db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
        if not category:
            return None

        category.name = data.name
        # Set mock user_id if not provided
        category.updated_by = data.updated_by if data.updated_by is not None else 1  # Mock user_id
        category.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: int) -> bool:
        category = self.db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
        if not category:
            return False
        category.is_deleted = True
        category.updated_at = datetime.now()
        self.db.commit()
        return True

