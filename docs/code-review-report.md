# Flask Blog API 代码审查报告

**审查日期:** 2026-04-26
**项目类型:** 博客API (FastAPI + SQLAlchemy)
**审查范围:** app/ 目录所有代码

---

## 问题汇总

| 序号 | 问题 | 严重程度 | 文件 | 状态 |
|------|------|---------|------|------|
| 1 | 密码明文存储 | 🔴 高 | `routers/user.py` | 待修复 |
| 2 | 文章缺少分类处理 | 🔴 高 | `routers/post.py` | 待修复 |
| 3 | Schema放错位置 | 🟡 中 | `routers/categories.py` | 待修复 |
| 4 | CategoryResponse字段不完整 | 🟡 中 | `routers/categories.py` | 待修复 |
| 5 | 缺少用户认证机制 | 🔴 高 | 全局 | 待规划 |
| 6 | 代码注释格式问题 | 🟢 低 | `main.py:18` | 待修复 |
| 7 | 用户路由不完整 | 🟡 中 | `routers/user.py` | 待修复 |

---

## 详细分析

### 1. 密码明文存储 🔴 高危

**问题描述:** 用户注册时密码直接存储为明文，存在严重安全隐患。

**当前代码:**
```python
# routers/user.py:13
db_user = User(username=user.username, email=user.email, password=user.password)
```

**风险:**
- 数据库泄露会直接暴露用户密码
- 违反安全最佳实践
- 不符合OWASP安全标准

**修复方案:**
- 使用bcrypt加密密码
- 添加passlib依赖

---

### 2. 文章缺少分类处理 🔴 高危

**问题描述:** Post与Category是多对多关系，但创建/更新文章时没有处理分类关联。

**当前代码:**
```python
# routers/post.py:17-25
db_post = Post(
    title=post.title,
    content=post.content,
    summary=post.summary,
    author_id=post.author_id,
)  # 缺少categories处理
```

**影响:**
- 文章无法关联分类
- 多对多关系功能失效

**修复方案:**
- PostCreate添加category_ids字段
- 创建/更新时关联分类

---

### 3. Schema放错位置 🟡 中危

**问题描述:** CategoryBase/CategoryCreate/CategoryResponse定义在routers文件中，违反分层架构。

**当前代码:**
```python
# routers/categories.py:10-21
class CategoryBase(BaseModel):
    name: str
    ...
```

**影响:**
- 代码结构混乱
- 不符合项目分层规范（schemas独立目录）

**修复方案:**
- 创建 `schemas/category.py`
- 将Schema类移至该文件

---

### 4. CategoryResponse字段不完整 🟡 中危

**问题描述:** 响应Schema只有id字段，缺少name和description。

**当前代码:**
```python
# routers/categories.py:17-21
class CategoryResponse(BaseModel):
    id: int
    # 缺少 name, description
```

**影响:**
- API返回数据不完整
- 前端无法获取分类名称

---

### 5. 缺少用户认证机制 🔴 高危

**问题描述:** API无认证保护，任何人可调用所有接口。

**影响:**
- 任何人可创建/删除文章
- 无权限控制

**修复方案:**
- 添加JWT认证
- 创建auth模块（本次暂不实施，后续规划）

---

### 6. 代码注释格式问题 🟢 低危

**问题描述:** 注释前有多余空格。

**位置:** `main.py:18`

---

### 7. 用户路由不完整 🟡 中危

**问题描述:** 缺少update_user和delete_user路由。

**当前路由:**
- POST /users/ - 创建
- GET /users/ - 列表
- GET /users/{id} - 详情

**缺少:**
- PUT /users/{id} - 更新
- DELETE /users/{id} - 删除

---

## 修复计划

### 本次修复（优先级高）
1. ✅ 密码加密处理
2. ✅ 文章分类关联
3. ✅ Schema位置调整
4. ✅ CategoryResponse补全
5. ✅ 用户路由补全
6. ✅ 注释格式修正

### 后续规划
- 用户认证系统（JWT）
- 权限管理
- API限流

---

## 修复执行记录

| 序号 | 修复内容 | 修改文件 | 完成时间 |
|------|---------|---------|---------|
| 1 | 密码加密 | routers/user.py, requirements.txt | ✅ 完成 |
| 2 | 文章分类 | schemas/post.py, routers/post.py | ✅ 完成 |
| 3 | Schema迁移 | schemas/category.py, routers/categories.py | ✅ 完成 |
| 4 | 字段补全 | schemas/category.py | ✅ 完成 |
| 5 | 用户路由 | routers/user.py | ✅ 完成 |
| 6 | 注释格式 | main.py | ✅ 完成 |