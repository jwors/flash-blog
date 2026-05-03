# 数据结构模块（Pydantic Schema）
# 作用：定义API的输入输出数据格式，实现请求验证和响应序列化

from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.post import PostBase, PostCreate, PostResponse
from app.schemas.category import CategoryBase, CategoryCreate, CategoryResponse
from app.schemas.comment import CommentBase, CommentCreate, CommentResponse

__all__ = [
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "PostBase", "PostCreate", "PostResponse",
    "CategoryBase", "CategoryCreate", "CategoryResponse",
    "CommentBase", "CommentCreate", "CommentResponse"
]