from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PostBase(BaseModel):
	title: str
	content: str
	summary: Optional[str] = None

class PostCreate(PostBase):
	author_id: int

class PostResponse(PostBase):
	id: int
	created_at: datetime
	updated_at: Optional[datetime] = None
	author_id: int

	class Config:
		from_attributes = True