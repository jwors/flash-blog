from pydantic import BaseModel, EmailStr  # 导入Pydantic基类和邮箱验证类型
from datetime import datetime  # 导入日期时间类型
from typing import Optional  # 导入可选类型


class UserBase(BaseModel):
    """用户基础数据结构，包含公共字段"""
    email: EmailStr  # 邵箱地址，EmailStr自动验证邮箱格式
    username: str  # 用户名


class UserCreate(UserBase):
    """用户创建请求数据结构"""
    password: str  # 用户密码，接收明文密码后加密存储


class UserUpdate(BaseModel):
    """用户更新请求数据结构，所有字段可选"""
    email: Optional[EmailStr] = None  # 邮箱，可选
    username: Optional[str] = None  # 用户名，可选
    password: Optional[str] = None  # 密码，可选


class UserResponse(UserBase):
    """用户响应数据结构，返回给API调用者"""
    id: int  # 用户ID
    created_at: datetime  # 创建时间

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据