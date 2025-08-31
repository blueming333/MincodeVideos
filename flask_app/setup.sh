#!/usr/bin/env bash

# MincodeVideos Flask版本 Linux/macOS 安装脚本

echo "🚀 MincodeVideos Flask版本 - 自动安装脚本"
echo "================================================"

# 获取脚本目录
SCRIPT_DIR="$(cd -- $(dirname -- "$0") && pwd)"
cd "$SCRIPT_DIR"

# 检查Python版本
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python版本检查通过: $python_version"
else
    echo "❌ Python版本过低: $python_version (需要 >= $required_version)"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
else
    echo "📦 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
python -m pip install --upgrade pip

# 安装依赖
echo "📚 安装Python依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ 找不到requirements.txt文件"
    exit 1
fi

# 检查FFmpeg
echo "🎬 检查FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg已安装: $(ffmpeg -version | head -n1)"
else
    echo "⚠️ 警告: FFmpeg未安装，视频处理功能可能无法正常工作"
    echo "请安装FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    echo "  CentOS: sudo yum install ffmpeg"
fi

# 复制配置文件
echo "⚙️ 初始化配置文件..."
if [ ! -f "../config/config.yml" ]; then
    if [ -f "../config/config.example.yml" ]; then
        cp "../config/config.example.yml" "../config/config.yml"
        echo "✅ 配置文件已创建"
    else
        echo "⚠️ 警告: 配置文件模板不存在"
    fi
else
    echo "✅ 配置文件已存在"
fi

# 创建必要目录
echo "📁 创建工作目录..."
mkdir -p ../work ../final ../temp

echo ""
echo "🎉 安装完成！"
echo "================================================"
echo "📖 使用说明:"
echo "   1. 运行: bash start.sh"
echo "   2. 浏览器打开: http://127.0.0.1:5000"
echo "   3. 首次使用请先完成系统配置"
echo ""
echo "💡 提示:"
echo "   • 配置文件位置: ../config/config.yml"
echo "   • 输出目录: ../final/"
echo "   • 工作目录: ../work/"
echo ""
echo "🔗 功能模块:"
echo "   • AI视频生成: http://127.0.0.1:5000/video/generate"
echo "   • 视频混剪: http://127.0.0.1:5000/mix/batch"
echo "   • 作品展示: http://127.0.0.1:5000/gallery/"
echo "   • 系统配置: http://127.0.0.1:5000/config/"

deactivate