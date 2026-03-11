@echo off
chcp 65001 >nul

echo ==========================================
echo 社区志愿者管理系统
echo Community Volunteer Management System
echo ==========================================

REM 检查Python版本
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 创建必要目录
if not exist "uploads" mkdir uploads
if not exist "instance" mkdir instance

REM 启动系统
echo 启动系统...
echo 访问地址: http://localhost:5002
echo 管理员账号: admin / admin123
echo 按 Ctrl+C 停止系统
echo ==========================================

python run.py

pause
