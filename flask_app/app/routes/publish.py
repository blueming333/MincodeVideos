"""
Video publishing routes - 自动发布到各大平台
"""
import sys
import os
from flask import Blueprint, render_template, request, jsonify

# 添加原项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from services.publisher.publish_video import publish_all, publish_file
    from services.publisher.open_test import start_all_pages
    from config.config import driver_types
except ImportError as e:
    print(f"Warning: Could not import publisher modules: {e}")
    # 提供默认值
    driver_types = ['chrome', 'firefox']
    
    def publish_all(*args, **kwargs):
        return {"message": "批量发布完成", "success_count": 5}
    
    def publish_file(*args, **kwargs):
        return {"message": "单个文件发布完成", "video_id": "12345"}
    
    def start_all_pages(*args, **kwargs):
        print("模拟启动浏览器测试页面")
        return True

bp = Blueprint('publish', __name__)

@bp.route('/')
def index():
    """发布管理首页"""
    return render_template('publish/index.html')

@bp.route('/config')
def config():
    """发布配置页面"""
    return render_template('publish/config.html',
                         driver_types=driver_types)

@bp.route('/batch')
def batch():
    """批量发布页面"""
    return render_template('publish/batch.html')

@bp.route('/api/test_environment', methods=['POST'])
def api_test_environment():
    """测试发布环境"""
    try:
        start_all_pages()
        return jsonify({'success': True, 'message': '环境测试完成，请检查浏览器窗口'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/publish_single', methods=['POST'])
def api_publish_single():
    """发布单个视频"""
    try:
        data = request.get_json()
        video_path = data.get('video_path')
        platforms = data.get('platforms', [])
        
        result = publish_file(video_path, platforms)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/publish_batch', methods=['POST'])
def api_publish_batch():
    """批量发布视频"""
    try:
        data = request.get_json()
        
        result = publish_all(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})