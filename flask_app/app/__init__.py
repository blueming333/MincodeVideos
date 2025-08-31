"""
Flask Application Factory
"""
import os
import sys
from flask import Flask

# 添加父目录到Python路径，以便导入原有的服务模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 应用配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    
    # 注册蓝图
    from .routes import main, config, video, gallery, mix, publish
    
    app.register_blueprint(main.bp)
    app.register_blueprint(config.bp, url_prefix='/config')
    app.register_blueprint(video.bp, url_prefix='/video')
    app.register_blueprint(gallery.bp, url_prefix='/gallery')
    app.register_blueprint(mix.bp, url_prefix='/mix')
    app.register_blueprint(publish.bp, url_prefix='/publish')
    
    return app