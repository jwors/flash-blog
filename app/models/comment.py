from sqlalchemy import Column,Integer,String,Text,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Comment(Base):
	__tablename__ = "comments"
	id = Column(Integer, primary_key=True, index=True)
	content = Column(Text, nullable=False)

	# 外键关联到用户表，表示每条评论属于一个用户
	author_id = Column(Integer, ForeignKey("users.id"))

	# 外键关联到文章表，表示每条评论属于一篇文章
	post_id = Column(Integer, ForeignKey("posts.id"))

	# 可选的父评论ID，表示这是一个回复
	parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

	# 时间戳
	created_at = Column(DateTime(timezone=True), server_default=func.now())

	# 关系
	author = relationship("User", back_populates="comments")
	post = relationship("Post", back_populates="comments")

	# 自引用：子评论
	replies = relationship("Comment", backref="parent", remote_side=[id])