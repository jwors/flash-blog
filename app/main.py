from fastapi import FastAPI, Request  # 导入FastAPI核心类和请求对象
from fastapi.staticfiles import StaticFiles  # 导入静态文件挂载类
from fastapi.templating import Jinja2Templates  # 导入Jinja2模板引擎
from fastapi.responses import HTMLResponse  # 导入HTML响应类

from app.database import engine, Base  # 导入数据库引擎和基类
from app.routers.user import router as user_router
from app.routers.post import router as post_router
from app.routers.comments import router as comments_router
from app.routers.categories import router as categories_router
from app.routers.pages import router as pages_router  # 页面路由
from app.routers.auth import router as auth_router  # 认证路由
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings

# 创建所有数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用实例
app = FastAPI(title="Blog API", version="1.0")

# 添加会话中间件
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comments_router)
app.include_router(categories_router)

# 注册页面路由
app.include_router(pages_router)
app.include_router(auth_router)


@app.get('/api')
def api_root():
    """API根路径"""
    return {"message": "Welcome to the Blog API!", "docs": "/docs"}


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}