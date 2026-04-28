import os  # 导入操作系统接口模块，用于访问环境变量
from dotenv import load_dotenv  # 导入dotenv模块，用于从.env文件加载环境变量

load_dotenv()  # 加载.env文件中的环境变量到系统环境
# 作用：将.env文件中的变量注入os.environ，使敏感配置(密钥、密码)不必硬编码在代码中


class Settings:
    """应用配置类，集中管理所有配置项

    作用：采用单例模式思想，将所有配置集中在一个类中管理，
    避免配置散落在各处，便于统一修改和维护
    """

    def __init__(self):  # 初始化方法，创建实例时自动调用
        # Flask密钥，用于session加密和CSRF保护
        # 作用：Flask用此密钥对session数据进行签名，防止伪造；优先从环境变量获取，无则使用开发默认值
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

        # 数据库连接地址
        # 作用：SQLAlchemy通过此URL连接数据库；优先从环境变量获取，生产环境可切换为PostgreSQL等
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")


settings = Settings()  # 创建全局配置实例
# 作用：模块导入时创建单例，其他模块通过from config import settings直接使用，无需重复实例化