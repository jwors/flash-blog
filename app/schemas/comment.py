from pydantic import BaseModel  # 导入Pydantic基类
from datetime import datetime  # 导入日期时间类型
from typing import Optional  # 导入可选类型


class CommentBase(BaseModel):
    """评论基础数据结构，包含公共字段"""
    content: str  # 评论内容


class CommentCreate(CommentBase):
    """评论创建请求数据结构"""
    author_id: int  # 评论作者ID
    post_id: int  # 所属文章ID
    parent_id: Optional[int] = None  # 父评论ID，可选字段，用于嵌套回复


class CommentResponse(CommentBase):
    """评论响应数据结构，返回给API调用者"""
    id: int  # 评论ID
    created_at: datetime  # 创建时间
    author_id: int  # 评论作者ID
    post_id: int  # 所属文章ID

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy模型对象，自动提取字段值