from fastapi import APIRouter, Depends, HTTPException  # 导入路由类、依赖注入、异常类
from sqlalchemy.orm import Session  # 导入会话类型
from typing import List  # 导入列表类型
from app.database import get_db  # 导入数据库会话依赖
from app.models.comment import Comment  # 导入评论模型
from app.schemas.comment import CommentCreate, CommentResponse  # 导入评论数据结构

router = APIRouter(prefix="/comments", tags=['评论'])
# 创建路由器实例
# 作用：将评论相关路由组织在一起，便于模块化管理；
# prefix="/comments" - 所有路由自动添加/comments前缀
# tags=['评论'] - API文档分组标签


@router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """创建评论或回复"""
    # 参数：comment - Pydantic验证请求体，包含content、author_id、post_id、parent_id
    # parent_id为None时是顶层评论，有值时是回复其他评论
    db_comment = Comment(
        content=comment.content,
        author_id=comment.author_id,
        post_id=comment.post_id,
        parent_id=comment.parent_id  # 嵌套回复的父评论ID
    )
    # 创建ORM对象，支持普通评论和嵌套回复
    db.add(db_comment)  # 添加到会话
    db.commit()  # 提交事务，执行INSERT
    db.refresh(db_comment)  # 刷新对象，获取数据库生成字段（id、created_at）
    return db_comment  # 返回评论对象，自动转换为CommentResponse


@router.get("/post/{post_id}", response_model=List[CommentResponse])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    """获取指定文章的所有评论列表"""
    # 路径参数：post_id - 文章ID，从URL路径获取
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    # 查询该文章的所有评论，包括顶层评论和回复
    # 注意：返回的是扁平列表，前端需根据parent_id构建树形结构
    return comments


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """删除评论"""
    # 路径参数：comment_id - 评论ID
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    # 查询指定评论
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    # 评论不存在返回404错误
    db.delete(db_comment)  # 删除评论对象
    db.commit()  # 提交事务，执行DELETE
    return {"detail": "评论已删除"}
    # 注意：删除父评论时，子评论（回复）不会自动删除；
    # 如需级联删除，需在模型中配置cascade或在业务逻辑中处理