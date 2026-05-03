from fastapi import APIRouter, Depends, HTTPException  # 导入FastAPI路由相关类
# APIRouter: 路由器类，用于分组管理路由
# Depends: 依赖注入函数，用于自动注入数据库会话
# HTTPException: HTTP异常类，用于返回错误响应

from sqlalchemy.orm import Session  # 导入SQLAlchemy会话类型
from typing import List  # 导入列表类型，用于类型提示
from app.database import get_db  # 导入数据库会话依赖函数
from app.models.category import Category  # 导入分类ORM模型
from app.schemas.category import CategoryCreate, CategoryResponse  # 导入分类Pydantic数据结构

# 创建路由器实例
router = APIRouter(prefix="/categories", tags=['分类'])
# prefix="/categories": 所有路由自动添加/categories前缀
# tags=['分类']: API文档分组标签，Swagger UI中归类显示


@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """创建分类

    参数:
        category: CategoryCreate - 分类创建数据，包含name和description
        db: Session - 数据库会话，由Depends(get_db)自动注入

    返回:
        CategoryResponse - 创建成功的分类数据，包含数据库生成的id字段

    流程:
        1. Pydantic验证请求体（name必填，description可选）
        2. 创建Category ORM对象
        3. 添加到会话、提交事务、刷新对象
        4. 返回分类响应

    示例请求:
        POST /categories/
        Body: {"name": "技术", "description": "技术相关文章"}
    """
    db_category = Category(  # 创建Category ORM对象
        name=category.name,  # 分类名称，如"技术"、"生活"
        description=category.description  # 分类描述，解释分类内容
    )

    db.add(db_category)  # 将分类对象添加到数据库会话，准备INSERT
    db.commit()  # 提交事务，执行SQL INSERT语句
    db.refresh(db_category)  # 刷新对象，获取数据库生成的id字段
    return db_category  # 返回分类对象，自动转换为CategoryResponse JSON


@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类列表

    参数:
        db: Session - 数据库会话

    返回:
        List[CategoryResponse] - 所有分类的列表，每个元素包含id、name、description

    用途:
        前端可调用此接口获取分类列表，用于:
        1. 分类导航菜单展示
        2. 文章创建/编辑时选择分类
        3. 分类筛选下拉框
    """
    return db.query(Category).all()  # 查询所有分类记录，返回列表
    # all()相当于SQL: SELECT * FROM categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取指定分类详情

    参数:
        category_id: int - 分类ID，从URL路径获取（如/categories/1中的1）
        db: Session - 数据库会话

    返回:
        CategoryResponse - 分类详情数据

    异常:
        HTTPException 404 - 分类不存在时返回

    用途:
        获取单个分类的详细信息，可用于:
        1. 分类详情页展示
        2. 编辑分类时获取原有数据
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    # 根据ID查询分类，first()返回第一条匹配记录或None

    if not db_category:  # 分类不存在
        raise HTTPException(status_code=404, detail="分类不存在")
        # 返回404错误，HTTPException自动转换为JSON响应

    return db_category  # 返回分类对象


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """更新分类信息

    参数:
        category_id: int - 要更新的分类ID
        category: CategoryCreate - 新的分类数据（name、description）
        db: Session - 数据库会话

    返回:
        CategoryResponse - 更新后的分类数据

    异常:
        HTTPException 404 - 分类不存在

    流程:
        1. 查询分类，不存在返回404
        2. 更新分类的name和description字段
        3. 提交事务，返回更新后的分类

    注意:
        name字段有唯一约束，如果新name已存在其他分类，会触发数据库错误
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")

    db_category.name = category.name  # 更新分类名称
    db_category.description = category.description  # 更新分类描述
    # 直接修改ORM对象属性，commit时会生成UPDATE语句

    db.commit()  # 提交事务，执行SQL UPDATE
    db.refresh(db_category)  # 刷新对象，确保数据同步
    return db_category  # 返回更新后的分类


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """删除分类

    参数:
        category_id: int - 要删除的分类ID
        db: Session - 数据库会话

    返回:
        dict - 删除成功消息 {"detail": "分类已删除"}

    异常:
        HTTPException 404 - 分类不存在

    注意:
        删除分类不会级联删除关联的文章，只是解除关联关系：
        - post_categories中间表中的关联记录会被删除
        - 文章本身仍然存在，只是不再属于该分类
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")

    db.delete(db_category)  # 删除分类对象
    # SQLAlchemy会自动处理多对多关系：删除中间表中关联该分类的记录

    db.commit()  # 提交事务，执行DELETE语句
    return {"detail": "分类已删除"}  # 返回成功消息