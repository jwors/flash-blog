from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey  # 导入SQLAlchemy字段类型
from sqlalchemy.orm import relationship  # 导入关系映射函数
from sqlalchemy.sql import func  # 导入SQL函数
from app.database import Base  # 导入ORM基类


class Comment(Base):  # 评论模型类，继承Base使其成为ORM映射类
    """评论数据模型，对应数据库comments表

    作用：存储用户对文章的评论内容，支持嵌套回复（评论可以回复评论）。
    通过外键关联用户和文章，实现评论的归属和聚合。
    """

    __tablename__ = "comments"  # 指定数据库表名

    id = Column(Integer, primary_key=True, index=True)
    # 主键ID
    # 作用：primary_key=True标记为主键，数据库自动自增；
    # index=True创建索引，加速评论查询

    content = Column(Text, nullable=False)
    # 评论正文内容
    # 作用：Text类型存储长文本，nullable=False强制必须有评论内容

    author_id = Column(Integer, ForeignKey("users.id"))
    # 作者ID外键，关联到用户表
    # 作用：ForeignKey建立数据库约束，确保评论必须关联一个有效用户；
    # comment.author可直接获取评论作者对象

    post_id = Column(Integer, ForeignKey("posts.id"))
    # 文章ID外键，关联到文章表
    # 作用：ForeignKey确保评论必须关联一篇有效文章；
    # comment.post可直接获取评论所属的文章对象

    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    # 父评论ID，用于嵌套回复
    # 作用：自引用外键，一条评论可以回复另一条评论（嵌套结构）；
    # nullable=True表示顶层评论没有父评论（直接评论文章，非回复他人）

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 创建时间
    # 作用：server_default=func.now()让数据库自动生成当前时间戳

    author = relationship("User", back_populates="comments")
    # 评论-作者关系（多对一）
    # 作用：comment.author获取评论作者的用户对象；
    # back_populates="comments"与User.comments形成双向关联

    post = relationship("Post", back_populates="comments")
    # 评论-文章关系（多对一）
    # 作用：comment.post获取评论所属的文章对象；
    # back_populates="comments"与Post.comments形成双向关联

    replies = relationship("Comment", backref="parent", remote_side=[id])
    # 评论-子评论关系（自引用一对多）
    # 作用：自引用关系实现嵌套回复，comment.replies获取该评论的所有回复；
    # remote_side=[id]指定"远端"是id列，区分父子关系（id是父，parent_id是子）；
    # backref="parent"自动创建反向属性，reply.parent可直接获取父评论对象