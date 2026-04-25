from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
	__tablename__ = "categories"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, index=True)
	description = Column(String(200))


	# 关系
	posts = relationship("Post", secondary="post_categories", back_populates="categories")