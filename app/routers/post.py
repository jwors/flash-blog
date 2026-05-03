from fastapi import APIRouter, Depends, HTTPException, Query  # 导入FastAPI路由相关类
# APIRouter: 路由器类，用于将路由分组管理
# Depends: 依赖注入函数，用于注入数据库会话等依赖
# HTTPException: HTTP异常类，用于返回错误响应（如404）
# Query: 查询参数验证类，用于验证URL查询参数（如page、limit）

from sqlalchemy.orm import Session  # 导入SQLAlchemy会话类型，用于数据库操作
from typing import List, Optional  # 导入类型提示类，用于函数参数和返回值类型标注
from app.database import get_db  # 导入数据库会话依赖函数
from app.models.post import Post  # 导入文章ORM模型，用于数据库查询和操作
from app.models.category import Category  # 导入分类ORM模型，用于多对多关联查询
from app.schemas.post import PostCreate, PostResponse, PostListResponse, PostDetailResponse  # 导入Pydantic数据结构

# 创建路由器实例
router = APIRouter(prefix="/posts", tags=['文章'])
# prefix="/posts": 所有路由自动添加/posts前缀，如/ -> /posts/
# tags=['文章']: API文档分组标签，Swagger UI按标签分组显示


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """创建文章

    参数:
        post: PostCreate - 文章创建数据，由Pydantic自动验证请求体
        db: Session - 数据库会话，由Depends(get_db)自动注入

    返回:
        PostResponse - 创建成功的文章数据，包含id、created_at等数据库生成的字段

    流程:
        1. Pydantic验证请求体是否符合PostCreate结构
        2. 创建Post ORM对象，将请求数据映射到数据库模型
        3. 处理分类关联（多对多关系）
        4. 添加到会话、提交事务、刷新对象
        5. 返回文章响应数据
    """
    db_post = Post(  # 创建Post ORM对象，对应数据库posts表的一行记录
        title=post.title,  # 文章标题，从请求体获取
        content=post.content,  # 文章正文，从请求体获取
        summary=post.summary,  # 文章摘要，从请求体获取
        author_id=post.author_id,  # 作者ID，从请求体获取，关联users表
    )

    # 处理分类关联：多对多关系
    if post.category_ids:  # 如果请求体包含分类ID列表
        # 查询所有指定ID的分类对象
        categories = db.query(Category).filter(Category.id.in_(post.category_ids)).all()
        # Category.id.in_([1,2,3]) 相当于 SQL: WHERE id IN (1,2,3)
        db_post.categories = categories  # 关联分类列表到文章对象
        # 多对多关系：通过中间表post_categories建立关联
        # SQLAlchemy自动处理中间表的INSERT操作

    db.add(db_post)  # 将文章对象添加到数据库会话，准备INSERT
    db.commit()  # 提交事务，执行SQL INSERT语句，数据写入数据库
    db.refresh(db_post)  # 刷新对象，获取数据库生成的字段值（id、created_at）
    # refresh相当于重新SELECT，将数据库生成的时间戳等字段同步到Python对象
    return db_post  # 返回文章对象，FastAPI自动转换为PostResponse JSON格式


@router.get("/", response_model=PostListResponse)
def list_posts(
    page: int = Query(1, ge=1),  # 页码参数，默认1，最小值1（ge=greater or equal）
    limit: int = Query(10, ge=1, le=100),  # 每页数量，默认10，范围1-100
    category_id: Optional[int] = None,  # 分类ID筛选，可选参数，默认None表示不筛选
    sort_by: str = Query("created_at", regex="^(created_at|updated_at)$"),  # 排序字段
    order: str = Query("desc", regex="^(asc|desc)$"),  # 排序方向
    db: Session = Depends(get_db)  # 数据库会话依赖注入
):
    """获取文章列表，支持分页、排序、分类筛选

    参数:
        page: int - 页码，从1开始（第1页、第2页...）
        limit: int - 每页文章数量，最大100防止一次加载过多数据
        category_id: Optional[int] - 分类ID，传入则只返回该分类下的文章
        sort_by: str - 排序字段，可选created_at（创建时间）或updated_at（更新时间）
        order: str - 排序方向，asc（升序）或desc（降序）
        db: Session - 数据库会话

    返回:
        PostListResponse - 包含文章列表和分页元数据（total、page、hasNext）

    示例请求:
        GET /posts/?page=1&limit=10&category_id=1&sort_by=created_at&order=desc
        返回：分类1下的文章，按创建时间降序，第1页10条
    """
    query = db.query(Post)  # 创建基础查询对象，相当于SQL: SELECT * FROM posts

    # 分类筛选：多对多关系过滤
    if category_id:  # 如果指定了分类ID
        # 多对多过滤：查询categories中包含指定分类的文章
        query = query.filter(Post.categories.any(Category.id == category_id))
        # Post.categories.any() 相当于 SQL: EXISTS (SELECT 1 FROM post_categories WHERE...)
        # 检查文章的关联分类中是否有指定的分类ID

    total = query.count()  # 获取符合条件的文章总数，用于计算分页信息
    # count()相当于SQL: SELECT COUNT(*) FROM posts WHERE...

    # 排序处理
    sort_column = getattr(Post, sort_by)  # 动态获取排序字段（Post.created_at或Post.updated_at）
    # getattr(Post, "created_at") 相当于 Post.created_at
    if order == "desc":  # 降序排序（最新的在前）
        query = query.order_by(sort_column.desc())  # SQL: ORDER BY created_at DESC
    else:  # 升序排序（最早的在前）
        query = query.order_by(sort_column.asc())  # SQL: ORDER BY created_at ASC

    # 分页处理
    offset = (page - 1) * limit  # 计算偏移量：第1页offset=0，第2页offset=limit
    # 第N页跳过前 (N-1)*limit 条记录
    posts = query.offset(offset).limit(limit).all()  # 执行查询，返回文章列表
    # offset(offset).limit(limit) 相当于 SQL: OFFSET 0 LIMIT 10

    # 计算是否有下一页
    has_next = offset + limit < total  # 已获取数量 < 总数，说明还有更多文章
    # 示例：total=25, page=2, limit=10 -> offset=10, 已获取20条 < 25条，hasNext=True

    # 构建响应对象
    return PostListResponse(
        items=posts,  # 当前页的文章列表
        total=total,  # 文章总数
        page=page,  # 当前页码
        limit=limit,  # 每页数量
        hasNext=has_next  # 是否有下一页
    )


@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """获取文章详情，包含作者名称和分类列表

    参数:
        post_id: int - 文章ID，从URL路径获取（如/posts/1中的1）
        db: Session - 数据库会话

    返回:
        PostDetailResponse - 文章详情，额外包含author_name和categories字段

    异常:
        HTTPException 404 - 文章不存在时返回

    流程:
        1. 根据post_id查询文章
        2. 文章不存在则返回404错误
        3. 通过relationship获取关联的作者和分类信息
        4. 构建详情响应返回
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 查询指定ID的文章
    # first()返回第一条匹配记录，不存在则返回None（不同于all()返回列表）

    if not db_post:  # 文章不存在
        raise HTTPException(status_code=404, detail="文章不存在")  # 返回404错误
        # HTTPException自动转换为JSON响应: {"detail": "文章不存在"}

    # 构建详情响应对象，手动提取关联数据
    response = PostDetailResponse(
        id=db_post.id,  # 文章ID
        title=db_post.title,  # 文章标题
        content=db_post.content,  # 文章正文
        summary=db_post.summary,  # 文章摘要
        author_id=db_post.author_id,  # 作者ID
        created_at=db_post.created_at,  # 创建时间
        updated_at=db_post.updated_at,  # 更新时间
        author_name=db_post.author.username,  # 作者用户名，通过relationship获取
        # db_post.author 访问关联的User对象（由relationship自动JOIN查询）
        categories=[category.name for category in db_post.categories]  # 分类名称列表
        # 遍历文章关联的所有分类，提取名称组成列表
        # 示例：db_post.categories = [Category(id=1,name="Tech"), Category(id=2,name="Life")]
        # 结果：categories = ["Tech", "Life"]
    )
    return response  # 返回详情响应


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    """更新文章

    参数:
        post_id: int - 要更新的文章ID
        post: PostCreate - 新的文章数据
        db: Session - 数据库会话

    返回:
        PostResponse - 更新后的文章数据

    异常:
        HTTPException 404 - 文章不存在

    流程:
        1. 查询文章，不存在返回404
        2. 更新文章字段
        3. 更新分类关联
        4. 提交事务，返回更新后的文章
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 查询文章
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")  # 文章不存在返回404

    # 更新文章字段（直接赋值修改ORM对象属性）
    db_post.title = post.title  # 更新标题
    db_post.content = post.content  # 更新正文内容
    db_post.summary = post.summary  # 更新摘要

    # 更新分类关联（多对多关系）
    if post.category_ids:  # 如果提供了新的分类ID列表
        categories = db.query(Category).filter(Category.id.in_(post.category_ids)).all()
        db_post.categories = categories  # 替换分类列表（旧的关联会被删除）
        # SQLAlchemy会自动处理中间表的UPDATE：先删除旧关联，再插入新关联

    db.commit()  # 提交事务，执行SQL UPDATE语句
    # UPDATE同时更新posts表和post_categories中间表
    db.refresh(db_post)  # 刷新对象，获取updated_at等自动更新的字段
    return db_post  # 返回更新后的文章


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """删除文章，级联删除关联评论

    参数:
        post_id: int - 要删除的文章ID
        db: Session - 数据库会话

    返回:
        dict - 删除成功消息 {"detail": "文章已删除"}

    异常:
        HTTPException 404 - 文章不存在

    级联删除:
        文章删除时，关联的评论会自动删除（由模型cascade="all, delete-orphan"配置）
        防止孤儿评论残留数据库
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 查询文章
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")  # 文章不存在返回404

    db.delete(db_post)  # 删除文章对象
    # delete()标记对象为删除状态，commit时执行SQL DELETE
    # 由于Post模型配置了cascade="all, delete-orphan"，关联评论也会被删除

    db.commit()  # 提交事务，执行DELETE语句
    return {"detail": "文章已删除"}  # 返回成功消息