from pydantic import BaseModel  # 导入Pydantic基类
from datetime import datetime  # 导入日期时间类型
from typing import Optional, List  # 导入可选类型和列表类型


class PostBase(BaseModel):
    """文章基础数据结构，包含公共字段"""
    title: str  # 文章标题
    content: str  # 文章正文
    summary: Optional[str] = None  # 文章摘要，可选字段，默认为空


class PostCreate(PostBase):
    """文章创建请求数据结构"""
    author_id: int  # 作者ID，关联用户表
    category_ids: Optional[List[int]] = None  # 分类ID列表，多对多关系，可选


class PostResponse(PostBase):
    """文章响应数据结构，返回给API调用者"""
    id: int  # 文章ID
    created_at: datetime  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间，可能为空（未更新过）
    author_id: int  # 作者ID

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy模型对象，自动提取字段值

class PostListResponse(BaseModel):
    items: List[PostResponse]
    total: int
    page: int
    limit: int
    hasNext: bool

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy模型对象，自动提取字段值

class PostDetailResponse(PostResponse):
    author_name:Optional[str] = None
    categories: List[str] = []