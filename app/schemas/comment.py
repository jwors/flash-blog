from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
	content: str


class CommentCreate(CommentBase):
	author_id: int
	post_id: int
	parent_id: Optional[int] = None  # 可选的父评论ID，表示这是一个回复

class CommentResponse(CommentBase):
	id: int
	created_at: datetime
	author_id: int
	post_id: int

	class Config:
		from_attributes = True