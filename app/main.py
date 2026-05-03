from fastapi import FastAPI  # 导入FastAPI核心类
from app.database import engine, Base  # 导入数据库引擎和基类
from app.routers.user import router as user_router
from app.routers.post import router as post_router
from app.routers.comments import router as comments_router
from app.routers.categories import router as categories_router

Base.metadata.create_all(bind=engine)
# 创建所有数据库表
# 作用：扫描所有继承Base的模型类，在数据库中创建对应的表结构；
# 执行时机：应用启动时自动执行，确保数据库表存在；开发环境使用，生产环境建议用迁移工具

app = FastAPI(title="Blog API", version="1.0")
# 创建FastAPI应用实例
# 作用：app是整个应用的入口，所有路由、中间件都注册到此实例；
# title和version会显示在自动生成的API文档中

# 注册路由
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comments_router)
app.include_router(categories_router)


@app.get('/')
def root():
    """根路径，返回欢迎信息"""
    return {"message": "Welcome to the Blog API!"}


@app.get("/health")
def health_check():
    """健康检查接口，用于监控服务状态"""
    return {"status": "ok"}