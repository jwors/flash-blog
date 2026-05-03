from pydantic import BaseModel, EmailStr  # 导入Pydantic基类和邮箱验证类型
# BaseModel: Pydantic模型基类，所有数据结构类都继承它
# EmailStr: 邮箱字符串类型，自动验证邮箱格式（如user@example.com）

from datetime import datetime  # 导入日期时间类型，用于created_at字段
from typing import Optional  # 导入可选类型，用于可选字段定义


class UserBase(BaseModel):
    """用户基础数据结构，包含公共字段

    作用：作为UserCreate和UserResponse的父类，定义用户的公共字段。
    避免在多个类中重复定义email和username字段，符合DRY原则。

    字段:
        - email: 邮箱地址，使用EmailStr类型自动验证格式
        - username: 用户名，普通字符串类型

    验证:
        EmailStr会自动验证邮箱格式，不符合则返回422错误：
        - 必须包含@符号
        - @后必须有域名
        - 示例：invalid-email 会触发验证错误
    """

    email: EmailStr  # 邮箱地址，EmailStr类型自动验证格式
    # EmailStr底层使用email-validator库验证
    # 示例有效邮箱：user@example.com, test@gmail.com

    username: str  # 用户名，字符串类型，无特殊验证


class UserCreate(UserBase):
    """用户创建请求数据结构

    作用：定义用户注册时需要提交的数据格式。
    继承UserBase的email和username字段，额外添加password字段。

    字段:
        - email: 邮箱（继承，必填）
        - username: 用户名（继承，必填）
        - password: 密码（新增，必填）

    安全处理:
        password字段接收明文密码，但在路由中会使用bcrypt加密：
        - 明文密码不存储到数据库
        - 使用passlib的CryptContext进行哈希加密
        - 数据库存储的是加密后的哈希值

    示例请求体:
        {"email": "user@example.com", "username": "张三", "password": "123456"}
    """

    password: str  # 用户密码，接收明文密码，路由中加密后存储
    # 注意：此字段不应出现在响应中（UserResponse不包含password）


class UserUpdate(BaseModel):
    """用户更新请求数据结构，所有字段可选

    作用：定义用户信息更新时可以修改的字段。
    所有字段都是Optional（可选），允许客户端只更新部分字段。

    为什么不继承UserBase:
        UserBase的email和username是必填字段，但更新操作应该允许只修改部分字段。
        因此UserUpdate独立定义所有字段为Optional，实现部分更新（PATCH语义）。

    字段:
        - email: 邮箱，可选，不传则不更新
        - username: 用户名，可选，不传则不更新
        - password: 密码，可选，不传则不更新

    使用示例:
        只更新用户名：{"username": "新名字"}  // 其他字段不变
        只修改密码：{"password": "新密码"}    // email和username不变

    路由处理逻辑:
        if user.username is not None:
            db_user.username = user.username  # 只有传了值才更新
    """

    email: Optional[EmailStr] = None  # 邮箱，可选，None表示不更新此字段
    username: Optional[str] = None  # 用户名，可选，None表示不更新
    password: Optional[str] = None  # 密码，可选，None表示不更新
    # 如果传入password，路由会先bcrypt加密再存储


class UserResponse(UserBase):
    """用户响应数据结构，返回给API调用者

    作用：定义API返回的用户数据格式，自动过滤敏感字段（password）。
    继承UserBase的email和username，添加id和created_at字段。

    为什么不包含password:
        安全原因：密码（即使是哈希值）不应返回给客户端。
        UserCreate用于接收密码，UserResponse用于返回数据，两者职责分离。

    字段:
        - id: 用户ID（数据库主键）
        - email: 邮箱（继承）
        - username: 用户名（继承）
        - created_at: 注册时间（数据库自动生成）

    示例响应:
        {"id": 1, "email": "user@example.com", "username": "张三", "created_at": "2026-05-01T10:00:00"}
    """

    id: int  # 用户ID，数据库自增生成的主键，用于唯一标识用户
    created_at: datetime  # 用户注册时间，数据库自动生成的时间戳

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy User对象，
        # 自动提取id、email、username、created_at字段值
        # 示例：UserResponse.from_orm(db_user) 直接将ORM对象转为响应对象