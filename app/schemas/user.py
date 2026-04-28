from pydantic import BaseModel, EmailStr  # 导入Pydantic基类和邮箱验证类型
from datetime import datetime  # 导入日期时间类型


class UserBase(BaseModel):
    """用户基础数据结构，包含公共字段"""
    email: EmailStr  # 邮箱地址，EmailStr自动验证邮箱格式（如必须有@符号）
    username: str  # 用户名，普通字符串


class UserCreate(UserBase):
    """用户创建请求数据结构，继承基础字段并添加密码"""
    password: str  # 用户密码，接收明文密码后加密存储


class UserResponse(UserBase):
    """用户响应数据结构，返回给API调用者"""
    id: int  # 用户ID，数据库自增生成
    created_at: datetime  # 创建时间，数据库自动生成
    # 注意：不包含password字段，安全考虑不暴露密码哈希

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy模型对象，自动提取字段值；
        # 原名orm_mode，Pydantic v2更名为from_attributes