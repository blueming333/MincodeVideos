"""
Flask Application Factory
"""
import os
import sys
from flask import Flask

# 添加父目录到Python路径，以便导入原有的服务模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 在任何其他导入之前安装streamlit适配器
from flask_app.app.utils.streamlit_adapter import install_streamlit_adapter
install_streamlit_adapter()

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 应用配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    
    # 初始化国际化
    from .utils.i18n import i18n
    i18n.init_app(app)
    
    # 注册蓝图
    from .routes import main, config, video, gallery, mix, publish, material
    from .routes.video_api import video_api
    from .routes.i18n_api import i18n_api
    
    app.register_blueprint(main.bp)
    app.register_blueprint(config.bp, url_prefix='/config')
    app.register_blueprint(video.video_bp, url_prefix='/video')
    app.register_blueprint(video_api)  # API路由
    app.register_blueprint(i18n_api)  # 国际化API路由
    app.register_blueprint(gallery.bp, url_prefix='/gallery')
    app.register_blueprint(mix.bp, url_prefix='/mix')
    app.register_blueprint(publish.bp, url_prefix='/publish')
    app.register_blueprint(material.bp, url_prefix='/material')
    
    return app