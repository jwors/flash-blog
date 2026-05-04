# Flask Blog 项目启动指南

## 一、启动项目

### 方式 1：终端直接运行（推荐调试时使用）

打开终端，进入项目目录后运行：

```bash
cd E:\chyProject\flask-blog
python -m uvicorn app.main:app --reload --port 8009
```

**优点**：
- print 输出直接显示在终端
- 方便调试和查看日志
- Ctrl+C 即可停止

**停止**：按 `Ctrl+C`

---

### 方式 2：后台运行（Claude 自动执行）

Claude 使用后台任务启动服务器：

```bash
python -m uvicorn app.main:app --reload --port 8009
```

**注意**：
- print 输出不显示在终端（被写入日志文件）
- 需要手动终止进程才能停止

---

## 二、停止项目

### 方法 1：终止所有 Python 进程（推荐）

```bash
taskkill //F //IM python.exe
```

这会终止所有 Python 进程，包括服务器。

### 方法 2：查找并终止特定进程

```bash
# 查找占用 8009 端口的进程
netstat -ano | findstr :8009

# 终止特定 PID（替换为实际 PID）
taskkill //F //PID <PID>
```

---

## 三、何时需要重启

| 情况 | 是否自动重载 | 说明 |
|------|-------------|------|
| 修改 `.py` 文件 | ✅ 自动 | `--reload` 参数会自动检测并重载 |
| 修改 `.html` 模板 | ❌ 不自动 | Jinja2 模板修改需要刷新页面（无需重启） |
| 修改 `.css/.js` | ❌ 不自动 | 需要浏览器强制刷新（Ctrl+F5） |
| 修改 `requirements.txt` | ❌ 不自动 | 安装新依赖后需要重启 |
| 修改 `.env` 配置 | ❌ 不自动 | 需要重启服务器 |
| 数据库结构变化 | ❌ 不自动 | 需要重启（或重建数据库） |

### 手动重启命令

```bash
# 先停止
taskkill //F //IM python.exe

# 再启动
cd E:\chyProject\flask-blog
python -m uvicorn app.main:app --reload --port 8009
```

---

## 四、常见问题

### Q1: 端口被占用怎么办？

```bash
# 查找占用进程
netstat -ano | findstr :8009

# 终止进程
taskkill //F //PID <PID>
```

### Q2: 代码改了但没生效？

1. `.py` 文件：检查 `--reload` 是否生效，可能需要手动重启
2. `.css/.js`：浏览器缓存，按 `Ctrl+F5` 强制刷新
3. 新安装依赖：必须重启服务器

### Q3: print 输出看不到？

后台运行时 print 不显示。解决方案：

1. 使用终端直接运行（推荐调试时）
2. 使用 logging 代替 print：
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"debug info: {variable}")
   ```

### Q4: 为什么 Claude 告诉我项目停了但端口还在？

Claude 的后台任务（Background Task）会持续运行，即使对话中显示"项目已停止"。
后台任务只有在以下情况才会停止：
- Claude 主动执行 `taskkill` 命令
- 系统重启
- 手动终止进程

---

## 五、访问地址

启动后可访问：

| 页面 | URL |
|------|-----|
| 首页 | http://127.0.0.1:8009/ |
| 写文章 | http://127.0.0.1:8009/write |
| 登录 | http://127.0.0.1:8009/auth/login |
| 注册 | http://127.0.0.1:8009/auth/register |
| API 文档 | http://127.0.0.1:8009/docs |

---

## 六、推荐开发流程

1. **启动服务器**：终端直接运行 `uvicorn`
2. **修改代码**：自动重载生效
3. **调试**：print 输出直接可见
4. **完成后**：Ctrl+C 停止，git commit