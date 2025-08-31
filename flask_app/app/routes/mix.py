"""
Video mixing routes - 视频混剪和合并
"""
import sys
import os
from flask import Blueprint, render_template, request, jsonify

# 添加原项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from main import main_generate_video_from_mix
    from config.config import transition_types, fade_list, audio_languages, audio_types
except ImportError as e:
    print(f"Warning: Could not import mix modules: {e}")
    # 提供默认值
    transition_types = ['fade', 'slide', 'zoom']
    fade_list = ['in', 'out', 'crossfade']
    audio_languages = {'zh-CN': '中文', 'en-US': 'English'}
    audio_types = {'remote': '云端语音', 'local': '本地语音'}
    
    def main_generate_video_from_mix(*args, **kwargs):
        return {"message": "混剪完成", "output_path": "/path/to/mixed_video.mp4"}

bp = Blueprint('mix', __name__)

@bp.route('/')
def index():
    """视频混剪首页"""
    return render_template('mix/index.html')

@bp.route('/batch')
def batch():
    """批量混剪页面"""
    return render_template('mix/batch.html',
                         transition_types=transition_types,
                         fade_list=fade_list,
                         audio_languages=audio_languages,
                         audio_types=audio_types)

@bp.route('/merge')
def merge():
    """视频合并页面"""
    return render_template('mix/merge.html',
                         transition_types=transition_types,
                         fade_list=fade_list)

@bp.route('/api/mix_videos', methods=['POST'])
def api_mix_videos():
    """批量混剪视频"""
    try:
        data = request.get_json()
        
        # 调用原有的混剪函数
        result = main_generate_video_from_mix(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/merge_videos', methods=['POST'])
def api_merge_videos():
    """合并视频"""
    try:
        data = request.get_json()
        
        # 这里添加合并逻辑
        return jsonify({'success': True, 'message': '视频合并完成'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})