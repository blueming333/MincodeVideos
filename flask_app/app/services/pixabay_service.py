"""
Flask兼容的Pixabay视频搜索服务
基于原始PixabayService，移除streamlit依赖，适配Flask应用
"""

import requests
from typing import List, Dict, Any
from urllib.parse import quote_plus
from flask_app.app.services.base_resource_service import BaseResourceService
from config.config import my_config
from tools.utils import must_have_value


class FlaskPixabayService(BaseResourceService):
    """Flask兼容的Pixabay搜索服务"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.api_key = my_config['resource']['pixabay']['api_key']
            must_have_value(self.api_key, "请设置Pixabay API密钥")
        except (KeyError, TypeError):
            raise ValueError("请设置Pixabay API密钥")

    def search_videos(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """
        搜索Pixabay视频
        
        Args:
            query: 搜索关键词
            per_page: 每页结果数量
            
        Returns:
            Pixabay API原始响应数据
        """
        # 限制查询长度
        if len(query) > 100:
            query = query[:80]
        query = quote_plus(query)
        
        url = 'https://pixabay.com/api/videos/'
        params = {
            'key': self.api_key,
            'q': query,
            'min_width': self.width,
            'min_height': self.height,
            'per_page': per_page
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Pixabay API错误: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Pixabay搜索请求失败: {e}")
            return {}

    def extract_video_info(self, video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从Pixabay API响应中提取标准化视频信息
        
        Args:
            video_data: Pixabay API原始响应
            
        Returns:
            标准化的视频信息列表
        """
        videos = []
        
        if not video_data or 'hits' not in video_data:
            return videos
            
        for video in video_data['hits']:
            try:
                # 获取最适合的视频文件
                best_video_file = self._get_best_video_file(video.get('videos', {}))
                if not best_video_file:
                    continue
                    
                video_info = {
                    'id': str(video.get('id', '')),
                    'title': video.get('tags', f"Pixabay视频{video.get('id', '')}"),
                    'url': best_video_file['url'],
                    'duration': video.get('duration', 0),
                    'width': best_video_file.get('width', 0),
                    'height': best_video_file.get('height', 0),
                    'thumbnail': video.get('userImageURL', ''),
                    'source': 'pixabay'
                }
                videos.append(video_info)
                
            except Exception as e:
                print(f"解析Pixabay视频信息时出错: {e}")
                continue
                
        return videos

    def _get_best_video_file(self, video_files: Dict[str, Any]) -> Dict[str, Any]:
        """
        从Pixabay视频文件字典中选择最佳质量的文件
        
        Args:
            video_files: 视频文件字典 (size -> file_info)
            
        Returns:
            最佳视频文件信息，如果没有找到则返回空字典
        """
        if not video_files:
            return {}
            
        # Pixabay的视频尺寸优先级
        size_priority = ['large', 'medium', 'small', 'tiny']
        
        # 按优先级查找符合要求的视频
        for size in size_priority:
            if size in video_files:
                video_file = video_files[size]
                file_width = video_file.get('width', 0)
                file_height = video_file.get('height', 0)
                
                if file_width >= self.width and file_height >= self.height:
                    return video_file
                    
        # 如果没有找到符合要求的，返回最大可用的
        for size in size_priority:
            if size in video_files:
                return video_files[size]
                
        return {}

    def search_for_keyword(self, keyword: str, target_duration: float = 10, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        为特定关键词搜索视频资源
        
        Args:
            keyword: 搜索关键词
            target_duration: 目标时长（秒）
            per_page: 每页结果数量
            
        Returns:
            符合要求的视频资源列表，每个元素包含：
            - id: 视频ID
            - keyword: 关键词
            - title: 标题
            - url: 下载链接
            - duration: 实际使用时长
            - source: 资源来源 ('pixabay')
        """
        # 搜索视频
        videos = self.search_and_extract(keyword, per_page)
        
        # 过滤质量
        filtered_videos = self.filter_videos_by_quality(videos)
        
        # 转换为统一的资源格式
        resources = []
        cumulative_duration = 0
        
        for video in filtered_videos:
            if cumulative_duration >= target_duration:
                break
                
            # 计算这个视频应该使用的时长
            remaining_duration = target_duration - cumulative_duration
            video_duration = min(video['duration'], remaining_duration, self.video_segment_max_length)
            
            resource = {
                'id': f"pixabay_{video['id']}",
                'keyword': keyword,
                'title': video['title'],
                'url': video['url'],
                'duration': video_duration,
                'source': 'pixabay',
                'thumbnail': video.get('thumbnail', ''),
                'original_duration': video['duration']
            }
            
            resources.append(resource)
            cumulative_duration += video_duration
            
        return resources