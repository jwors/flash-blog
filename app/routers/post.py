from fastapi import APIRouter, Depends, HTTPException  # 导入路由类、依赖注入、异常类
from sqlalchemy.orm import Session  # 导入会话类型
from typing import List, Optional  # 导入列表和可选类型
from app.database import get_db  # 导入数据库会话依赖
from app.models.post import Post  # 导入文章模型
from app.models.category import Category  # 导入分类模型
from app.schemas.post import PostCreate, PostResponse  # 导入文章数据结构

router = APIRouter(prefix="/posts", tags=['文章'])


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """创建文章"""
    db_post = Post(
        title=post.title,
        content=post.content,
        summary=post.summary,
        author_id=post.author_id,
    )
    # 处理分类关联：多对多关系
    if post.category_ids:
        categories = db.query(Category).filter(Category.id.in_(post.category_ids)).all()
        db_post.categories = categories  # 关联分类列表

    db.add(db_post)  # 添加到会话
    db.commit()  # 提交事务，执行INSERT
    db.refresh(db_post)  # 刷新对象，获取数据库生成字段
    return db_post  # 返回文章对象


@router.get("/", response_model=List[PostResponse])
def list_posts(
    skip: int = 0,  # 分页偏移量
    limit: int = 10,  # 每页数量
    category_id: Optional[int] = None,  # 分类过滤
    db: Session = Depends(get_db)
):
    """获取文章列表，支持分页和分类过滤"""
    query = db.query(Post)
    if category_id:
        # 多对多过滤：查询属于指定分类的文章
        query = query.filter(Post.categories.any(Category.id == category_id))
    posts = query.offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """获取文章详情"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return db_post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    """更新文章"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")

    db_post.title = post.title  # 更新标题
    db_post.content = post.content  # 更新内容
    db_post.summary = post.summary  # 更新摘要

    # 更新分类关联
    if post.category_ids:
        categories = db.query(Category).filter(Category.id.in_(post.category_ids)).all()
        db_post.categories = categories  # 替换分类列表

    db.commit()  # 提交事务
    db.refresh(db_post)  # 刷新对象
    return db_post


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """删除文章"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    db.delete(db_post)  # 删除对象，级联删除评论
    db.commit()  # 提交事务
    return {"detail": "文章已删除"}