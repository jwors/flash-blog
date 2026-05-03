from pydantic import BaseModel  # 导入Pydantic基类


class CategoryBase(BaseModel):
    """分类基础数据结构，包含公共字段"""
    name: str  # 分类名称
    description: str = None  # 分类描述，可选


class CategoryCreate(CategoryBase):
    """分类创建请求数据结构"""
    pass  # 继承CategoryBase所有字段


class CategoryResponse(CategoryBase):
    """分类响应数据结构，返回给API调用者"""
    id: int  # 分类ID

    class Config:
        from_attributes = True
        # 配置：允许从ORM对象读取数据
        # 作用：使Pydantic能直接接受SQLAlchemy模型对象，自动提取字段值