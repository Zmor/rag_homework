#!/bin/bash

# RAG系统安装脚本

set -e

echo "开始安装RAG系统..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✓ Python版本检查通过: $python_version"

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

echo "✓ 虚拟环境创建完成"

# 升级pip
echo "升级pip..."
pip install --upgrade pip

echo "✓ pip升级完成"

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

echo "✓ 依赖包安装完成"

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs chroma_db

echo "✓ 目录创建完成"

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入您的API密钥"
else
    echo "✓ 环境变量文件已存在"
fi

# 运行测试
echo "运行测试..."
python run_tests.py

echo "✓ 测试运行完成"

echo ""
echo "安装完成！ 🎉"
echo ""
echo "下一步:"
echo "1. 编辑 .env 文件，填入您的API密钥"
echo "2. 运行示例: python examples/demo.py"
echo "3. 使用命令行工具: python examples/cli.py --mode interactive"
echo ""
echo "要激活虚拟环境，请运行: source venv/bin/activate"
echo "要退出虚拟环境，请运行: deactivate"