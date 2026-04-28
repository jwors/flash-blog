from fastapi import FastAPI, Depends  # 导入FastAPI核心类和依赖注入函数
from sqlalchemy.orm import Session  # 导入SQLAlchemy会话类型，用于类型提示
from app.database import engine, Base, get_db  # 导入数据库引擎、基类和会话依赖
from app.models.user import User  # 导入用户模型，用于数据库操作
from app.schemas.user import UserCreate, UserResponse  # 导入用户数据结构，用于API输入输出

Base.metadata.create_all(bind=engine)
# 创建所有数据库表
# 作用：扫描所有继承Base的模型类，在数据库中创建对应的表结构；
# 执行时机：应用启动时自动执行，确保数据库表存在；开发环境使用，生产环境建议用迁移工具

app = FastAPI(title="Blog API", version="1.0")
# 创建FastAPI应用实例
# 作用：app是整个应用的入口，所有路由、中间件都注册到此实例；
# title和version会显示在自动生成的API文档中


@app.get('/')
def root():
    """根路径，返回欢迎信息"""
    return {"message": "Welcome to the Blog API!"}
# 作用：提供API入口测试，用户访问根路径可确认服务运行状态


@app.post('/user/', response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    # 参数解析：
    # - user: UserCreate - Pydantic自动验证请求体，确保数据格式正确
    # - db: Session = Depends(get_db) - 依赖注入获取数据库会话，请求结束自动关闭
    db_user = User(username=user.username, email=user.email, password=user.password)
    # 创建ORM对象，将Pydantic数据转换为数据库模型实例
    db.add(db_user)  # 将对象添加到会话，准备插入数据库
    db.commit()  # 提交事务，实际执行INSERT语句
    db.refresh(db_user)  # 刷新对象，获取数据库生成的字段（如id、created_at）
    return db_user  # 返回用户对象，FastAPI自动转换为UserResponse格式


@app.get("/user")
def list_users(db: Session = Depends(get_db)):
    """获取所有用户列表"""
    users = db.query(User).all()  # 查询User表所有记录，返回Python对象列表
    return users  # 返回用户列表，FastAPI自动序列化为JSON