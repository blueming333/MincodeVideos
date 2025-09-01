"""
Streamlit兼容适配器
为现有依赖streamlit的代码提供兼容性支持，使其能够使用新的配置管理器
"""

from flask_app.app.utils.video_config_manager import video_config_manager


class SessionStateAdapter:
    """模拟streamlit session_state的适配器"""
    
    def __init__(self):
        self._config_manager = video_config_manager
    
    def __getitem__(self, key: str):
        """支持 st.session_state[key] 语法"""
        return self._config_manager[key]
    
    def __setitem__(self, key: str, value):
        """支持 st.session_state[key] = value 语法"""
        self._config_manager[key] = value
    
    def __contains__(self, key: str):
        """支持 key in st.session_state 语法"""
        return key in self._config_manager
    
    def get(self, key: str, default=None):
        """支持 st.session_state.get(key, default) 语法"""
        return self._config_manager.get(key, default)
    
    def items(self):
        """支持遍历"""
        return self._config_manager.items()
    
    def keys(self):
        """支持获取所有键"""
        return self._config_manager.keys()
    
    def values(self):
        """支持获取所有值"""
        return self._config_manager.values()


class StreamlitAdapter:
    """模拟streamlit模块的适配器"""
    
    def __init__(self):
        self.session_state = SessionStateAdapter()
    
    @staticmethod
    def cache_data(ttl=300):
        """模拟streamlit的cache_data装饰器"""
        def decorator(func):
            return func
        return decorator


# 创建全局适配器实例
streamlit_adapter = StreamlitAdapter()


def install_streamlit_adapter():
    """安装streamlit适配器，替换真实的streamlit模块"""
    import sys
    sys.modules['streamlit'] = streamlit_adapter
    
    # 创建st别名
    sys.modules['st'] = streamlit_adapter
    
    return streamlit_adapter


def get_session_state():
    """获取session state实例"""
    return streamlit_adapter.session_state
