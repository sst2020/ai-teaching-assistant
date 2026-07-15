# 实机部署检查清单

## 前置条件

- [ ] 服务器已准备（Linux Ubuntu 20.04+/CentOS 8+）
- [ ] 域名已解析到服务器 IP
- [ ] SSH 已配置，可以远程登录

## 第一步：系统环境

- [ ] 更新系统包
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

- [ ] 安装必要软件
  ```bash
  sudo apt install -y python3 python3-pip python3-venv nodejs npm \
    mysql-server rabbitmq-server nginx git curl
  ```

- [ ] 安装 PM2
  ```bash
  sudo npm install -g pm2
  ```

- [ ] 创建应用目录
  ```bash
  sudo mkdir -p /opt/ai-teaching-assistant
  sudo chown $USER:$USER /opt/ai-teaching-assistant
  ```

## 第二步：数据库

- [ ] MySQL 已启动
  ```bash
  sudo systemctl status mysql
  ```

- [ ] 创建数据库和用户
  ```sql
  CREATE DATABASE ai_teaching_assistant;
  CREATE USER 'ai_teaching'@'localhost' IDENTIFIED BY '强密码';
  GRANT ALL PRIVILEGES ON ai_teaching_assistant.* TO 'ai_teaching'@'localhost';
  ```

- [ ] RabbitMQ 已启动（可选）
  ```bash
  sudo systemctl status rabbitmq-server
  ```

## 第三步：后端部署

- [ ] 代码已上传到 `/opt/ai-teaching-assistant`

- [ ] 创建 Python 虚拟环境
  ```bash
  cd /opt/ai-teaching-assistant/backend
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

- [ ] 配置 `.env` 文件
  ```bash
  cp .env.production.example .env
  # 编辑 .env，修改所有占位符
  ```

- [ ] 关键配置项已修改
  - [ ] `DATABASE_URL` - 数据库连接字符串
  - [ ] `SECRET_KEY` - JWT 密钥（强随机字符串）
  - [ ] `CORS_ORIGINS` - 前端域名
  - [ ] `OPENAI_API_KEY` - AI API 密钥
  - [ ] `DEBUG=false` - 关闭调试模式

- [ ] 数据库初始化
  ```bash
  alembic upgrade head
  ```

- [ ] PM2 配置已创建
  ```bash
  pm2 start ecosystem.config.js
  pm2 save
  pm2 startup
  ```

- [ ] 后端服务运行正常
  ```bash
  pm2 status
  curl http://localhost:9000/health
  ```

## 第四步：前端部署

- [ ] 安装前端依赖
  ```bash
  cd /opt/ai-teaching-assistant/frontend
  npm install
  ```

- [ ] 创建生产环境配置
  ```bash
  echo "VITE_API_URL=/api/v1" > .env.production
  ```

- [ ] 构建前端
  ```bash
  npm run build
  ```

- [ ] 确认 `dist` 目录已生成
  ```bash
  ls -la /opt/ai-teaching-assistant/frontend/dist
  ```

## 第五步：Nginx 配置

- [ ] 创建 Nginx 配置文件
  ```bash
  sudo tee /etc/nginx/sites-available/ai-teaching-assistant
  ```

- [ ] 配置内容检查
  - [ ] 前端静态文件路径正确
  - [ ] 后端 API 反向代理配置正确
  - [ ] 域名配置正确

- [ ] 启用配置
  ```bash
  sudo ln -s /etc/nginx/sites-available/ai-teaching-assistant \
    /etc/nginx/sites-enabled/
  sudo rm -f /etc/nginx/sites-enabled/default
  ```

- [ ] 测试配置并重启
  ```bash
  sudo nginx -t
  sudo systemctl restart nginx
  ```

- [ ] Nginx 运行正常
  ```bash
  sudo systemctl status nginx
  ```

## 第六步：HTTPS（Let's Encrypt）

- [ ] 安装 Certbot
  ```bash
  sudo apt install -y certbot python3-certbot-nginx
  ```

- [ ] 申请证书
  ```bash
  sudo certbot --nginx -d your-domain.com -d www.your-domain.com
  ```

- [ ] 证书自动续期已配置
  ```bash
  sudo systemctl status certbot.timer
  ```

## 第七步：防火墙

- [ ] 配置防火墙规则
  ```bash
  sudo ufw allow 22/tcp
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```

- [ ] 确认后端端口 9000 未对外开放（仅本地）

## 第八步：日志与监控

- [ ] 创建日志目录
  ```bash
  sudo mkdir -p /var/log/ai-teaching
  sudo chown www-data:www-data /var/log/ai-teaching
  ```

- [ ] 配置日志轮转
  ```bash
  sudo tee /etc/logrotate.d/ai-teaching-assistant
  ```

- [ ] PM2 日志正常
  ```bash
  pm2 logs ai-teaching-backend --lines 20
  ```

## 第九步：备份

- [ ] 创建备份脚本
  ```bash
  /opt/ai-teaching-assistant/scripts/backup.sh
  ```

- [ ] 配置定时任务
  ```bash
  crontab -l | grep backup
  ```

## 第十步：验证测试

- [ ] 前端页面可访问
  ```
  https://your-domain.com
  ```

- [ ] API 文档可访问
  ```
  https://your-domain.com/api/docs
  ```

- [ ] 注册功能正常

- [ ] 登录功能正常

- [ ] 登录后可跳转到 Dashboard

- [ ] 刷新页面后仍保持登录状态

## 故障排查

如果出现问题，检查以下日志：

1. **后端日志**
   ```bash
   pm2 logs ai-teaching-backend
   ```

2. **Nginx 错误日志**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Nginx 访问日志**
   ```bash
   sudo tail -f /var/log/nginx/access.log
   ```

4. **MySQL 日志**
   ```bash
   sudo tail -f /var/log/mysql/error.log
   ```

## 部署后安全加固

- [ ] 修改默认 SSH 端口（可选）
- [ ] 禁用 root 登录
- [ ] 配置 fail2ban
- [ ] 定期更新系统和依赖
- [ ] 配置数据库定期备份
- [ ] 启用服务器监控告警

---

**部署完成！** 🎉
