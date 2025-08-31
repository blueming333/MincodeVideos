"""
Video gallery routes - 视频作品展示
"""
import sys
import os
from flask import Blueprint, render_template, request, jsonify, send_file

# 添加原项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from tools.video_utils import get_video_files_info, format_file_size
except ImportError as e:
    print(f"Warning: Could not import video utils: {e}")
    # 提供默认值
    def get_video_files_info(directory):
        return [
            {
                "filename": "示例视频1.mp4",
                "filepath": "/path/to/video1.mp4",
                "size_formatted": "25.6 MB",
                "create_time_formatted": "2024-08-31 10:30"
            },
            {
                "filename": "示例视频2.mp4",
                "filepath": "/path/to/video2.mp4",
                "size_formatted": "18.2 MB",
                "create_time_formatted": "2024-08-31 11:15"
            }
        ]
    
    def format_file_size(size_bytes):
        return f"{size_bytes / 1024 / 1024:.1f} MB"

bp = Blueprint('gallery', __name__)

@bp.route('/')
def index():
    """视频画廊首页 - 现代化的卡片布局"""
    return render_template('gallery/index.html')

@bp.route('/api/videos')
def api_videos():
    """获取视频列表API"""
    try:
        directory = request.args.get('directory', './final')
        videos = get_video_files_info(directory)
        return jsonify({'success': True, 'data': videos})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/download/<path:filename>')
def api_download(filename):
    """下载视频文件"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})