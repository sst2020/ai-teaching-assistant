# 实机部署指南（无 Docker）

本文档介绍如何在不使用 Docker 的服务器实机上部署 AI Teaching Assistant 项目。

## 环境要求

### 服务器要求
- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+ / Debian 11+)
- **CPU**: 2 核以上
- **内存**: 4GB 以上
- **磁盘**: 20GB 以上可用空间

### 依赖软件
- **Python**: 3.10 或更高版本
- **Node.js**: 18 LTS 或更高版本
- **MySQL**: 8.0 或更高版本
- **RabbitMQ**: 3.10 或更高版本（可选，用于异步任务）
- **Nginx**: 用于反向代理和静态文件服务
- **PM2**: 用于进程管理

---

## 1. 系统环境准备

### 1.1 安装基础依赖（Ubuntu/Debian）
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm mysql-server rabbitmq-server nginx git
```

### 1.2 安装基础依赖（CentOS/RHEL）
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip nodejs npm mysql-server rabbitmq-server nginx git
```

### 1.3 安装 PM2
```bash
sudo npm install -g pm2
```

---

## 2. 数据库配置

### 2.1 MySQL 配置
```bash
# 登录 MySQL
sudo mysql -u root

# 创建数据库和用户
CREATE DATABASE ai_teaching_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ai_teaching'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ai_teaching_assistant.* TO 'ai_teaching'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2.2 RabbitMQ 配置（可选）
```bash
# 创建 RabbitMQ 用户
sudo rabbitmqctl add_user ai_ta your_rabbitmq_password
sudo rabbitmqctl set_user_tags ai_ta administrator
sudo rabbitmqctl set_permissions -p / ai_ta ".*" ".*" ".*"

# 启用管理插件
sudo rabbitmq-plugins enable rabbitmq_management
sudo systemctl restart rabbitmq-server
```

---

## 3. 后端部署

### 3.1 代码部署
```bash
# 创建应用目录
sudo mkdir -p /opt/ai-teaching-assistant
sudo chown $USER:$USER /opt/ai-teaching-assistant

# 克隆代码（或上传代码）
cd /opt/ai-teaching-assistant
git clone <your-repo-url> .
```

### 3.2 Python 环境配置
```bash
cd /opt/ai-teaching-assistant/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3.3 环境变量配置
```bash
# 创建 .env 文件
cat > /opt/ai-teaching-assistant/backend/.env << 'EOF'
# 应用配置
APP_NAME=AI Teaching Assistant API
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# 服务器配置
HOST=0.0.0.0
PORT=9000
WORKERS=4

# 数据库配置
DATABASE_URL=mysql+aiomysql://ai_teaching:your_secure_password@localhost:3306/ai_teaching_assistant
DATABASE_ECHO=false

# RabbitMQ 配置（可选）
RABBITMQ_URL=amqp://ai_ta:your_rabbitmq_password@localhost:5672/

# 安全配置
SECRET_KEY=your-very-secure-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS 配置
CORS_ORIGINS=["https://your-frontend-domain.com"]

# AI/LLM 配置（根据实际使用配置）
OPENAI_API_KEY=your-openai-api-key
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
EOF
```

### 3.4 数据库初始化
```bash
cd /opt/ai-teaching-assistant/backend
source venv/bin/activate

# 运行数据库迁移（如果有 alembic）
alembic upgrade head

# 或者使用应用启动时自动创建表
python -c "from app.main import app; print('Database initialized')"
```

### 3.5 PM2 配置
```bash
cat > /opt/ai-teaching-assistant/backend/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'ai-teaching-backend',
      script: 'venv/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4',
      cwd: '/opt/ai-teaching-assistant/backend',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '/opt/ai-teaching-assistant/backend'
      },
      log_file: '/var/log/ai-teaching/backend.log',
      out_file: '/var/log/ai-teaching/backend-out.log',
      error_file: '/var/log/ai-teaching/backend-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
EOF

# 创建日志目录
sudo mkdir -p /var/log/ai-teaching
sudo chown $USER:$USER /var/log/ai-teaching

# 启动后端服务
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 4. 前端部署

### 4.1 构建前端
```bash
cd /opt/ai-teaching-assistant/frontend

# 安装依赖
npm install

# 创建生产环境配置
cat > .env.production << 'EOF'
VITE_API_URL=/api/v1
EOF

# 构建
npm run build
```

### 4.2 Nginx 配置
```bash
sudo tee /etc/nginx/sites-available/ai-teaching-assistant << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 前端静态文件
    location / {
        root /opt/ai-teaching-assistant/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }
    
    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:9000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用配置
sudo ln -sf /etc/nginx/sites-available/ai-teaching-assistant /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 5. HTTPS 配置（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo systemctl enable certbot.timer
```

---

## 6. 防火墙配置

```bash
# UFW（Ubuntu/Debian）
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 9000/tcp  # 后端 API（如果直接暴露）
sudo ufw enable

# 或者 firewalld（CentOS/RHEL）
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 7. 监控与日志

### 7.1 配置日志轮转
```bash
sudo tee /etc/logrotate.d/ai-teaching-assistant << 'EOF'
/var/log/ai-teaching/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
EOF
```

### 7.2 PM2 监控
```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs ai-teaching-backend

# 监控资源使用
pm2 monit
```

---

## 8. 备份策略

### 8.1 数据库备份脚本
```bash
cat > /opt/ai-teaching-assistant/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ai-teaching-assistant"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="ai_teaching_assistant"
DB_USER="ai_teaching"
DB_PASS="your_secure_password"

mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u$DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# 备份上传文件
if [ -d "/opt/ai-teaching-assistant/backend/uploads" ]; then
    tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/ai-teaching-assistant/backend uploads
fi

# 保留最近 30 天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x /opt/ai-teaching-assistant/scripts/backup.sh

# 添加定时任务（每天凌晨 2 点备份）
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ai-teaching-assistant/scripts/backup.sh") | crontab -
```

---

## 9. 更新部署

### 9.1 后端更新
```bash
cd /opt/ai-teaching-assistant/backend
source venv/bin/activate

# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 重启服务
pm2 restart ai-teaching-backend
```

### 9.2 前端更新
```bash
cd /opt/ai-teaching-assistant/frontend

# 拉取最新代码
git pull

# 重新构建
npm install
npm run build

# Nginx 会自动使用新的构建文件
```

---

## 10. 故障排查

### 10.1 检查服务状态
```bash
# 后端
pm2 status
pm2 logs ai-teaching-backend

# Nginx
sudo systemctl status nginx
sudo nginx -t

# MySQL
sudo systemctl status mysql

# RabbitMQ
sudo systemctl status rabbitmq-server
```

### 10.2 常见问题

**问题 1: 后端无法连接数据库**
- 检查数据库配置 `.env` 中的 `DATABASE_URL`
- 确认 MySQL 用户权限
- 检查 MySQL 是否运行: `sudo systemctl status mysql`

**问题 2: 前端无法访问后端 API**
- 检查 Nginx 配置中的反向代理设置
- 确认后端服务运行: `pm2 status`
- 查看 Nginx 错误日志: `sudo tail -f /var/log/nginx/error.log`

**问题 3: 权限问题**
- 确认文件权限: `sudo chown -R www-data:www-data /opt/ai-teaching-assistant`
- 确认日志目录权限: `sudo chown -R www-data:www-data /var/log/ai-teaching`

---

## 11. 安全加固建议

1. **使用非 root 用户运行服务**
2. **定期更新系统和依赖**
3. **配置 fail2ban 防止暴力破解**
4. **启用 MySQL SSL 连接**
5. **配置防火墙限制端口访问**
6. **定期更换密钥和密码**
7. **启用服务器访问日志审计**

---

## 端口对照表

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx HTTP | 80 | 前端服务 |
| Nginx HTTPS | 443 | 前端服务（SSL） |
| 后端 API | 9000 | 仅本地访问（通过 Nginx 代理） |
| MySQL | 3306 | 仅本地访问 |
| RabbitMQ | 5672 | 仅本地访问 |
| RabbitMQ 管理 | 15672 | 可选，建议限制访问 |

---

## 文件路径对照表

| 项目 | 路径 |
|------|------|
| 后端代码 | `/opt/ai-teaching-assistant/backend` |
| 前端代码 | `/opt/ai-teaching-assistant/frontend` |
| 前端构建文件 | `/opt/ai-teaching-assistant/frontend/dist` |
| 日志文件 | `/var/log/ai-teaching/` |
| 备份文件 | `/var/backups/ai-teaching-assistant/` |
| Nginx 配置 | `/etc/nginx/sites-available/ai-teaching-assistant` |

---

## 环境变量配置清单

| 变量 | 开发环境 | 生产环境 | 说明 |
|------|----------|----------|------|
| DEBUG | true | **false** | 关闭调试模式 |
| LOG_LEVEL | INFO | **INFO** | 日志级别 |
| PORT | 9000 | **9000** | 后端端口 |
| DATABASE_URL | localhost | **服务器地址** | 数据库连接 |
| SECRET_KEY | dev-key | **强密码** | JWT 密钥 |
| CORS_ORIGINS | ["*"] | **具体域名** | 跨域限制 |
| OPENAI_API_KEY | test-key | **真实密钥** | AI 服务 |

---

**注意**：部署前请务必将所有 `your-xxx` 占位符替换为实际的安全值。
