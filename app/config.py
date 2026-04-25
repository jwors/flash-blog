import os  # 导入操作系统接口模块，用于访问环境变量
from dotenv import load_dotenv  # 导入dotenv模块，用于从.env文件加载环境变量

load_dotenv()  # 加载.env文件中的环境变量到系统环境


class Settings:
    """应用配置类，集中管理所有配置项"""

    def __init__(self):  # 初始化方法，创建实例时自动调用
        # Flask密钥，用于session加密和CSRF保护，优先从环境变量获取，无则使用默认值
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

        # 数据库连接地址，优先从环境变量获取，无则使用本地SQLite数据库
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")


settings = Settings()  # 创建全局配置实例，供其他模块导入使用