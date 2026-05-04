from fastapi import APIRouter, Request, Depends, HTTPException, Form  # 导入路由相关类
from fastapi.responses import HTMLResponse, RedirectResponse  # 导入响应类
from fastapi.templating import Jinja2Templates  # 导入模板引擎
from sqlalchemy.orm import Session  # 导入会话类型
from typing import Optional  # 导入可选类型
from passlib.context import CryptContext  # 导入密码加密库

from app.database import get_db  # 导入数据库会话依赖
from app.models.user import User  # 导入用户模型
from app.config import settings  # 导入配置

# 创建路由器实例
router = APIRouter(tags=['认证'])

# 配置模板引擎
templates = Jinja2Templates(directory="templates")

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(request: Request, db: Session) -> Optional[dict]:
    """从 session 获取当前登录用户"""
    user_id = request.session.get("user_id")
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return {"id": user.id, "username": user.username}
    return None


@router.get("/auth/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    """登录页面"""
    current_user = get_current_user(request, db)
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "current_user": current_user}
    )


@router.post("/auth/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """处理登录表单提交"""
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "用户名或密码错误", "current_user": None}
        )

    # TODO: 启用 session 后恢复
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@router.get("/auth/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    """注册页面"""
    current_user = get_current_user(request, db)
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "current_user": current_user}
    )


@router.post("/auth/register")
def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """处理注册表单提交"""
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "用户名已存在", "current_user": None}
        )

    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "邮箱已被注册", "current_user": None}
        )

    hashed_password = pwd_context.hash(password)
    user = User(username=username, email=email, password=hashed_password)

    db.add(user)
    db.commit()
    db.refresh(user)

    # TODO: 启用 session 后恢复
    request.session["user_id"] = user.id
    return RedirectResponse(url="/auth/login?registered=true", status_code=303)


@router.get("/auth/logout")
def logout(request: Request):
    """退出登录"""
    # TODO: 启用 session 后恢复
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)