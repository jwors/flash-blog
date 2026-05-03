from pydantic import BaseModel  # 导入Pydantic基类，用于数据验证和序列化
from datetime import datetime  # 导入日期时间类型，用于时间字段
from typing import Optional, List  # 导入可选类型和列表类型，用于字段类型定义


class PostBase(BaseModel):
    """文章基础数据结构，包含公共字段

    作用：作为其他Schema的父类，避免重复定义公共字段（title、content、summary）。
    继承PostBase的类自动拥有这些字段，符合DRY原则。
    """

    title: str  # 文章标题，必填字段，字符串类型
    content: str  # 文章正文内容，必填字段，字符串类型
    summary: Optional[str] = None  # 文章摘要，可选字段，默认为None（空）


class PostCreate(PostBase):
    """文章创建请求数据结构

    作用：定义创建文章时客户端需要提交的数据格式。
    继承PostBase的title、content、summary字段，额外添加author_id和category_ids。
    FastAPI自动验证请求体是否符合此结构，不符合则返回422错误。
    """

    author_id: int  # 作者ID，必填字段，关联users表的主键
    category_ids: Optional[List[int]] = None  # 分类ID列表，可选字段，用于多对多关联
    # 作用：客户端可传入多个分类ID，如[1,2,3]表示文章同时属于3个分类


class PostResponse(PostBase):
    """文章响应数据结构，返回给API调用者

    作用：定义API返回的文章数据格式，自动过滤掉敏感字段（如password）。
    客户端收到的JSON数据遵循此结构，保证响应数据的一致性。
    """

    id: int  # 文章ID，数据库自生成的主键
    created_at: datetime  # 创建时间，数据库自动生成的时间戳
    updated_at: Optional[datetime] = None  # 更新时间，可能为None（文章从未修改过）
    author_id: int  # 作者ID，关联users表

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy模型对象（如Post实例），
        # 自动提取字段值，无需手动转换为字典。
        # 示例：PostResponse.from_orm(db_post) 直接将ORM对象转为响应对象


class PostListResponse(BaseModel):
    """文章列表响应数据结构，包含分页元数据

    作用：返回文章列表时，不仅返回文章数据，还返回分页信息（总数、页码、是否有下一页）。
    客户端可根据total和hasNext判断是否需要加载更多，实现无限滚动或分页导航。
    """

    items: List[PostResponse]  # 当前页的文章列表，每个元素是PostResponse结构
    total: int  # 符合条件的文章总数（用于计算总页数：total_pages = total / limit）
    page: int  # 当前页码（从1开始），客户端传入的page参数
    limit: int  # 每页文章数量，客户端传入的limit参数
    hasNext: bool  # 是否有下一页，用于前端判断是否显示"加载更多"按钮
    # 计算逻辑：hasNext = (page * limit) < total

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据


class PostDetailResponse(PostResponse):
    """文章详情响应数据结构，包含作者和分类信息

    作用：返回单篇文章详情时，额外返回作者名称和分类名称列表。
    继承PostResponse的所有字段，添加author_name和categories字段。
    客户端无需再发起额外请求获取作者信息和分类信息，减少API调用次数。
    """

    author_name: Optional[str] = None  # 作者用户名，从关联的User模型获取
    # 作用：显示文章作者，如"张三发布了这篇文章"
    # 获取方式：db_post.author.username（通过relationship关联）

    categories: List[str] = []  # 分类名称列表，从关联的Category模型获取
    # 作用：显示文章所属分类，如["技术", "Python"]
    # 获取方式：[c.name for c in db_post.categories]（通过多对多relationship）