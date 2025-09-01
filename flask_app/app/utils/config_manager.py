"""
配置管理器 - 解决配置动态更新问题
提供配置的动态加载和刷新功能
"""
import os
import sys
import yaml
import threading
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
sys.path.insert(0, project_root)


class ConfigManager:
    """配置管理器 - 单例模式，确保配置的一致性"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_path = os.path.join(project_root, 'config', 'config.yml')
            self._config = None
            self._load_config()
            self.initialized = True
    
    def _load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = self._get_default_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'ui': {'language': 'zh-CN'},
            'llm': {'provider': 'OpenAI'},
            'audio': {'provider': 'Azure'},
            'resource': {'provider': 'pexels'},
            'publisher': {'driver_type': 'chrome'}
        }
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self._config.copy()
    
    def get(self, key_path: str, default=None):
        """
        获取配置值，支持嵌套路径
        例如: get('audio.provider') 获取 config['audio']['provider']
        """
        keys = key_path.split('.')
        value = self._config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值，支持嵌套路径
        例如: set('audio.provider', 'Ali') 设置 config['audio']['provider'] = 'Ali'
        """
        keys = key_path.split('.')
        config_ref = self._config
        
        # 确保路径存在
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        config_ref[keys[-1]] = value
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新整个配置"""
        self._config = new_config
    
    def save_config(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            print(f"配置已保存到: {self.config_path}")
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def reload_config(self):
        """重新加载配置"""
        self._load_config()
        print("配置已重新加载")
    
    def get_audio_provider(self) -> str:
        """获取音频提供商"""
        return self.get('audio.provider', 'Azure')
    
    def get_audio_voices(self) -> Dict[str, Dict[str, str]]:
        """根据配置的音频提供商获取语音选项"""
        provider = self.get_audio_provider()
        
        try:
            if provider == 'Azure':
                from config.config import audio_voices_azure
                return audio_voices_azure
            elif provider == 'Ali':
                from config.config import audio_voices_ali
                return audio_voices_ali
            elif provider == 'Tencent':
                from config.config import audio_voices_tencent
                return audio_voices_tencent
            elif provider == 'MinMax':
                from services.audio.minmax_service import minmax_voices
                return minmax_voices
        except ImportError as e:
            print(f"导入语音配置失败: {e}")
        
        # 默认返回基础语音选项
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


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config() -> Dict[str, Any]:
    """获取当前配置"""
    return config_manager.get_config()


def get_config_value(key_path: str, default=None):
    """获取配置值"""
    return config_manager.get(key_path, default)


def update_config(new_config: Dict[str, Any]):
    """更新配置"""
    config_manager.update_config(new_config)
    return config_manager.save_config()


def reload_config():
    """重新加载配置"""
    config_manager.reload_config()


def get_audio_service():
    """获取音频服务实例"""
    provider = config_manager.get_audio_provider()
    
    try:
        if provider == 'Azure':
            from services.audio.azure_service import AzureAudioService
            return AzureAudioService()
        elif provider == 'Ali':
            from services.audio.alitts_service import AliAudioService
            return AliAudioService()
        elif provider == 'Tencent':
            from services.audio.tencent_tts_service import TencentAudioService
            return TencentAudioService()
        elif provider == 'MinMax':
            from services.audio.minmax_service import MinMaxAudioService
            return MinMaxAudioService()
    except ImportError as e:
        print(f"导入音频服务失败 ({provider}): {e}")
    
    # 返回默认服务
    from services.audio.azure_service import AzureAudioService
    return AzureAudioService()
