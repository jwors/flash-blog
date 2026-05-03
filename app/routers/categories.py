from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.category import Category
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=['分类'])

class CategoryBase(BaseModel):
	name: str
	description: str = None

class CategoryCreate(CategoryBase):
	pass

class CategoryResponse(BaseModel):
	id: int
	name: str
	description: str = None

	class Config:
		from_attributes = True


@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
	"""创建分类"""
	db_category = Category(name=category.name, description=category.description)
	db.add(db_category)
	db.commit()
	db.refresh(db_category)
	return db_category


@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
	"""获取所有分类"""
	return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
	"""获取指定分类"""
	db_category = db.query(Category).filter(Category.id == category_id).first()
	if not db_category:
		raise HTTPException(status_code=404, detail="分类不存在")
	return db_category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
	"""删除分类"""
	db_category = db.query(Category).filter(Category.id == category_id).first()
	if not db_category:
		raise HTTPException(status_code=404, detail="分类不存在")
	db.delete(db_category)
	db.commit()
	return {"detail": "分类已删除"}