from fastapi import APIRouter, Depends, HTTPException  # 导入路由类、依赖注入、异常类
from sqlalchemy.orm import Session  # 导入会话类型
from typing import List  # 导入列表类型
from app.database import get_db  # 导入数据库会话依赖
from app.models.category import Category  # 导入分类模型
from app.schemas.category import CategoryCreate, CategoryResponse  # 导入分类数据结构

router = APIRouter(prefix="/categories", tags=['分类'])


@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """创建分类"""
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)  # 添加到会话
    db.commit()  # 提交事务
    db.refresh(db_category)  # 刷新对象
    return db_category


@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类列表"""
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取指定分类详情"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """更新分类"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    db_category.name = category.name  # 更新名称
    db_category.description = category.description  # 更新描述
    db.commit()  # 提交事务
    db.refresh(db_category)  # 刷新对象
    return db_category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """删除分类"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(db_category)  # 删除对象
    db.commit()  # 提交事务
    return {"detail": "分类已删除"}