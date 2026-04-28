from sqlalchemy import create_engine  # 导入SQLAlchemy引擎创建函数
from sqlalchemy.orm import sessionmaker, declarative_base  # 导入会话工厂和ORM基类
from app.config import settings  # 导入配置实例

# 创建数据库引擎
# 作用：引擎是SQLAlchemy与数据库的底层连接核心，管理连接池、执行SQL语句
engine = create_engine(
    settings.DATABASE_URL,  # 数据库连接地址，格式：sqlite:///路径 或 postgresql://user:pass@host/db
    connect_args={"check_same_thread": False}  # SQLite专用配置
    # 作用：SQLite默认禁止多线程共享连接，此配置允许FastAPI多线程请求使用同一连接池
)

# 创建会话工厂类
# 作用：sessionmaker是工厂模式实现，每次调用SessionLocal()生成一个新会话实例，
# 会话是ORM操作的入口，所有增删改查都通过会话执行
SessionLocal = sessionmaker(
    autocommit=False,  # 禁用自动提交，需手动调用commit()，确保事务可控
    autoflush=False,    # 禁用自动刷新，需手动调用flush()，避免意外写入数据库
    bind=engine         # 绑定引擎，会话通过引擎执行SQL
)

# 创建ORM模型基类
# 作用：所有模型类继承Base后，SQLAlchemy自动将其映射到数据库表，
# Base包含元数据(metadata)，记录所有表结构信息
Base = declarative_base()


# 数据库会话依赖函数
# 作用：FastAPI依赖注入模式的核心，通过yield生成器实现请求级会话管理：
# 1. 请求开始时：生成db会话供路由使用
# 2. 请求处理中：路由通过db操作数据库
# 3. 请求结束后：finally块自动关闭会话，释放数据库连接
def get_db():
    """获取数据库会话，请求结束后自动关闭"""
    db = SessionLocal()  # 创建新的数据库会话实例
    try:
        yield db  # 生成会话供请求使用（yield暂停函数，返回db给调用者）
    finally:
        db.close()  # 无论请求成功或异常，都会执行关闭，防止连接泄漏