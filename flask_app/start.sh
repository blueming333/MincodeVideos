#!/usr/bin/env bash

# MincodeVideos Flask版本 Linux/macOS 启动脚本

# 获取脚本目录
SCRIPT_DIR="$(cd -- $(dirname -- "$0") && pwd)"
# 切换到根目录（父目录）
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "🚀 启动 MincodeVideos Flask版本..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行根目录的 setup.sh 进行安装"
    exit 1
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask未安装，正在安装依赖..."
    pip install flask pyyaml
fi

# 切换回flask_app目录
cd "$SCRIPT_DIR"

# 设置环境变量
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=True
export FLASK_HOST=127.0.0.1
export FLASK_PORT=5000

# 检查端口是否被占用
if lsof -i:$FLASK_PORT >/dev/null 2>&1; then
    echo "⚠️ 端口 $FLASK_PORT 已被占用，尝试使用其他端口..."
    export FLASK_PORT=5001
fi

echo "📍 启动地址: http://$FLASK_HOST:$FLASK_PORT"
echo "🔧 调试模式: 开启"
echo "📁 工作目录: $(pwd)"
echo "📂 虚拟环境: $ROOT_DIR/venv"
echo ""
echo "💡 按 Ctrl+C 停止服务器"
echo ""

# 启动Flask应用
python run.py

deactivate