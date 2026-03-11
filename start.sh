#!/bin/bash

# 社区志愿者管理系统启动脚本
# Community Volunteer Management System Startup Script

echo "=========================================="
echo "社区志愿者管理系统"
echo "Community Volunteer Management System"
echo "=========================================="

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 创建必要目录
mkdir -p uploads
mkdir -p instance

# 启动系统
echo "启动系统..."
echo "访问地址: http://localhost:5002"
echo "管理员账号: admin / admin123"
echo "按 Ctrl+C 停止系统"
echo "=========================================="

python3 run.py
