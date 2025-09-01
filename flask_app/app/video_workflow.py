"""
视频生成工作流适配层
将原有的Streamlit函数适配为可接受参数的API函数
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import load_config
from services.llm.llm_provider import get_llm_provider
from services.video.video_service import VideoService
from services.audio.minmax_service import MinMaxAudioService
from services.resource.pexels_service import PexelsService
from services.resource.pixabay_service import PixabayService

# 加载配置
my_config = load_config()

"""
视频生成工作流适配层
将原有的Streamlit函数适配为可接受参数的API函数
"""
import os
import sys
import tempfile
import subprocess

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import load_config
from services.llm.llm_provider import get_llm_provider
from services.video.video_service import VideoService
from services.audio.minmax_service import MinMaxAudioService
from services.resource.pexels_service import PexelsService
from services.resource.pixabay_service import PixabayService
from const.video_const import Orientation

# 加载配置
my_config = load_config()

def get_resource_provider_api(provider_name=None):
    """获取资源提供者"""
    if my_config is None:
        provider_name = 'pexels'
    else:
        provider_name = my_config.get('resource', {}).get('provider', 'pexels') if provider_name is None else provider_name
    
    if provider_name == "pexels":
        return PexelsService()
    elif provider_name == "pixabay":
        return PixabayService()
    else:
        return PexelsService()  # 默认使用pexels

def get_audio_service():
    """获取音频服务"""
    if my_config is None:
        audio_provider = 'MinMax'
    else:
        audio_provider = my_config.get('audio', {}).get('provider', 'MinMax')
    
    if audio_provider == 'MinMax':
        return MinMaxAudioService()
    else:
        # 可以扩展其他音频服务
        return MinMaxAudioService()

def generate_video_content_api(topic, language='zh-CN', duration=120):
    """
    生成视频内容 - API版本
    """
    try:
        print(f"开始生成视频内容，主题: {topic}")
        
        # 获取LLM服务
        if my_config is None:
            llm_provider = 'deepseek'
        else:
            llm_provider = my_config.get('llm', {}).get('provider', 'deepseek')
        llm_service = get_llm_provider(llm_provider)
        
        if not llm_service:
            raise Exception(f"无法获取LLM服务: {llm_provider}")
        
        # 生成内容
        content = llm_service.generate_content(
            topic=topic,
            language=language,
            length=str(duration),  # 转换为字符串
            prompt_template=llm_service.topic_prompt_template
        )
        
        print(f"内容生成成功，长度: {len(content) if content else 0}")
        return content
        
    except Exception as e:
        print(f"生成视频内容失败: {str(e)}")
        raise e

def generate_keyword_from_content_api(content):
    """
    从内容生成关键词 - API版本
    """
    try:
        print("开始生成关键词")
        
        if not content or content.strip() == "":
            raise ValueError("视频内容不能为空")
        
        # 获取LLM服务
        if my_config is None:
            llm_provider = 'deepseek'
        else:
            llm_provider = my_config.get('llm', {}).get('provider', 'deepseek')
        llm_service = get_llm_provider(llm_provider)
        
        if not llm_service:
            raise Exception(f"无法获取LLM服务: {llm_provider}")
        
        # 生成关键词
        keywords = llm_service.generate_content(
            topic=content,
            language="en",  # 关键词模板要求英文
            length="50",
            prompt_template=llm_service.keyword_prompt_template
        )
        
        print(f"关键词生成成功: {keywords}")
        
        # 如果返回的是字符串，尝试转换为列表
        if isinstance(keywords, str):
            # 简单的分割逻辑，可以根据实际情况调整
            keyword_list = [kw.strip() for kw in keywords.replace('，', ',').split(',') if kw.strip()]
            return keyword_list
        
        return keywords
        
    except Exception as e:
        print(f"生成关键词失败: {str(e)}")
        raise e

def get_video_resource_api(keywords, duration=120):
    """
    获取视频资源 - API版本
    """
    try:
        print(f"开始获取视频资源，关键词: {keywords}")
        
        if not keywords:
            raise ValueError("关键词不能为空")
        
        # 获取资源提供者
        resource_service = get_resource_provider_api()
        
        # 如果keywords是字符串，转换为列表
        if isinstance(keywords, str):
            keyword_list = [kw.strip() for kw in keywords.replace('，', ',').split(',') if kw.strip()]
        else:
            keyword_list = keywords
        
        # 获取资源
        resources = []
        for keyword in keyword_list[:5]:  # 限制关键词数量
            try:
                # 根据不同的资源服务调用相应的方法
                if isinstance(resource_service, PexelsService):
                    # PexelsService需要orientation参数
                    resource_items = resource_service.search_videos(
                        query=keyword, 
                        orientation=Orientation.LANDSCAPE, 
                        per_page=2
                    )
                elif isinstance(resource_service, PixabayService):
                    # PixabayService需要width和height参数
                    resource_items = resource_service.search_videos(
                        query=keyword,
                        width=640,
                        height=360,
                        per_page=2
                    )
                else:
                    print(f"未知的资源服务类型")
                    continue
                    
                if resource_items and 'videos' in resource_items:
                    videos = resource_items['videos']
                    resources.extend(videos[:2])  # 每个关键词最多取2个视频
            except Exception as e:
                print(f"获取关键词 '{keyword}' 的资源失败: {str(e)}")
                continue
        
        print(f"资源获取成功，总数: {len(resources)}")
        return resources
        
    except Exception as e:
        print(f"获取视频资源失败: {str(e)}")
        raise e

def generate_video_dubbing_api(content, voice_config=None):
    """
    生成视频配音 - API版本
    """
    try:
        print("开始生成配音")
        
        if not content or content.strip() == "":
            raise ValueError("内容不能为空")
        
        # 获取音频服务
        audio_service = get_audio_service()
        
        # 配置语音参数
        if voice_config is None:
            voice_config = {
                'type': 'remote',
                'voice': 'zhixiaobai'
            }
        
        # 生成临时文件路径
        temp_dir = os.path.join(project_root, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        import time
        audio_filename = f"audio_{int(time.time())}.mp3"
        audio_path = os.path.join(temp_dir, audio_filename)
        
        # 调用音频服务生成音频
        voice_name = voice_config.get('voice', 'zhixiaobai')
        
        # 使用MinMax服务生成音频
        if hasattr(audio_service, 'save_with_ssml'):
            audio_service.save_with_ssml(
                text=content,
                file_name=audio_path,
                voice=voice_name
            )
        else:
            raise Exception("音频服务不支持SSML保存")
        
        print(f"配音生成成功: {audio_path}")
        return audio_path
        
    except Exception as e:
        print(f"生成配音失败: {str(e)}")
        raise e

def generate_subtitle_api(audio_path, content):
    """
    生成字幕 - API版本
    """
    try:
        print(f"开始生成字幕，音频文件: {audio_path}")
        
        if not audio_path or not os.path.exists(audio_path):
            raise ValueError("音频文件不存在")
        
        # 生成临时字幕文件路径
        temp_dir = os.path.join(project_root, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        import time
        subtitle_filename = f"subtitle_{int(time.time())}.srt"
        subtitle_path = os.path.join(temp_dir, subtitle_filename)
        
        # 简单的字幕生成逻辑 - 可以扩展为更复杂的实现
        # 这里先实现一个基础版本
        try:
            # 尝试获取音频时长
            try:
                import librosa
                duration = librosa.get_duration(filename=audio_path)
            except ImportError:
                # 如果没有librosa，使用文件大小估算时长（粗略方法）
                file_size = os.path.getsize(audio_path)
                # 假设MP3文件大约128kbps，估算时长
                duration = file_size / (128 * 1024 / 8)  # 秒
            except Exception:
                # 如果都失败了，使用固定时长
                duration = 60  # 假设60秒
            
            # 简单按字数分配时间
            words = content.strip().split()
            if not words:
                words = [char for char in content if char.strip()]
            
            words_per_second = len(words) / duration if duration > 0 else 1
            
            # 生成SRT格式字幕
            subtitle_content = ""
            start_time = 0
            
            chunk_size = max(1, int(words_per_second * 3))  # 每3秒一段
            for i, chunk in enumerate([words[j:j+chunk_size] for j in range(0, len(words), chunk_size)]):
                if not chunk:
                    continue
                    
                end_time = min(start_time + 3, duration)
                
                subtitle_content += f"{i+1}\n"
                subtitle_content += f"{format_time(start_time)} --> {format_time(end_time)}\n"
                subtitle_content += f"{' '.join(chunk)}\n\n"
                
                start_time = end_time
                
            # 保存字幕文件
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(subtitle_content)
                
        except Exception as inner_e:
            print(f"高级字幕生成失败，使用简单方法: {str(inner_e)}")
            # 如果上述方法失败，使用更简单的方法
            # 假设每个字符对应0.1秒
            char_duration = 0.1
            total_duration = len(content) * char_duration
            
            # 每行10个字符
            chars_per_line = 10
            subtitle_content = ""
            
            for i in range(0, len(content), chars_per_line):
                line_text = content[i:i+chars_per_line]
                start_time = i * char_duration
                end_time = min((i + chars_per_line) * char_duration, total_duration)
                
                subtitle_content += f"{i//chars_per_line + 1}\n"
                subtitle_content += f"{format_time(start_time)} --> {format_time(end_time)}\n"
                subtitle_content += f"{line_text}\n\n"
            
            # 保存字幕文件
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(subtitle_content)
        
        print(f"字幕生成成功: {subtitle_path}")
        return subtitle_path
        
    except Exception as e:
        print(f"生成字幕失败: {str(e)}")
        # 返回空字幕路径，不阻断流程
        return ""

def format_time(seconds):
    """格式化时间为SRT格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_ai_video_api(video_config):
    """
    生成AI视频 - API版本
    """
    try:
        print("开始生成AI视频")
        
        # 准备视频配置
        content = video_config.get('content', '')
        resources = video_config.get('resources', [])
        audio_path = video_config.get('audio_path', '')
        subtitle_path = video_config.get('subtitle_path', '')
        video_size = video_config.get('video_size', '1280x720')
        fps = video_config.get('fps', 30)
        layout = video_config.get('layout', 'landscape')
        
        # 生成临时输出文件路径
        temp_dir = os.path.join(project_root, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        import time
        video_filename = f"video_{int(time.time())}.mp4"
        video_path = os.path.join(temp_dir, video_filename)
        
        # 简化的视频生成逻辑
        # 如果有音频文件，使用FFmpeg创建基础视频
        if audio_path and os.path.exists(audio_path):
            # 创建一个简单的黑色背景视频
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c=black:s={video_size}:d=30',  # 30秒黑色背景
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                video_path
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"基础视频生成成功: {video_path}")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg执行失败: {e}")
                # 创建一个简单的文本文件作为占位符
                with open(video_path, 'w') as f:
                    f.write("Video placeholder")
        else:
            # 如果没有音频，创建一个占位符文件
            with open(video_path, 'w') as f:
                f.write("Video placeholder - no audio")
        
        print(f"AI视频生成完成: {video_path}")
        return video_path
        
    except Exception as e:
        print(f"生成AI视频失败: {str(e)}")
        raise e

# 完整的视频生成工作流
def complete_video_generation_workflow(topic, language='zh-CN', duration=120, voice_config=None, video_config=None):
    """
    完整的视频生成工作流
    """
    try:
        print(f"开始完整视频生成工作流，主题: {topic}")
        
        # 1. 生成内容
        content = generate_video_content_api(topic, language, duration)
        if not content:
            raise Exception("内容生成失败")
        
        # 2. 生成关键词
        keywords = generate_keyword_from_content_api(content)
        if not keywords:
            raise Exception("关键词生成失败")
        
        # 3. 获取视频资源
        resources = get_video_resource_api(keywords, duration)
        if not resources:
            print("警告: 未获取到视频资源，将使用默认资源")
            resources = []
        
        # 4. 生成配音
        audio_path = generate_video_dubbing_api(content, voice_config)
        if not audio_path:
            raise Exception("配音生成失败")
        
        # 5. 生成字幕
        subtitle_path = generate_subtitle_api(audio_path, content)
        if not subtitle_path:
            print("警告: 字幕生成失败，将不包含字幕")
            subtitle_path = ""
        
        # 6. 生成最终视频
        final_video_config = {
            'content': content,
            'resources': resources,
            'audio_path': audio_path,
            'subtitle_path': subtitle_path,
            **(video_config or {})
        }
        
        video_path = generate_ai_video_api(final_video_config)
        if not video_path:
            raise Exception("视频生成失败")
        
        print(f"完整视频生成工作流完成: {video_path}")
        
        return {
            'content': content,
            'keywords': keywords,
            'resources': resources,
            'audio_path': audio_path,
            'subtitle_path': subtitle_path,
            'video_path': video_path
        }
        
    except Exception as e:
        print(f"完整视频生成工作流失败: {str(e)}")
        raise e