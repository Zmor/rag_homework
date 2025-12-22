@echo off
REM RAG系统安装脚本（Windows版）

echo 开始安装RAG系统...

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    exit /b 1
)

echo √ Python检查通过

REM 创建虚拟环境
echo 创建虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo 错误: 创建虚拟环境失败
    exit /b 1
)

echo √ 虚拟环境创建完成

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 错误: 激活虚拟环境失败
    exit /b 1
)

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo 错误: 升级pip失败
    exit /b 1
)

echo √ pip升级完成

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 安装依赖包失败
    exit /b 1
)

echo √ 依赖包安装完成

REM 创建必要的目录
echo 创建必要的目录...
if not exist logs mkdir logs
if not exist chroma_db mkdir chroma_db

echo √ 目录创建完成

REM 检查环境变量文件
if not exist .env (
    echo 创建环境变量文件...
    copy .env.example .env
    echo ⚠️  请编辑 .env 文件，填入您的API密钥
) else (
    echo √ 环境变量文件已存在
)

REM 运行测试
echo 运行测试...
python run_tests.py
if %errorlevel% neq 0 (
    echo 警告: 测试运行失败，请检查配置
)

echo.
echo 安装完成！ 🎉
echo.
echo 下一步:
echo 1. 编辑 .env 文件，填入您的API密钥
echo 2. 运行示例: python examples\demo.py
echo 3. 使用命令行工具: python examples\cli.py --mode interactive
echo.
echo 要激活虚拟环境，请运行: venv\Scripts\activate.bat
echo 要退出虚拟环境，请运行: deactivate

REM 保持命令行窗口打开
echo.
echo 按任意键退出...
pause >nul