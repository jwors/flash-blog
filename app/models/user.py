from sqlalchemy import Column, Integer, String, DateTime  # 导入SQLAlchemy字段类型
from sqlalchemy.sql import func  # 导入SQL函数，用于数据库级函数调用
from sqlalchemy.orm import relationship  # 导入关系映射函数
from app.database import Base  # 导入ORM基类


class User(Base):  # 用户模型类，继承Base使其成为ORM映射类
    """用户数据模型，对应数据库users表

    作用：ORM模型将Python类映射到数据库表，操作Python对象即操作数据库记录，
    无需手写SQL语句。Base.__mapper__会自动扫描类属性，生成表结构映射。
    """

    __tablename__ = "users"  # 指定数据库表名
    # 作用：SQLAlchemy根据此属性确定模型对应的真实表名，默认为类名小写

    id = Column(Integer, primary_key=True, index=True)
    # 主键ID
    # 作用：primary_key=True标记为主键，数据库自动自增；
    # index=True创建B-tree索引，加速WHERE id=?查询（从O(n)到O(log n)）

    username = Column(String, unique=True, index=True)
    # 用户名
    # 作用：unique=True添加唯一约束，数据库拒绝重复值；
    # index=True创建索引，加速WHERE username=?和JOIN操作

    email = Column(String, unique=True, index=True)
    # 邵箱地址
    # 作用：同上，唯一约束防止重复注册，索引加速查询

    password = Column(String)
    # 密码哈希值
    # 作用：存储加密后的密码（如bcrypt哈希），非明文；
    # String类型无长度限制，实际应指定String(255)避免过长

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 创建时间
    # 作用：server_default=func.now()让数据库（而非Python）生成时间戳，
    # 好处：1.避免客户端时间不准；2.批量插入时数据库统一生成；
    # timezone=True存储带时区的时间，避免时区混乱问题

    posts = relationship("Post", back_populates="author")
    # 用户-文章关系（一对多）
    # 作用：relationship建立ORM层面的关联，user.posts可直接获取该用户的所有文章，
    # 无需手动JOIN查询；back_populates="author"与Post.author形成双向关联，
    # 使post.author也能反向获取用户对象

    comments = relationship("Comment", back_populates="author")
    # 用户-评论关系（一对多）
    # 作用：同上，user.comments获取该用户的所有评论；双向关联便于双向导航