"""
Flask兼容的视频生成服务
将原本基于streamlit的视频生成流程适配为Flask应用
"""

import os
import tempfile
import requests
from typing import Dict, Any, List, Optional
from config.config import my_config
from tools.utils import random_with_system_time, extent_audio
from flask_app.app.utils.video_config_manager import video_config_manager, update_video_config
from flask_app.app.utils.streamlit_adapter import install_streamlit_adapter
import logging

logger = logging.getLogger(__name__)

# 安装streamlit适配器，确保在其他导入之前完成
install_streamlit_adapter()

# 在安装适配器后导入依赖streamlit的模块
from services.video.video_service import get_audio_duration, VideoService
from services.captioning.captioning_service import add_subtitles


class FlaskVideoGenerationService:
    """Flask兼容的视频生成服务"""
    
    def __init__(self, work_dir: Optional[str] = None):
        """
        初始化视频生成服务
        
        Args:
            work_dir: 工作目录，用于存储临时文件
        """
        self.work_dir = work_dir or tempfile.gettempdir()
        os.makedirs(self.work_dir, exist_ok=True)
        
    def generate_complete_video(self, 
                              content: str,
                              keywords: List[str], 
                              audio_file: str,
                              subtitle_file: Optional[str] = None,
                              video_resources: Optional[List[Dict[str, Any]]] = None,
                              enable_subtitles: bool = False,
                              subtitle_config: Optional[Dict[str, Any]] = None,
                              video_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成完整的视频
        
        Args:
            content: 视频文案内容
            keywords: 关键词列表
            audio_file: 音频文件路径
            subtitle_file: 字幕文件路径（可选）
            video_resources: 视频资源列表
            enable_subtitles: 是否启用字幕
            subtitle_config: 字幕配置
            video_config: 视频配置
            
        Returns:
            生成结果
        """
        # 首先设置视频配置，确保所有服务都能获取到正确的配置
        if video_config is None:
            video_config = {}
        self._setup_video_config(video_config)
        
        try:
            result = {
                'success': False,
                'video_file': None,
                'duration': 0,
                'steps_completed': [],
                'error': None
            }
            
            # 获取默认视频配置
            default_video_config = {
                'fps': 30,
                'size': '720x1280',  # 默认竖屏
                'layout': 'portrait',
                'segment_min_length': 5,
                'segment_max_length': 10,
                'enable_transition_effect': True,
                'transition_effect_type': 'xfade',
                'transition_effect_value': 'fade',
                'transition_effect_duration': '1'
            }
            
            # 合并用户配置
            if video_config:
                default_video_config.update(video_config)
            video_config = default_video_config
            
            # 步骤1: 准备视频资源
            logger.info("步骤1: 准备视频资源")
            if not video_resources:
                logger.error("没有提供视频资源")
                result['error'] = "没有提供视频资源"
                return result
                
            # 下载并准备视频文件列表
            video_files = self._prepare_video_files(video_resources)
            if not video_files:
                logger.error("无法准备视频文件")
                result['error'] = "无法准备视频文件"
                return result
                
            result['steps_completed'].append('prepare_video_files')
            
            # 步骤2: 验证音频文件
            logger.info("步骤2: 验证音频文件")
            if not os.path.exists(audio_file):
                logger.error(f"音频文件不存在: {audio_file}")
                result['error'] = f"音频文件不存在: {audio_file}"
                return result
                
            # 检查音频文件是否为空
            if os.path.getsize(audio_file) == 0:
                logger.error(f"音频文件为空: {audio_file}")
                result['error'] = f"音频文件为空: {audio_file}"
                return result
                
            # 扩展音频2秒，防止突然结束
            try:
                extent_audio(audio_file, 2)
            except Exception as e:
                logger.warning(f"音频扩展失败: {e}")
                
            audio_duration = get_audio_duration(audio_file)
            logger.info(f"音频时长: {audio_duration}秒")
            result['duration'] = audio_duration
            result['steps_completed'].append('validate_audio')
            
            # 步骤3: 创建视频服务并生成视频
            logger.info("步骤3: 视频合成")
            video_service = VideoService(video_files, audio_file)
            
            # 规范化视频
            logger.info("规范化视频片段")
            video_service.normalize_video()
            result['steps_completed'].append('normalize_video')
            
            # 生成带音频的视频
            logger.info("生成带音频的视频")
            video_file = video_service.generate_video_with_audio()
            if not video_file or not os.path.exists(video_file):
                logger.error("视频生成失败")
                result['error'] = "视频生成失败"
                return result
                
            result['video_file'] = video_file
            result['steps_completed'].append('generate_video_with_audio')
            
            # 步骤4: 添加字幕（如果需要）
            if enable_subtitles and subtitle_file and os.path.exists(subtitle_file):
                logger.info("步骤4: 添加字幕")
                try:
                    subtitle_config = subtitle_config or {}
                    add_subtitles(
                        video_file, 
                        subtitle_file,
                        font_name=subtitle_config.get('font_name', 'Arial'),
                        font_size=subtitle_config.get('font_size', 24),
                        primary_colour=subtitle_config.get('primary_colour', '&Hffffff'),
                        outline_colour=subtitle_config.get('outline_colour', '&H000000'),
                        outline=subtitle_config.get('outline', 2),
                        alignment=subtitle_config.get('alignment', 2)
                    )
                    result['steps_completed'].append('add_subtitles')
                    logger.info("字幕添加完成")
                except Exception as e:
                    logger.warning(f"添加字幕失败: {e}")
                    # 字幕添加失败不影响主要流程
            
            result['success'] = True
            logger.info(f"视频生成完成: {video_file}")
            return result
            
        except Exception as e:
            logger.error(f"视频生成过程中发生错误: {e}")
            result['error'] = str(e)
            return result
    
    def _setup_video_config(self, video_config: Dict[str, Any]):
        """
        设置视频生成配置，替代streamlit session_state
        
        Args:
            video_config: 视频配置参数
        """
        # 获取默认配置
        default_config = {
            'video_fps': 30,
            'video_size': '720x1280',
            'video_layout': 'portrait',
            'video_segment_min_length': 5,
            'video_segment_max_length': 10,
            'enable_video_transition_effect': True,
            'video_transition_effect_type': 'xfade',
            'video_transition_effect_value': 'fade',
            'video_transition_effect_duration': '1',
        }
        
        # 映射用户配置到内部配置键
        config_mapping = {
            'fps': 'video_fps',
            'size': 'video_size',
            'layout': 'video_layout',
            'segment_min_length': 'video_segment_min_length',
            'segment_max_length': 'video_segment_max_length',
            'enable_transition_effect': 'enable_video_transition_effect',
            'transition_effect_type': 'video_transition_effect_type',
            'transition_effect_value': 'video_transition_effect_value',
            'transition_effect_duration': 'video_transition_effect_duration',
        }
        
        # 应用用户配置
        for user_key, internal_key in config_mapping.items():
            if user_key in video_config:
                default_config[internal_key] = video_config[user_key]
        
        # 更新配置管理器
        update_video_config(default_config)
        
        logger.info(f"已设置视频配置，包含 {len(default_config)} 个配置项")
    
    def _prepare_video_files(self, video_resources: List[Dict[str, Any]]) -> List[str]:
        """
        准备视频文件，下载远程资源或验证本地文件
        
        Args:
            video_resources: 视频资源列表
            
        Returns:
            本地视频文件路径列表
        """
        video_files = []
        
        for resource in video_resources:
            try:
                # 如果是本地文件路径，直接验证
                url = resource.get('url', '')
                if url.startswith('file://') or not url.startswith('http'):
                    # 本地文件
                    local_path = url.replace('file://', '') if url.startswith('file://') else url
                    if os.path.exists(local_path):
                        video_files.append(local_path)
                        logger.info(f"使用本地视频文件: {local_path}")
                    else:
                        logger.warning(f"本地视频文件不存在: {local_path}")
                else:
                    # 远程文件，需要下载
                    local_path = self._download_video_resource(resource)
                    if local_path:
                        video_files.append(local_path)
                        
            except Exception as e:
                logger.error(f"处理视频资源时发生错误: {e}")
                continue
                
        return video_files
    
    def _download_video_resource(self, resource: Dict[str, Any]) -> Optional[str]:
        """
        下载视频资源到本地
        
        Args:
            resource: 视频资源信息
            
        Returns:
            本地文件路径，失败时返回None
        """
        try:
            import requests
            
            url = resource.get('url')
            if not url:
                return None
                
            # 生成本地文件名
            random_name = random_with_system_time()
            source = resource.get('source', 'unknown')
            video_id = resource.get('id', 'unknown')
            
            # 从URL中提取文件扩展名
            file_extension = '.mp4'  # 默认扩展名
            if '.' in url.split('/')[-1]:
                file_extension = '.' + url.split('.')[-1].split('?')[0]
                
            local_filename = f"{source}_{video_id}_{random_name}{file_extension}"
            local_path = os.path.join(self.work_dir, local_filename)
            
            # 下载文件
            logger.info(f"下载视频资源: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"视频下载完成: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"下载视频资源失败: {e}")
            return None
    
    def cleanup_temp_files(self, video_file: str, keep_final_video: bool = True):
        """
        清理临时文件
        
        Args:
            video_file: 最终视频文件路径
            keep_final_video: 是否保留最终视频文件
        """
        try:
            # 清理工作目录中的临时文件
            for file in os.listdir(self.work_dir):
                file_path = os.path.join(self.work_dir, file)
                if os.path.isfile(file_path):
                    if keep_final_video and file_path == video_file:
                        continue  # 保留最终视频文件
                    try:
                        os.remove(file_path)
                        logger.debug(f"删除临时文件: {file_path}")
                    except Exception as e:
                        logger.warning(f"删除临时文件失败: {e}")
                        
        except Exception as e:
            logger.warning(f"清理临时文件时发生错误: {e}")
            

def get_default_subtitle_config() -> Dict[str, Any]:
    """获取默认字幕配置"""
    return {
        'font_name': 'Arial',
        'font_size': 24,
        'primary_colour': '&Hffffff',  # 白色
        'outline_colour': '&H000000',  # 黑色边框
        'outline': 2,  # 边框宽度
        'alignment': 2  # 底部居中
    }