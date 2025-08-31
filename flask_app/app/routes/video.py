"""
Video generation routes - AI视频生成工作流
"""
import sys
import os
from flask import Blueprint, render_template, request, jsonify

# 添加原项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# 尝试导入原有模块
try:
    from main import main_generate_video_content, main_generate_ai_video, main_generate_video_dubbing
    from main import main_get_video_resource, main_generate_subtitle, main_try_test_audio
    from config.config import my_config
    original_modules_available = True
except ImportError as e:
    print(f"Warning: Could not import video modules: {e}")
    my_config = {}
    original_modules_available = False

# 如果原有模块不可用，提供模拟函数
if not original_modules_available:
    def main_generate_video_content(*args, **kwargs):
        return "模拟生成的视频内容"
    
    def main_generate_ai_video(*args, **kwargs):
        return "模拟生成的AI视频"
    
    def main_generate_video_dubbing(*args, **kwargs):
        return "模拟生成的视频配音"
    
    def main_get_video_resource(*args, **kwargs):
        return []
    
    def main_generate_subtitle(*args, **kwargs):
        return {"subtitle_path": "/path/to/subtitle.srt"}
    
    def main_try_test_audio(*args, **kwargs):
        return {"audio_url": "/test/audio.mp3"}

# 定义默认配置
audio_languages = {
    'zh-CN': '中文',
    'en-US': 'English', 
    'ja-JP': '日本語'
}

transition_types = {
    'fade': '淡入淡出',
    'slide': '滑动',
    'zoom': '缩放'
}

fade_list = ['in', 'out', 'inout']

bp = Blueprint('video', __name__)

@bp.route('/')
def index():
    """视频生成工作流首页"""
    return render_template('video/index.html')

@bp.route('/generate')
def generate():
    """AI视频生成页面 - 现代化的步骤向导"""
    return render_template('video/generate.html', 
                         audio_languages=audio_languages,
                         transition_types=transition_types,
                         fade_list=fade_list)

@bp.route('/api/generate_content', methods=['POST'])
def api_generate_content():
    """生成视频内容"""
    try:
        data = request.get_json()
        topic = data.get('topic')
        language = data.get('language', 'zh-CN')
        length = data.get('length', 120)
        
        # 调用原有的生成函数
        result = main_generate_video_content(topic, language, length)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/get_resources', methods=['POST'])
def api_get_resources():
    """获取视频资源"""
    try:
        data = request.get_json()
        content = data.get('content')
        
        result = main_get_video_resource(content)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/generate_dubbing', methods=['POST'])
def api_generate_dubbing():
    """生成配音"""
    try:
        data = request.get_json()
        content = data.get('content')
        voice_config = data.get('voice_config', {})
        
        result = main_generate_video_dubbing(content, voice_config)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/generate_subtitle', methods=['POST'])
def api_generate_subtitle():
    """生成字幕"""
    try:
        data = request.get_json()
        audio_path = data.get('audio_path')
        
        result = main_generate_subtitle(audio_path)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/generate_video', methods=['POST'])
def api_generate_video():
    """最终视频生成"""
    try:
        data = request.get_json()
        
        result = main_generate_ai_video(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/api/test_audio', methods=['POST'])
def api_test_audio():
    """测试音频服务"""
    try:
        data = request.get_json()
        text = data.get('text', '这是一个测试音频')
        
        result = main_try_test_audio(text)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})