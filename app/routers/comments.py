from fastapi import APIRouter, Depends, HTTPException  # 导入FastAPI路由相关类
# APIRouter: 路由器类，用于分组管理评论相关路由
# Depends: 依赖注入函数，用于自动注入数据库会话
# HTTPException: HTTP异常类，用于返回错误响应（如404评论不存在）

from sqlalchemy.orm import Session  # 导入SQLAlchemy会话类型，用于数据库操作
from typing import List  # 导入列表类型，用于类型提示（如List[CommentResponse]）

from app.database import get_db  # 导入数据库会话依赖函数
from app.models.comment import Comment  # 导入评论ORM模型，对应数据库comments表
from app.schemas.comment import CommentCreate, CommentResponse  # 导入评论Pydantic数据结构

# 创建路由器实例
router = APIRouter(prefix="/comments", tags=['评论'])
# prefix="/comments": 所有路由自动添加/comments前缀
# tags=['评论']: API文档分组标签，Swagger UI中归类显示
# 示例：@router.post("/") 实际路径为 POST /comments/


@router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """创建评论或回复

    参数:
        comment: CommentCreate - 评论创建数据
            - content: 评论正文内容
            - author_id: 评论作者ID
            - post_id: 所属文章ID
            - parent_id: 父评论ID（可选，用于嵌套回复）
        db: Session - 数据库会话，由Depends(get_db)自动注入

    返回:
        CommentResponse - 创建成功的评论数据，包含id和created_at

    评论类型:
        1. 顶层评论：parent_id=None，直接评论文章
           示例：{"content": "好文章！", "author_id": 1, "post_id": 5}
        2. 回复评论：parent_id有值，回复其他评论
           示例：{"content": "同意你的观点", "author_id": 2, "post_id": 5, "parent_id": 10}

    嵌套结构:
        评论支持多级嵌套（回复的回复）：
        - 评论A（parent_id=None）
          - 评论B（parent_id=A.id，回复A）
            - 评论C（parent_id=B.id，回复B）
        前端根据parent_id构建评论树，展示回复关系。

    流程:
        1. Pydantic验证请求体
        2. 创建Comment ORM对象
        3. 添加到会话、提交事务、刷新对象
        4. 返回评论响应
    """
    db_comment = Comment(  # 创建Comment ORM对象
        content=comment.content,  # 评论正文内容
        author_id=comment.author_id,  # 评论作者ID，关联users表
        post_id=comment.post_id,  # 所属文章ID，关联posts表
        parent_id=comment.parent_id  # 父评论ID，用于嵌套回复
        # parent_id=None时是顶层评论，有值时是回复其他评论
    )

    db.add(db_comment)  # 将评论对象添加到数据库会话，准备INSERT
    db.commit()  # 提交事务，执行SQL INSERT，数据写入数据库
    db.refresh(db_comment)  # 刷新对象，获取数据库生成的id和created_at字段
    return db_comment  # 返回评论对象，FastAPI自动转换为CommentResponse JSON


@router.get("/post/{post_id}", response_model=List[CommentResponse])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    """获取指定文章的所有评论列表

    参数:
        post_id: int - 文章ID，从URL路径获取（如/comments/post/5中的5）
        db: Session - 数据库会话

    返回:
        List[CommentResponse] - 该文章的所有评论列表（扁平结构）

    数据结构:
        返回的是扁平列表，包含所有评论（顶层评论和回复）：
        [
            {"id": 1, "content": "好文章", "parent_id": null, ...},  // 顶层评论
            {"id": 2, "content": "同意", "parent_id": 1, ...},       // 回复评论1
            {"id": 3, "content": "补充", "parent_id": 1, ...}        // 回复评论1
        ]

        前端需要根据parent_id构建树形结构：
        - parent_id=null的是顶层评论
        - parent_id有值的是回复，找到对应的父评论

    性能考虑:
        大量评论时，应考虑：
        - 分页加载（只加载前N条评论）
        - 按时间排序（新评论在前）
        - 深度限制（限制嵌套层级）

    示例请求:
        GET /comments/post/5  // 获取文章ID=5的所有评论
    """
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    # 根据文章ID查询所有评论，包括顶层评论和回复
    # filter(Comment.post_id == post_id) 相当于 SQL: WHERE post_id = 5
    # all() 返回所有匹配记录的列表

    return comments  # 返回评论列表


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """删除评论

    参数:
        comment_id: int - 要删除的评论ID，从URL路径获取
        db: Session - 数据库会话

    返回:
        dict - 删除成功消息 {"detail": "评论已删除"}

    异常:
        HTTPException 404 - 评论不存在时返回

    级联删除问题:
        当前实现不会级联删除子评论（回复）：
        - 删除父评论后，子评论的parent_id仍指向已删除的评论
        - 实际项目中应考虑：
          1. 级联删除所有子评论（递归删除）
          2. 将子评论的parent_id设为NULL（转为顶层评论）
          3. 软删除（标记deleted字段，保留数据）

    安全考虑:
        实际生产环境应添加权限控制：
        - 只有评论作者可以删除自己的评论
        - 文章作者可以删除文章下的任何评论
        - 管理员可以删除任何评论
    """
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    # 根据ID查询评论，first()返回第一条匹配记录或None

    if not db_comment:  # 评论不存在
        raise HTTPException(status_code=404, detail="评论不存在")
        # 返回404错误，HTTPException自动转换为JSON响应

    db.delete(db_comment)  # 删除评论对象，标记为删除状态
    # 注意：删除父评论时，子评论不会自动删除
    # 如需级联删除，需在模型配置cascade或在业务逻辑中处理

    db.commit()  # 提交事务，执行SQL DELETE
    return {"detail": "评论已删除"}  # 返回成功消息