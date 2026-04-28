from sqlalchemy import Column, Integer, String, ForeignKey  # 导入SQLAlchemy字段类型
from sqlalchemy.orm import relationship  # 导入关系映射函数
from app.database import Base  # 导入ORM基类


class Category(Base):  # 分类模型类，继承Base使其成为ORM映射类
    """分类数据模型，对应数据库categories表

    作用：存储博客文章的分类标签，如"技术"、"生活"、"随笔"等。
    通过多对多关系与文章关联，实现文章的分类管理。
    """

    __tablename__ = "categories"  # 指定数据库表名

    id = Column(Integer, primary_key=True, index=True)
    # 主键ID
    # 作用：primary_key=True标记为主键，数据库自动自增；
    # index=True创建索引，加速分类查询

    name = Column(String, unique=True, index=True)
    # 分类名称
    # 作用：unique=True确保分类名称不重复，如不能有两个"技术"分类；
    # index=True加速分类名称搜索

    description = Column(String(200))
    # 分类描述
    # 作用：限制200字符的描述文字，解释分类内容，便于用户理解分类用途

    posts = relationship("Post", secondary="post_categories", back_populates="categories")
    # 分类-文章关系（多对多）
    # 作用：secondary指定中间表post_categories，category.posts获取该分类下的所有文章；
    # 多对多关系：一个分类可包含多篇文章，一篇文章也可属于多个分类