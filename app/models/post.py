from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table  # 导入SQLAlchemy字段类型
from sqlalchemy.orm import relationship  # 导入关系映射函数
from sqlalchemy.sql import func  # 导入SQL函数
from app.database import Base  # 导入ORM基类


# 文章-分类 多对多关联表
# 作用：多对多关系需要一个中间表来存储关联关系，
# 一篇文章可以属于多个分类，一个分类也可以包含多篇文章
post_categories = Table(
    'post_categories',  # 中间表名
    Base.metadata,  # 绑定到Base的元数据，使表能被创建和管理
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    # 文章ID外键，引用posts表的主键；primary_key=True组成联合主键防止重复关联
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
    # 分类ID外键，引用categories表的主键；联合主键确保同一文章不会重复关联同一分类
)


class Post(Base):  # 文章模型类，继承Base使其成为ORM映射类
    """文章数据模型，对应数据库posts表

    作用：存储博客文章内容，包括标题、正文、摘要、作者关联、时间戳等。
    通过relationship实现与用户(一对多)、评论(一对多)、分类(多对多)的关联。
    """

    __tablename__ = "posts"  # 指定数据库表名

    id = Column(Integer, primary_key=True, index=True)
    # 主键ID
    # 作用：primary_key=True标记为主键，数据库自动自增；
    # index=True创建索引，加速文章查询

    title = Column(String, index=True)
    # 文章标题
    # 作用：index=True创建索引，加速标题搜索和排序操作

    content = Column(Text, nullable=False)
    # 文章正文内容
    # 作用：Text类型用于存储长文本（无长度限制），比String更适合文章内容；
    # nullable=False强制必须有内容，防止空文章入库

    summary = Column(String(200))
    # 文章摘要
    # 作用：限制200字符的短描述，用于列表页展示，提升用户体验

    author_id = Column(Integer, ForeignKey("users.id"))
    # 作者ID外键
    # 作用：ForeignKey建立数据库级别的关联约束，引用users表的id字段；
    # 外键确保：1.author_id必须是有效的用户ID；2.删除用户时可设置级联策略

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 创建时间
    # 作用：server_default=func.now()让数据库自动生成当前时间戳

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # 更新时间
    # 作用：onupdate=func.now()每次更新记录时自动刷新时间，无需手动设置；
    # 配合created_at可追踪文章的修改历史

    author = relationship("User", back_populates="posts")
    # 文章-作者关系（多对一）
    # 作用：post.author可直接获取作者用户对象，无需JOIN；
    # back_populates="posts"与User.posts形成双向关联

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    # 文章-评论关系（一对多）
    # 作用：post.comments获取该文章的所有评论；
    # cascade="all, delete-orphan"级联策略：删除文章时自动删除其所有评论，
    # 防止孤儿评论残留数据库

    categories = relationship("Category", secondary="post_categories", back_populates="posts")
    # 文章-分类关系（多对多）
    # 作用：secondary指定中间表post_categories，post.categories获取所有关联分类；
    # 多对多通过中间表实现，一篇文章可有多个分类标签