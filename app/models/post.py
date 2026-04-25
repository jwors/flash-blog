from sqlalchemy import Column,Integer,String,Text,DateTime,ForeignKey,Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

  # 文章-分类 多对多关联表
post_categories = Table(
	'post_categories',
	Base.metadata,
	Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
	Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Post(Base):
		__tablename__ = "posts"
		id = Column(Integer, primary_key=True, index=True)
		title = Column(String, index=True)
		content = Column(Text,nullable=False)
		summary = Column(String(200))

		# 外键关联到用户表，表示每篇文章属于一个用户
		author_id = Column(Integer, ForeignKey("users.id"))

		# 时间戳
		created_at = Column(DateTime(timezone=True), server_default=func.now())
		updated_at = Column(DateTime(timezone=True), onupdate=func.now())

		# 关系
		author = relationship("User", back_populates="posts")
		comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
		categories = relationship("Category", secondary="post_categories", back_populates="posts")