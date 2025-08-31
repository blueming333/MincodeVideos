@echo off
chcp 65001

echo 🚀 MincodeVideos Flask版本 - Windows 安装脚本
echo ================================================

REM 获取脚本目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请下载并安装Python 3.8+: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

REM 创建虚拟环境
if not exist "venv" (
    echo 📦 创建Python虚拟环境...
    python -m venv venv
) else (
    echo 📦 虚拟环境已存在
)

REM 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo ⬆️ 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📚 安装Python依赖包...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo ❌ 找不到requirements.txt文件
    pause
    exit /b 1
)

REM 检查FFmpeg
echo 🎬 检查FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 警告: FFmpeg未安装，视频处理功能可能无法正常工作
    echo 请下载FFmpeg: https://ffmpeg.org/download.html#build-windows
    echo 并将ffmpeg.exe添加到系统PATH
) else (
    echo ✅ FFmpeg已安装
)

REM 复制配置文件
echo ⚙️ 初始化配置文件...
if not exist "..\config\config.yml" (
    if exist "..\config\config.example.yml" (
        copy "..\config\config.example.yml" "..\config\config.yml"
        echo ✅ 配置文件已创建
    ) else (
        echo ⚠️ 警告: 配置文件模板不存在
    )
) else (
    echo ✅ 配置文件已存在
)

REM 创建必要目录
echo 📁 创建工作目录...
if not exist "..\work" mkdir "..\work"
if not exist "..\final" mkdir "..\final"
if not exist "..\temp" mkdir "..\temp"

echo.
echo 🎉 安装完成！
echo ================================================
echo 📖 使用说明:
echo    1. 运行: start.bat
echo    2. 浏览器打开: http://127.0.0.1:5000
echo    3. 首次使用请先完成系统配置
echo.
echo 💡 提示:
echo    • 配置文件位置: ..\config\config.yml
echo    • 输出目录: ..\final\
echo    • 工作目录: ..\work\
echo.
echo 🔗 功能模块:
echo    • AI视频生成: http://127.0.0.1:5000/video/generate
echo    • 视频混剪: http://127.0.0.1:5000/mix/batch
echo    • 作品展示: http://127.0.0.1:5000/gallery/
echo    • 系统配置: http://127.0.0.1:5000/config/

call venv\Scripts\deactivate.bat
pause