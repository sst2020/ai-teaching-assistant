@echo off
REM ============================================
REM AI Teaching Assistant Backend - 依赖安装脚本
REM ============================================
echo [INFO] 开始安装后端依赖...
echo.

REM 激活 Conda 环境
echo [STEP 1] 激活 Conda 环境: ai_teaching_assistant_backend
call conda activate ai_teaching_assistant_backend
if errorlevel 1 (
    echo [ERROR] 环境激活失败
    exit /b 1
)
echo [SUCCESS] 环境激活成功
echo.

REM 验证 Python 版本
echo [STEP 2] 验证 Python 版本
python --version
if errorlevel 1 (
    echo [ERROR] Python 未找到
    exit /b 1
)
echo [SUCCESS] Python 版本验证通过
echo.

REM 使用 Conda 安装基础包
echo [STEP 3] 使用 Conda 安装基础包...
echo [INFO] 安装数据库和开发工具包（这可能需要几分钟）...
call conda install -c conda-forge -y sqlalchemy psycopg2 alembic pytest black isort mypy aiofiles cachetools
if errorlevel 1 (
    echo [WARNING] Conda 安装部分失败，将继续使用 pip 安装
) else (
    echo [SUCCESS] Conda 包安装完成
)
echo.

REM 使用 Pip 安装所有依赖
echo [STEP 4] 使用 Pip 安装 requirements.txt 中的所有依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Pip 安装失败
    exit /b 1
)
echo [SUCCESS] Pip 依赖安装完成
echo.

REM 验证关键包安装
echo [STEP 5-8] 验证关键包安装...
echo [INFO] 验证 FastAPI...
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
if errorlevel 1 (
    echo [ERROR] FastAPI 导入失败
    exit /b 1
)

echo [INFO] 验证 SQLAlchemy...
python -c "import sqlalchemy; print('SQLAlchemy version:', sqlalchemy.__version__)"
if errorlevel 1 (
    echo [ERROR] SQLAlchemy 导入失败
    exit /b 1
)

echo [INFO] 验证 OpenAI...
python -c "import openai; print('OpenAI version:', openai.__version__)"
if errorlevel 1 (
    echo [ERROR] OpenAI 导入失败
    exit /b 1
)

echo [INFO] 验证 Pydantic...
python -c "import pydantic; print('Pydantic version:', pydantic.__version__)"
if errorlevel 1 (
    echo [ERROR] Pydantic 导入失败
    exit /b 1
)
echo [SUCCESS] 所有关键包验证通过
echo.

REM 导出环境配置
echo [STEP 9] 导出环境配置到 environment.yml...
call conda env export > environment.yml
if errorlevel 1 (
    echo [WARNING] 环境导出失败
) else (
    echo [SUCCESS] 环境配置已导出到 backend/environment.yml
)
echo.

REM 生成已安装包列表
echo [STEP 10] 生成已安装包列表...
pip list > installed_packages.txt
if errorlevel 1 (
    echo [WARNING] 包列表生成失败
) else (
    echo [SUCCESS] 包列表已保存到 backend/installed_packages.txt
)
echo.

REM 运行完整的包导入测试
echo [STEP 11] 运行完整的包导入测试...
python -c "import fastapi, uvicorn, sqlalchemy, pydantic, openai, aiofiles, pytest, black; print('[SUCCESS] 所有核心包导入成功')"
if errorlevel 1 (
    echo [ERROR] 包导入测试失败
    exit /b 1
)
echo.

REM 显示安装摘要
echo [STEP 12] 安装完成摘要
echo ============================================
echo [SUCCESS] 依赖安装完成！
echo.
echo 已安装的关键包:
pip list | findstr /i "fastapi uvicorn sqlalchemy pydantic openai pytest black"
echo.
echo 环境配置文件: backend/environment.yml
echo 包列表文件: backend/installed_packages.txt
echo ============================================
echo.
echo [INFO] 您现在可以运行后端服务了
echo [INFO] 使用命令: uvicorn app.main:app --reload
echo.

pause

