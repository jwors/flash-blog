from pydantic import BaseModel  # 导入Pydantic基类，用于数据验证和序列化
from datetime import datetime  # 导入日期时间类型，用于created_at字段
from typing import Optional  # 导入可选类型，用于可选字段定义


class CommentBase(BaseModel):
    """评论基础数据结构，包含公共字段

    作用：作为CommentCreate和CommentResponse的父类，定义评论的核心字段。
    评论只有一个核心字段content（内容），其他字段（author、post、parent）是关联关系。

    字段:
        - content: 评论正文内容，字符串类型

    注意:
        评论内容不应过长，一般限制在几百字符内（实际项目中应添加长度验证）
    """

    content: str  # 评论正文内容，必填字段


class CommentCreate(CommentBase):
    """评论创建请求数据结构

    作用：定义创建评论时客户端需要提交的数据格式。
    继承CommentBase的content字段，额外添加关联字段。

    字段:
        - content: 评论内容（继承，必填）
        - author_id: 评论作者ID（必填）
        - post_id: 所属文章ID（必填）
        - parent_id: 父评论ID（可选，用于嵌套回复）

    嵌套回复说明:
        - parent_id=None: 顶层评论，直接评论文章
        - parent_id=123: 回复ID为123的评论（嵌套结构）
        前端根据parent_id构建评论树，显示回复关系。

    示例请求体:
        顶层评论: {"content": "好文章！", "author_id": 1, "post_id": 5}
        回复评论: {"content": "同意", "author_id": 2, "post_id": 5, "parent_id": 10}
    """

    author_id: int  # 评论作者ID，关联users表的主键
    post_id: int  # 所属文章ID，关联posts表的主键
    parent_id: Optional[int] = None  # 父评论ID，可选字段，用于嵌套回复
    # parent_id=None表示这是顶层评论（直接评论文章，不是回复其他评论）
    # parent_id有值表示这是回复评论（回复某条已有评论）


class CommentResponse(CommentBase):
    """评论响应数据结构，返回给API调用者

    作用：定义API返回的评论数据格式。
    继承CommentBase的content字段，添加数据库生成的字段和关联ID。

    字段:
        - id: 评论ID（数据库主键）
        - content: 评论内容（继承）
        - created_at: 评论时间（数据库自动生成）
        - author_id: 作者ID
        - post_id: 文章ID

    注意:
        响应不包含parent_id字段，客户端需通过其他方式获取评论树结构。
        实际项目中可能需要添加author_name字段显示评论者名称。

    示例响应:
        {"id": 1, "content": "好文章！", "created_at": "2026-05-01T10:00:00", "author_id": 1, "post_id": 5}
    """

    id: int  # 评论ID，数据库自增生成的主键
    created_at: datetime  # 评论创建时间，数据库自动生成的时间戳
    author_id: int  # 评论作者ID，可通过relationship获取作者详情
    post_id: int  # 所属文章ID，可通过relationship获取文章详情

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy Comment对象，
        # 自动提取id、content、created_at、author_id、post_id字段值