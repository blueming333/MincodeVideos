"""
Video generation routes - AI视频生成工作流
"""
from flask import Blueprint, render_template

video_bp = Blueprint('video', __name__)

@video_bp.route('/')
def index():
    """视频生成工作流首页"""
    return render_template('video/index.html')

@video_bp.route('/generate')
def generate():
    """视频生成页面"""
    # 提供默认配置给前端
    frontend_config = get_default_config()
    return render_template('video/generate.html', **frontend_config)

from flask import Blueprint, render_template
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

try:
    from config.config import my_config, audio_voices_azure, audio_voices_ali, audio_voices_tencent
    from services.audio.minmax_service import minmax_voices
    legacy_config_available = True
except ImportError:
    legacy_config_available = False
    my_config = {}
    audio_voices_azure = {}
    audio_voices_ali = {}
    audio_voices_tencent = {}
    minmax_voices = {}

# 使用新的配置管理器
try:
    from flask_app.app.utils.config_manager import config_manager
    config_manager_available = True
except ImportError:
    config_manager_available = False

video_bp = Blueprint('video', __name__)

def get_audio_voices():
    """根据配置的音频提供商获取语音选项"""
    if config_manager_available:
        return config_manager.get_audio_voices()
    
    # 向后兼容方式
    if legacy_config_available:
        selected_audio_provider = my_config.get('audio', {}).get('provider', '')
        if selected_audio_provider == 'Azure':
            return audio_voices_azure
        elif selected_audio_provider == 'Ali':
            return audio_voices_ali
        elif selected_audio_provider == 'Tencent':
            return audio_voices_tencent
        elif selected_audio_provider == 'MinMax':
            return minmax_voices
    
    # 默认返回一些基础语音选项
    return {
        'zh-CN': {
            'zhixiaobai': '智小白（女声）',
            'zhilingmei': '智灵美（女声）',
            'zhiyuanshan': '智远山（男声）'
        },
        'en-US': {
            'en_female_1': 'Sarah (Female)',
            'en_male_1': 'John (Male)'
        }
    }

def get_default_config():
    """获取默认配置"""
    return {
        'languages': {
            'zh-CN': '中文',
            'en-US': 'English',
            'ja-JP': '日本語'
        },
        'audio_types': {
            'remote': '在线语音',
            'local': '本地上传'
        },
        'audio_languages': {
            'zh-CN': '中文',
            'en-US': 'English',
        },
        'audio_voices': get_audio_voices(),
        'subtitle_fonts': [
            'PingFang SC Regular',
            'Songti SC Regular',
            'Arial',
            'Times New Roman',
            'Microsoft YaHei'
        ],
        'subtitle_positions': {
            0: '上方',
            1: '中间',
            2: '下方'
        }
    }

@video_bp.route('/generate')
def generate():
    """AI视频生成页面"""
    config = get_default_config()
    return render_template('video/generate.html', **config)