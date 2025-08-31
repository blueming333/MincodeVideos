@echo off
chcp 65001

echo 🚀 启动 MincodeVideos Flask版本...

REM 获取脚本目录
set SCRIPT_DIR=%~dp0
REM 切换到根目录（父目录）
for %%i in ("%SCRIPT_DIR%..") do set ROOT_DIR=%%~fi
cd /d "%ROOT_DIR%"

REM 检查虚拟环境
if not exist "venv" (
    echo ❌ 虚拟环境不存在，请先运行根目录的 setup.bat 进行安装
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ❌ Flask未安装，正在安装依赖...
    pip install flask pyyaml
)

REM 切换回flask_app目录
cd /d "%SCRIPT_DIR%"

REM 设置环境变量
set FLASK_APP=run.py
set FLASK_ENV=development
set FLASK_DEBUG=True
set FLASK_HOST=127.0.0.1
set FLASK_PORT=5000

echo 📍 启动地址: http://%FLASK_HOST%:%FLASK_PORT%
echo 🔧 调试模式: 开启
echo 📁 工作目录: %CD%
echo 📂 虚拟环境: %ROOT_DIR%\venv
echo.
echo 💡 按 Ctrl+C 停止服务器
echo.

REM 启动Flask应用
python run.py

REM 停用虚拟环境
call venv\Scripts\deactivate.bat
pause