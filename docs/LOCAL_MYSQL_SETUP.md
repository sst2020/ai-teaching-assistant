# 本地 MySQL 开发环境配置指南

本文档介绍如何在本地（不使用 Docker）配置 MySQL 数据库进行开发测试。

## 前置条件

确保本地已安装 MySQL Server 8.0+ 并正在运行。

### 检查 MySQL 服务状态

**Windows:**
```powershell
# 检查 MySQL 服务状态
Get-Service -Name "MySQL*"

# 如果未运行，启动 MySQL 服务
Start-Service -Name "MySQL80"  # 或 MySQL57，根据你的版本
```

**macOS:**
```bash
brew services start mysql
```

**Linux:**
```bash
sudo systemctl status mysql
sudo systemctl start mysql
```

---

## 数据库初始化

### 步骤 1: 登录 MySQL

```bash
# 使用 root 用户登录
mysql -u root -p

# 或者如果使用默认空密码
mysql -u root
```

### 步骤 2: 创建数据库

```sql
-- 创建数据库，使用 utf8mb4 字符集支持中文和 emoji
CREATE DATABASE IF NOT EXISTS ai_teaching_assistant 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- 查看创建结果
SHOW DATABASES;
```

### 步骤 3: 创建用户并授权

```sql
-- 创建专用用户（推荐）
CREATE USER IF NOT EXISTS 'ai_teaching'@'localhost' 
  IDENTIFIED BY 'ai_teaching_dev';

-- 授权（开发环境可以使用所有权限）
GRANT ALL PRIVILEGES ON ai_teaching_assistant.* 
  TO 'ai_teaching'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证用户
SELECT user, host FROM mysql.user WHERE user = 'ai_teaching';
SHOW GRANTS FOR 'ai_teaching'@'localhost';
```

### 步骤 4: 测试连接

```bash
# 使用新用户登录测试
mysql -u ai_teaching -p ai_teaching_assistant

# 输入密码: ai_teaching_dev

# 测试命令
SHOW TABLES;
EXIT;
```

---

## 启动开发服务

数据库配置完成后，使用以下脚本启动开发服务：

### Windows

```batch
# 在项目根目录执行
scripts\start-local.bat
```

或手动启动：

```batch
# 终端 1: 启动后端
cd backend
set DATABASE_URL=mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload

# 终端 2: 启动前端
cd frontend
npm run dev
```

### Linux/macOS

```bash
# 在项目根目录执行
chmod +x scripts/start-local.sh
./scripts/start-local.sh
```

---

## 故障排查

### 问题 1: MySQL 连接被拒绝

**错误信息:**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'localhost'")
```

**解决方案:**
1. 确认 MySQL 服务已启动
2. 检查 MySQL 端口（默认 3306）
3. 检查防火墙设置

```bash
# 检查端口
netstat -an | findstr 3306  # Windows
lsof -i :3306               # macOS/Linux
```

### 问题 2: 用户认证失败

**错误信息:**
```
Access denied for user 'ai_teaching'@'localhost'
```

**解决方案:**
```sql
-- 重置用户密码
ALTER USER 'ai_teaching'@'localhost' 
  IDENTIFIED BY 'ai_teaching_dev';
FLUSH PRIVILEGES;
```

### 问题 3: aiomysql 模块未找到

**错误信息:**
```
ModuleNotFoundError: No module named 'aiomysql'
```

**解决方案:**
```bash
cd backend
.\venv\Scripts\pip.exe install aiomysql pymysql
```

### 问题 4: 数据库表未创建

**解决方案:**
后端启动时会自动创建表结构（基于 SQLAlchemy models）。
如果需要手动创建，可以使用 Alembic 迁移：

```bash
cd backend
.\venv\Scripts\alembic.exe upgrade head
```

---

## 配置说明

### 后端数据库连接配置

启动脚本中已设置以下环境变量：

```batch
DATABASE_URL=mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant
```

如果需要修改，可以在以下位置调整：
- `scripts/start-local.bat` (Windows)
- `scripts/start-local.sh` (Linux/macOS)

### 连接字符串格式

```
mysql+aiomysql://用户名:密码@主机:端口/数据库名
```

**示例:**
- 本地开发: `mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant`
- 使用 IP: `mysql+aiomysql://user:pass@127.0.0.1:3306/dbname`
- 使用 Socket: `mysql+aiomysql://user:pass@/dbname?unix_socket=/tmp/mysql.sock`

---

## 安全提示

⚠️ **开发环境配置仅用于本地开发，请勿用于生产环境！**

生产环境应该：
1. 使用强密码
2. 限制数据库用户权限（仅授予必要权限）
3. 启用 SSL 连接
4. 配置防火墙限制访问
5. 定期备份数据

---

## 相关文档

- [实机部署指南](./PRODUCTION_DEPLOYMENT.md) - 生产环境部署说明
- [部署检查清单](./DEPLOYMENT_CHECKLIST.md) - 部署前检查项
