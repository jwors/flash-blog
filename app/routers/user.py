from fastapi import APIRouter, Depends, HTTPException  # 导入路由类、依赖注入、异常类
from sqlalchemy.orm import Session  # 导入会话类型
from typing import List  # 导入列表类型
from passlib.context import CryptContext  # 导入密码加密库
from app.database import get_db  # 导入数据库会话依赖
from app.models.user import User  # 导入用户模型
from app.schemas.user import UserCreate, UserResponse, UserUpdate  # 导入用户数据结构

# 密码加密上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(prefix="/users", tags=["用户"])


def get_password_hash(password: str) -> str:
    """生成密码哈希值"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    # 密码加密：使用bcrypt哈希算法加密密码，防止明文存储
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password  # 存储加密后的密码
    )
    db.add(db_user)  # 添加到会话
    db.commit()  # 提交事务，执行INSERT
    db.refresh(db_user)  # 刷新对象，获取数据库生成字段
    return db_user  # 返回用户对象


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """获取所有用户列表"""
    return db.query(User).all()  # 查询User表所有记录


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户详情"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新字段，如果提供了新值则更新
    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email
    if user.password is not None:
        db_user.password = get_password_hash(user.password)  # 密码加密后更新

    db.commit()  # 提交事务，执行UPDATE
    db.refresh(db_user)  # 刷新对象
    return db_user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(db_user)  # 删除对象
    db.commit()  # 提交事务，执行DELETE
    return {"detail": "用户已删除"}