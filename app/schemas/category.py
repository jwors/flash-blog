from pydantic import BaseModel  # 导入Pydantic基类，用于数据验证和序列化


class CategoryBase(BaseModel):
    """分类基础数据结构，包含公共字段

    作用：作为其他Schema的父类，定义分类的公共字段（name、description）。
    继承CategoryBase的类自动拥有这些字段，避免重复定义。
    """

    name: str  # 分类名称，必填字段，如"技术"、"生活"、"随笔"
    description: str = None  # 分类描述，可选字段，默认为None
    # 作用：解释分类内容，帮助用户理解分类用途


class CategoryCreate(CategoryBase):
    """分类创建请求数据结构

    作用：定义创建分类时客户端需要提交的数据格式。
    继承CategoryBase，无需额外字段（创建分类只需name和description）。

    验证规则:
        - name: 必填，字符串类型
        - description: 可选，字符串类型，默认None

    示例请求体:
        {"name": "技术", "description": "技术相关文章"}
    """
    pass  # 空类体，表示完全继承父类字段


class CategoryResponse(CategoryBase):
    """分类响应数据结构，返回给API调用者

    作用：定义API返回的分类数据格式，额外包含数据库生成的id字段。
    客户端收到的JSON数据遵循此结构。

    字段:
        - id: 分类ID（数据库主键）
        - name: 分类名称（继承自CategoryBase）
        - description: 分类描述（继承自CategoryBase）

    示例响应:
        {"id": 1, "name": "技术", "description": "技术相关文章"}
    """

    id: int  # 分类ID，数据库自增生成的主键

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy Category对象，
        # 自动提取id、name、description字段值