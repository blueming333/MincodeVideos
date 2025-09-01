"""
Flask兼容的资源服务基类
替换原本的streamlit依赖，支持Flask应用的资源搜索
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from const.video_const import Orientation


class BaseResourceService(ABC):
    """Flask兼容的资源服务基类"""
    
    def __init__(self, 
                 orientation: str = "landscape",
                 width: int = 1920, 
                 height: int = 1080,
                 fps: int = 30,
                 video_segment_min_length: int = 3,
                 video_segment_max_length: int = 15,
                 enable_video_transition_effect: bool = False,
                 video_transition_effect_duration: float = 1.0):
        """
        初始化资源服务
        
        Args:
            orientation: 视频方向 (landscape/portrait/square)
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            video_segment_min_length: 最小片段长度（秒）
            video_segment_max_length: 最大片段长度（秒）
            enable_video_transition_effect: 是否启用转场效果
            video_transition_effect_duration: 转场效果持续时间（秒）
        """
        self.orientation = Orientation(orientation)
        self.width = width
        self.height = height
        self.fps = fps
        self.video_segment_min_length = video_segment_min_length
        self.video_segment_max_length = video_segment_max_length
        self.enable_video_transition_effect = enable_video_transition_effect
        self.video_transition_effect_duration = video_transition_effect_duration

    @abstractmethod
    def search_videos(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """
        搜索视频资源
        
        Args:
            query: 搜索关键词
            per_page: 每页结果数量
            
        Returns:
            搜索结果的原始数据
        """
        raise NotImplementedError

    @abstractmethod
    def extract_video_info(self, video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从原始搜索结果中提取标准化的视频信息
        
        Args:
            video_data: 原始搜索结果
            
        Returns:
            标准化的视频信息列表，每个元素包含：
            - id: 视频ID
            - title: 标题
            - url: 视频URL
            - duration: 时长（秒）
            - width: 宽度
            - height: 高度
            - thumbnail: 缩略图URL（可选）
        """
        raise NotImplementedError

    def search_and_extract(self, query: str, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        搜索并提取标准化的视频信息
        
        Args:
            query: 搜索关键词
            per_page: 每页结果数量
            
        Returns:
            标准化的视频信息列表
        """
        try:
            raw_data = self.search_videos(query, per_page)
            if raw_data:
                return self.extract_video_info(raw_data)
            return []
        except Exception as e:
            print(f"搜索视频时发生错误: {e}")
            return []

    def filter_videos_by_quality(self, videos: List[Dict[str, Any]], 
                                exact_match: bool = False) -> List[Dict[str, Any]]:
        """
        根据质量要求过滤视频
        
        Args:
            videos: 视频列表
            exact_match: 是否要求精确匹配尺寸
            
        Returns:
            过滤后的视频列表
        """
        filtered = []
        for video in videos:
            # 过滤时长
            duration = video.get('duration', 0)
            if duration < self.video_segment_min_length:
                continue
            if duration > self.video_segment_max_length:
                video['duration'] = self.video_segment_max_length
            
            # 过滤尺寸
            video_width = video.get('width', 0)
            video_height = video.get('height', 0)
            
            if exact_match:
                if video_width == self.width and video_height == self.height:
                    filtered.append(video)
            else:
                if video_width >= self.width and video_height >= self.height:
                    filtered.append(video)
                    
        return filtered

    def calculate_total_duration(self, videos: List[Dict[str, Any]]) -> float:
        """
        计算视频总时长，考虑转场效果
        
        Args:
            videos: 视频列表
            
        Returns:
            总时长（秒）
        """
        if not videos:
            return 0
            
        total_duration = 0
        for i, video in enumerate(videos):
            duration = video.get('duration', 0)
            if self.enable_video_transition_effect and i > 0:
                total_duration += duration - self.video_transition_effect_duration
            else:
                total_duration += duration
                
        return max(0, total_duration)