from fastapi import APIRouter, Request, Depends, Form  # 导入路由相关类
from fastapi.responses import HTMLResponse, RedirectResponse  # 导入响应类
from fastapi.templating import Jinja2Templates  # 导入模板引擎
from sqlalchemy.orm import Session  # 导入会话类型
from typing import Optional, List  # 导入类型

from app.database import get_db  # 导入数据库会话依赖
from app.models.post import Post  # 导入文章模型
from app.models.category import Category  # 导入分类模型
from app.models.user import User  # 导入用户模型

# 创建路由器实例
router = APIRouter(tags=['页面'])

# 配置模板引擎
templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request, db: Session) -> Optional[dict]:
    """从 session 获取当前登录用户"""
    user_id = request.session.get("user_id")
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return {"id": user.id, "username": user.username}
    return None


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    """首页"""
    current_user = get_current_user(request, db)

    page = int(request.query_params.get("page", 1))
    category_id = request.query_params.get("category_id")

    query = db.query(Post)
    if category_id:
        query = query.filter(Post.categories.any(Category.id == int(category_id)))

    total = query.count()
    limit = 12
    offset = (page - 1) * limit
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()

    post_list = []
    for post in posts:
        post_list.append({
            "id": post.id,
            "title": post.title,
            "summary": post.summary,
            "content": post.content[:100] if not post.summary else None,
            "author_name": post.author.username if post.author else None,
            "created_at": post.created_at,
            "categories": [c.name for c in post.categories]
        })

    categories = db.query(Category).all()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "post_list": post_list,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "hasNext": offset + limit < total
        },
        "categories": categories,
        "category_id": int(category_id) if category_id else None,
        "current_user": current_user
    })


@router.get("/p/{post_id}", response_class=HTMLResponse)
def post_detail(request: Request, post_id: int, db: Session = Depends(get_db)):
    """文章详情页（使用 /p/{id} 避免和 API 路由冲突）"""
    current_user = get_current_user(request, db)

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("post/detail.html", {
        "request": request,
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "author_id": post.author_id,
            "author_name": post.author.username if post.author else None,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "categories": [c.name for c in post.categories]
        },
        "comments": [],
        "current_user": current_user
    })


@router.get("/write", response_class=HTMLResponse)
def create_post_page(request: Request, db: Session = Depends(get_db)):
    """创建文章页面"""
    current_user = get_current_user(request, db)

    categories = db.query(Category).all()
    return templates.TemplateResponse("post/create.html", {
        "request": request,
        "categories": categories,
        "current_user": current_user,
        "edit_mode": False,
        "post": None
    })


@router.post("/write")
def create_post_submit(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    summary: Optional[str] = Form(None),
    category_ids: List[int] = Form(None),
    db: Session = Depends(get_db)
):
    """处理创建文章表单"""
    post = Post(
        title=title,
        content=content,
        summary=summary,
        author_id=1  # 暂时固定为用户1
    )

    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        post.categories = categories

    db.add(post)
    db.commit()
    db.refresh(post)

    return RedirectResponse(url=f"/p/{post.id}", status_code=303)