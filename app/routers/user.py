from fastapi import APIRouter, Depends, HTTPException  # 导入FastAPI路由相关类
# APIRouter: 路由器类，用于分组管理用户相关路由
# Depends: 依赖注入函数，用于自动注入数据库会话
# HTTPException: HTTP异常类，用于返回错误响应（如404用户不存在）

from sqlalchemy.orm import Session  # 导入SQLAlchemy会话类型，用于数据库操作
from typing import List  # 导入列表类型，用于类型提示（如List[UserResponse]）

from passlib.context import CryptContext  # 导入密码加密库
# CryptContext: 密码哈希上下文，支持多种哈希算法（bcrypt、argon2等）
# bcrypt: 业界标准的密码哈希算法，加盐+多轮哈希，防止彩虹表攻击

from app.database import get_db  # 导入数据库会话依赖函数
from app.models.user import User  # 导入用户ORM模型，对应数据库users表
from app.schemas.user import UserCreate, UserResponse, UserUpdate  # 导入用户Pydantic数据结构

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# schemes=["bcrypt"]: 使用bcrypt算法进行密码哈希
# deprecated="auto": 自动处理过时的哈希算法（如需要升级旧哈希）
#
# bcrypt特点:
# - 自动加盐：每次哈希生成随机盐值，相同密码哈希结果不同
# - 计算密集：可配置迭代轮数（默认12轮），增加破解难度
# - 安全存储：即使数据库泄露，攻击者也无法还原明文密码


# 创建路由器实例
router = APIRouter(prefix="/users", tags=["用户"])
# prefix="/users": 所有路由自动添加/users前缀
# tags=["用户"]: API文档分组标签，Swagger UI中归类显示


def get_password_hash(password: str) -> str:
    """生成密码哈希值

    参数:
        password: str - 明文密码（用户输入的原始密码）

    返回:
        str - bcrypt哈希后的密码字符串

    示例:
        明文: "123456"
        哈希: "$2b$12$N9qo8uLOickgx2ZMRZoMy.MrqJ8hZeq3pB..."
        （哈希值包含算法标识、轮数、盐值和哈希结果）

    安全说明:
        - 每次调用生成不同的哈希值（随机盐）
        - 相同密码的两次哈希结果不同，但验证都能成功
    """
    return pwd_context.hash(password)  # 使用bcrypt算法哈希密码


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配

    参数:
        plain_password: str - 用户输入的明文密码
        hashed_password: str - 数据库存储的哈希密码

    返回:
        bool - True表示密码匹配，False表示不匹配

    工作原理:
        bcrypt哈希包含盐值，验证时：
        1. 从哈希值中提取盐值和算法参数
        2. 用相同参数对明文密码进行哈希
        3. 比较两个哈希值是否相同

    用途:
        用户登录时验证密码：
        if verify_password(input_password, db_user.password):
            # 密码正确，允许登录
    """
    return pwd_context.verify(plain_password, hashed_password)  # 验证密码


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户（注册）

    参数:
        user: UserCreate - 用户创建数据，包含username、email、password
        db: Session - 数据库会话，由Depends(get_db)自动注入

    返回:
        UserResponse - 创建成功的用户数据（不含password字段）

    流程:
        1. Pydantic验证请求体（email格式、字段完整性）
        2. 使用bcrypt加密明文密码
        3. 创建User ORM对象
        4. 添加到会话、提交事务、刷新对象
        5. 返回用户响应（password字段自动过滤）

    安全处理:
        - 明文密码不存储到数据库
        - 使用bcrypt哈希加密，防止密码泄露
        - UserResponse不包含password字段，响应安全

    示例请求:
        POST /users/
        Body: {"email": "user@example.com", "username": "张三", "password": "123456"}
    """
    # 密码加密：使用bcrypt哈希算法加密密码
    hashed_password = get_password_hash(user.password)  # 明文密码转为哈希值
    # 示例：get_password_hash("123456") -> "$2b$12$..."

    db_user = User(  # 创建User ORM对象
        username=user.username,  # 用户名，直接存储
        email=user.email,  # 邮箱，直接存储
        password=hashed_password  # 存储加密后的哈希密码（非明文）
    )

    db.add(db_user)  # 将用户对象添加到数据库会话
    db.commit()  # 提交事务，执行SQL INSERT，数据写入数据库
    db.refresh(db_user)  # 刷新对象，获取数据库生成的id和created_at字段
    return db_user  # 返回用户对象，FastAPI自动转换为UserResponse（不含password）


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """获取所有用户列表

    参数:
        db: Session - 数据库会话

    返回:
        List[UserResponse] - 所有用户的列表

    注意:
        此接口返回所有用户信息，实际生产环境应考虑：
        - 添加权限控制（仅管理员可访问）
        - 添加分页参数（防止大量用户时性能问题）
        - 过滤敏感信息（如email）
    """
    return db.query(User).all()  # 查询users表所有记录，返回列表
    # all()相当于SQL: SELECT * FROM users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户详情

    参数:
        user_id: int - 用户ID，从URL路径获取（如/users/1中的1）
        db: Session - 数据库会话

    返回:
        UserResponse - 用户详情数据

    异常:
        HTTPException 404 - 用户不存在时返回

    用途:
        获取单个用户的详细信息，可用于：
        1. 用户个人主页展示
        2. 文章详情页显示作者信息
        3. 评论列表显示评论者信息
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    # 根据ID查询用户，first()返回第一条匹配记录或None

    if not db_user:  # 用户不存在
        raise HTTPException(status_code=404, detail="用户不存在")
        # 返回404错误，HTTPException自动转换为JSON响应

    return db_user  # 返回用户对象


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息

    参数:
        user_id: int - 要更新的用户ID
        user: UserUpdate - 更新数据，所有字段可选（部分更新）
        db: Session - 数据库会话

    返回:
        UserResponse - 更新后的用户数据

    异常:
        HTTPException 404 - 用户不存在

    流程:
        1. 查询用户，不存在返回404
        2. 部分更新：只更新传入的字段（None值不更新）
        3. 密码特殊处理：传入新密码时先加密再存储
        4. 提交事务，返回更新后的用户

    部分更新逻辑:
        UserUpdate所有字段都是Optional，允许只修改部分信息：
        - 只更新用户名：{"username": "新名字"}
        - 只修改密码：{"password": "新密码"}
        - 同时更新多个：{"username": "新名字", "email": "新邮箱"}

    示例请求:
        PUT /users/1
        Body: {"username": "新用户名"}
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 部分更新：只有字段不为None时才更新
    if user.username is not None:  # 如果传入了新用户名
        db_user.username = user.username  # 更新用户名字段

    if user.email is not None:  # 如果传入了新邮箱
        db_user.email = user.email  # 更新邮箱字段

    if user.password is not None:  # 如果传入了新密码
        db_user.password = get_password_hash(user.password)  # 密码加密后再更新
        # 安全处理：新密码也需要加密存储，不能明文

    db.commit()  # 提交事务，执行SQL UPDATE
    db.refresh(db_user)  # 刷新对象，确保数据同步
    return db_user  # 返回更新后的用户对象


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户

    参数:
        user_id: int - 要删除的用户ID
        db: Session - 数据库会话

    返回:
        dict - 删除成功消息 {"detail": "用户已删除"}

    异常:
        HTTPException 404 - 用户不存在

    级联删除:
        User模型配置了与Post和Comment的关联关系：
        - 删除用户时，关联的文章可能需要处理（取决于cascade配置）
        - 当前配置下，文章的author_id变为NULL或保留（取决于外键约束）
        - 实际项目中应考虑：是否允许删除有文章的用户，或软删除

    安全考虑:
        - 实际生产环境应添加权限控制（仅管理员或本人可删除）
        - 可能需要软删除（标记deleted字段而非物理删除）
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(db_user)  # 删除用户对象，标记为删除状态
    db.commit()  # 提交事务，执行SQL DELETE
    return {"detail": "用户已删除"}  # 返回成功消息