"""
Flask兼容的Pexels视频搜索服务
基于原始PexelsService，移除streamlit依赖，适配Flask应用
"""

import requests
from typing import List, Dict, Any
from flask_app.app.services.base_resource_service import BaseResourceService
from config.config import my_config
from tools.utils import must_have_value


class FlaskPexelsService(BaseResourceService):
    """Flask兼容的Pexels搜索服务"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.api_key = my_config['resource']['pexels']['api_key']
            must_have_value(self.api_key, "请设置Pexels API密钥")
        except (KeyError, TypeError):
            raise ValueError("请设置Pexels API密钥")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
            'Authorization': self.api_key
        }

    def search_videos(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """
        搜索Pexels视频
        
        Args:
            query: 搜索关键词
            per_page: 每页结果数量
            
        Returns:
            Pexels API原始响应数据
        """
        url = f'https://api.pexels.com/videos/search'
        params = {
            'query': query,
            'orientation': self.orientation.value,
            'per_page': per_page
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Pexels API错误: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Pexels搜索请求失败: {e}")
            return {}

    def extract_video_info(self, video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从Pexels API响应中提取标准化视频信息
        
        Args:
            video_data: Pexels API原始响应
            
        Returns:
            标准化的视频信息列表
        """
        videos = []
        
        if not video_data or 'videos' not in video_data:
            return videos
            
        for video in video_data['videos']:
            try:
                # 获取最适合的视频文件
                best_video_file = self._get_best_video_file(video.get('video_files', []))
                if not best_video_file:
                    continue
                    
                video_info = {
                    'id': str(video.get('id', '')),
                    'title': video.get('user', {}).get('name', f"Pexels视频{video.get('id', '')}"),
                    'url': best_video_file['link'],
                    'duration': video.get('duration', 0),
                    'width': best_video_file.get('width', 0),
                    'height': best_video_file.get('height', 0),
                    'thumbnail': video.get('image', ''),
                    'source': 'pexels'
                }
                videos.append(video_info)
                
            except Exception as e:
                print(f"解析Pexels视频信息时出错: {e}")
                continue
                
        return videos

    def _get_best_video_file(self, video_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        从视频文件列表中选择最佳质量的文件
        
        Args:
            video_files: 视频文件列表
            
        Returns:
            最佳视频文件信息，如果没有找到则返回空字典
        """
        if not video_files:
            return {}
            
        # 按分辨率排序，优先选择高分辨率
        sorted_files = sorted(
            video_files, 
            key=lambda x: (x.get('width', 0) * x.get('height', 0)), 
            reverse=True
        )
        
        # 首先尝试找到符合尺寸要求的文件
        for video_file in sorted_files:
            file_width = video_file.get('width', 0)
            file_height = video_file.get('height', 0)
            
            if file_width >= self.width and file_height >= self.height:
                return video_file
                
        # 如果没有找到符合要求的，返回最高分辨率的
        return sorted_files[0] if sorted_files else {}

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
            - source: 资源来源 ('pexels')
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
                'id': f"pexels_{video['id']}",
                'keyword': keyword,
                'title': video['title'],
                'url': video['url'],
                'duration': video_duration,
                'source': 'pexels',
                'thumbnail': video.get('thumbnail', ''),
                'original_duration': video['duration']
            }
            
            resources.append(resource)
            cumulative_duration += video_duration
            
        return resources