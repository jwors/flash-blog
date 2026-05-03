from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["用户"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
	"""创建用户"""
	pwd_context = CryptContext(schemes=["bcrypt"])
	db_user = User(username=user.username, email=user.email, password=pwd_context.hash(user.password))
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
	"""获取所有用户"""
	return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
	"""获取指定用户"""
	db_user = db.query(User).filter(User.id == user_id).first()
	if not db_user:
		raise HTTPException(status_code=404, detail="用户不存在")
	return db_user