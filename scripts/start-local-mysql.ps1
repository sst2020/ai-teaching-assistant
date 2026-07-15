# 本地开发环境启动脚本（使用本地 MySQL）
# 使用方法: .\scripts\start-local-mysql.ps1

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Green
Write-Host "AI Teaching Assistant 本地启动脚本" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# 项目路径
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

# 检查 MySQL 是否运行
Write-Host "[1/5] 检查 MySQL 服务..." -ForegroundColor Yellow
try {
    $mysqlStatus = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($mysqlStatus -and $mysqlStatus.Status -eq "Running") {
        Write-Host "MySQL 服务正在运行" -ForegroundColor Green
    } else {
        Write-Host "警告: MySQL 服务未运行，尝试启动..." -ForegroundColor Yellow
        Start-Service -Name "MySQL*" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
} catch {
    Write-Host "警告: 无法检查 MySQL 服务状态，请手动确保 MySQL 已启动" -ForegroundColor Yellow
}

# 设置后端环境变量
Write-Host "[2/5] 配置后端环境..." -ForegroundColor Yellow
$env:APP_NAME = "AI Teaching Assistant API"
$env:APP_VERSION = "1.0.0"
$env:DEBUG = "true"
$env:LOG_LEVEL = "INFO"
$env:HOST = "127.0.0.1"
$env:PORT = "9000"
$env:WORKERS = "1"
$env:DATABASE_URL = "mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant"
$env:DATABASE_ECHO = "false"
$env:RABBITMQ_URL = ""  # 禁用 RabbitMQ
$env:SECRET_KEY = "local-dev-secret-key"
$env:CORS_ORIGINS = '["http://localhost:3000","http://127.0.0.1:3000"]'
$env:RATE_LIMIT_ENABLED = "false"

# 检查端口占用
Write-Host "[3/5] 检查端口占用..." -ForegroundColor Yellow
$ports = @(9000, 3000)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "端口 $port 被占用，尝试释放..." -ForegroundColor Yellow
        $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($process) {
            Stop-Process -Id $process.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

# 启动后端
Write-Host "[4/5] 启动后端服务..." -ForegroundColor Yellow
$backendCmd = "cd '$BackendDir'; .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowTitle "Backend (Port 9000)"

# 等待后端启动
Start-Sleep -Seconds 5

# 检查后端是否启动成功
try {
    $response = Invoke-RestMethod -Uri "http://localhost:9000/health" -Method GET -TimeoutSec 5
    Write-Host "后端服务已启动" -ForegroundColor Green
} catch {
    Write-Host "警告: 后端可能未正常启动，请检查后端窗口的错误信息" -ForegroundColor Red
}

# 启动前端
Write-Host "[5/5] 启动前端服务..." -ForegroundColor Yellow
$frontendCmd = "cd '$FrontendDir'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowTitle "Frontend (Port 3000)"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "服务启动中..." -ForegroundColor Green
Write-Host "后端: http://localhost:9000" -ForegroundColor Yellow
Write-Host "前端: http://localhost:3000" -ForegroundColor Yellow
Write-Host "API文档: http://localhost:9000/docs" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "请确保:" -ForegroundColor Cyan
Write-Host "1. MySQL 已启动并运行" -ForegroundColor Cyan
Write-Host "2. 数据库 'ai_teaching_assistant' 已创建" -ForegroundColor Cyan
Write-Host "3. 用户 'ai_teaching'@'localhost' 已创建并授权" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键停止所有服务..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 停止服务
Write-Host "正在停止服务..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.MainWindowTitle -match "Backend \(Port 9000\)|Frontend \(Port 3000\)"} | Stop-Process -Force

Write-Host "服务已停止" -ForegroundColor Green
