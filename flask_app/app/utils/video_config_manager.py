"""
视频生成配置管理器
用于替代streamlit session_state，提供统一的配置管理
"""

from typing import Dict, Any, Optional
import threading


class VideoConfigManager:
    """视频配置管理器，替代streamlit session_state"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config = {}
            self._initialized = True
            self._set_defaults()
    
    def _set_defaults(self):
        """设置默认配置"""
        self.config.update({
            # 视频配置
            'video_fps': 30,
            'video_size': '720x1280',
            'video_layout': 'portrait',
            'video_segment_min_length': 5,
            'video_segment_max_length': 10,
            'enable_video_transition_effect': True,
            'video_transition_effect_type': 'xfade',
            'video_transition_effect_value': 'fade',
            'video_transition_effect_duration': '1',
            
            # 音频配置
            'audio_vol': 50,
            'audio_emotion': 'default',
            'audio_temperature': 0.3,
            'audio_top_p': 0.7,
            'text_seed': 42,
            'refine_text': False,
            'refine_text_prompt': '',
            
            # 背景音乐配置
            'enable_background_music': False,
            'background_music': '',
            'background_music_volume': 0.3,
            
            # 字幕配置
            'enable_subtitles': False,
            'subtitle_font': 'Arial',
            'subtitle_font_size': 24,
            'subtitle_color': '&Hffffff',
            'subtitle_border_color': '&H000000',
            'subtitle_border_width': 2,
            'subtitle_position': 2,
            
            # 识别配置
            'recognition_audio_type': 'local',
            
            # 场景配置
            'scene_number': 0,
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
    
    def update(self, config_dict: Dict[str, Any]):
        """批量更新配置"""
        self.config.update(config_dict)
    
    def get_video_config(self) -> Dict[str, Any]:
        """获取视频相关配置"""
        return {
            'fps': self.get('video_fps'),
            'size': self.get('video_size'),
            'layout': self.get('video_layout'),
            'segment_min_length': self.get('video_segment_min_length'),
            'segment_max_length': self.get('video_segment_max_length'),
            'enable_transition_effect': self.get('enable_video_transition_effect'),
            'transition_effect_type': self.get('video_transition_effect_type'),
            'transition_effect_value': self.get('video_transition_effect_value'),
            'transition_effect_duration': self.get('video_transition_effect_duration'),
        }
    
    def get_audio_config(self) -> Dict[str, Any]:
        """获取音频相关配置"""
        return {
            'vol': self.get('audio_vol'),
            'emotion': self.get('audio_emotion'),
            'temperature': self.get('audio_temperature'),
            'top_p': self.get('audio_top_p'),
            'text_seed': self.get('text_seed'),
            'refine_text': self.get('refine_text'),
            'refine_text_prompt': self.get('refine_text_prompt'),
        }
    
    def __contains__(self, key: str) -> bool:
        """检查配置是否存在"""
        return key in self.config
    
    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        if key not in self.config:
            raise KeyError(f'Configuration key "{key}" not found')
        return self.config[key]
    
    def __setitem__(self, key: str, value: Any):
        """支持字典式设置"""
        self.config[key] = value
    
    def items(self):
        """返回所有配置项"""
        return self.config.items()
    
    def keys(self):
        """返回所有配置键"""
        return self.config.keys()
    
    def values(self):
        """返回所有配置值"""
        return self.config.values()


# 全局配置管理器实例
video_config_manager = VideoConfigManager()


def get_video_config(key: str, default: Any = None) -> Any:
    """便捷函数：获取视频配置"""
    return video_config_manager.get(key, default)


def set_video_config(key: str, value: Any):
    """便捷函数：设置视频配置"""
    video_config_manager.set(key, value)


def update_video_config(config_dict: Dict[str, Any]):
    """便捷函数：批量更新视频配置"""
    video_config_manager.update(config_dict)
