#!/usr/bin/env python3
"""
MincodeVideos Flask Application Entry Point
"""
import os
import sys
from app import create_app

# 确保工作目录正确
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 创建Flask应用
app = create_app()

if __name__ == '__main__':
    # 开发模式配置
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'on']
    port = int(os.environ.get('FLASK_PORT', 5000))
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    
    print(f"""
    🚀 MincodeVideos Flask 版本启动中...
    
    📍 访问地址: http://{host}:{port}
    {'🌐 外部访问: 已开启 (0.0.0.0)' if host == '0.0.0.0' else '🏠 本地访问: 仅限本机'}
    🔧 调试模式: {'开启' if debug_mode else '关闭'}
    📁 工作目录: {os.getcwd()}
    
    🎯 主要功能:
       • AI视频生成: http://{host}:{port}/video/generate
       • 视频混剪: http://{host}:{port}/mix/batch  
       • 作品展示: http://{host}:{port}/gallery/
       • 素材搜索: http://{host}:{port}/material/search
       • 系统配置: http://{host}:{port}/config/
    
    💡 提示: 首次使用请先完成系统配置
    """)
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )