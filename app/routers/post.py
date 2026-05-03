from fastapi import APIRouter, Depends, HTTPException  # 导入路由类、依赖注入、异常类
from sqlalchemy.orm import Session  # 导入会话类型
from typing import List, Optional  # 导入列表和可选类型
from app.database import get_db  # 导入数据库会话依赖
from app.models.post import Post  # 导入文章模型
from app.models.category import Category  # 导入分类模型
from app.schemas.post import PostCreate, PostResponse  # 导入文章数据结构

router = APIRouter(prefix="/posts", tags=['文章'])
# 创建路由器实例
# 作用：将相关路由组织在一起，便于模块化管理；
# prefix="/posts" - 所有路由自动添加/posts前缀，如/ -> /posts/
# tags=['文章'] - API文档分组标签，Swagger UI按标签分组显示


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """创建文章"""
    # 参数：post - Pydantic验证请求体；db - 依赖注入数据库会话
    db_post = Post(
        title=post.title,
        content=post.content,
        summary=post.summary,
        author_id=post.author_id,
    )
    # 创建ORM对象，将请求数据转换为数据库模型
    db.add(db_post)  # 添加到会话
    db.commit()  # 提交事务，执行INSERT
    db.refresh(db_post)  # 刷新对象，获取数据库生成字段
    return db_post  # 返回文章对象，自动转换为PostResponse


@router.get("/", response_model=List[PostResponse])
def list_posts(
    skip: int = 0,  # 分页偏移量，默认0（从第一条开始）
    limit: int = 10,  # 每页数量，默认10条
    category_id: Optional[int] = None,  # 分类过滤，可选
    db: Session = Depends(get_db)
):
    """获取文章列表，支持分页和分类过滤"""
    query = db.query(Post)  # 创建查询对象
    if category_id:
         query = query.filter(Post.categories.any(Category.id == category_id)) # 添加分类过滤条件
    posts = query.offset(skip).limit(limit).all()  # 执行分页查询，返回结果列表
    return posts


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    """更新文章（注：路由装饰器应为@router.put，当前@router.get是错误的）"""
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 查询指定ID的文章
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")  # 文章不存在返回404
    db_post.title = post.title  # 更新标题
    db_post.content = post.content  # 更新内容
    db_post.summary = post.summary  # 更新摘要
    db.commit()  # 提交事务，执行UPDATE
    db.refresh(db_post)  # 刷新对象，获取更新后的字段
    return db_post


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """删除文章"""
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 查询文章
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")  # 不存在返回404
    db.delete(db_post)  # 删除对象
    db.commit()  # 提交事务，执行DELETE
    return {"detail": "文章已删除"}  # 返回成功消息