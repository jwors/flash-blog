# 数据模型模块
# 存放所有SQLAlchemy ORM模型类

from app.models.user import User  # 导入用户模型，方便其他模块使用
from app.models.post import Post, post_categories  # 导入文章模型和关联表
from app.models.category import Category  # 导入分类模型
from app.models.comment import Comment  # 导入评论模型

__all__ = ["User", "Post", "Category", "Comment", "post_categories"]
