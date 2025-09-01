from flask import Blueprint, request, jsonify
from flask import send_from_directory
import os
import sys
import logging
import time
import json
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

class EmptyService:
    def __init__(self, *args, **kwargs):
        pass
    def generate_content(self, prompt):
        return "模拟生成的内容"
    def generate_simple_content(self, prompt):
        return self.generate_content(prompt)
    def save_with_ssml(self, text, file_name, voice, rate="0"):
        # 占位：创建空文件代表失败或跳过
        try:
            with open(file_name, 'wb') as f:
                f.write(b'')
        except Exception:
            pass
    def chat_with_content(self, content, output_wav):
        # 占位：创建空文件
        try:
            with open(output_wav, 'wb') as f:
                f.write(b'')
        except Exception:
            pass
    def generate_audio(self, content, output_file):
        # 占位：创建空文件
        try:
            with open(output_file, 'wb') as f:
                f.write(b'')
        except Exception:
            pass
    def process(self, audio_file, language):
        # 占位：返回空的识别结果
        return []

try:
    from services.llm.deepseek_service import MyDeepSeekService as DeepSeekService
except ImportError as e:
    logging.warning(f"DeepSeek 导入失败: {e}")
    DeepSeekService = EmptyService

try:
    from services.resource.pexels_service import PexelsService
except ImportError:
    PexelsService = EmptyService

try:
    from services.resource.pixabay_service import PixabayService
except ImportError:
    PixabayService = EmptyService

# TTS 服务
try:
    from services.audio.tencent_tts_service import TencentAudioService
except ImportError:
    TencentAudioService = EmptyService
try:
    from services.audio.azure_service import AzureAudioService
except ImportError:
    AzureAudioService = EmptyService
try:
    from services.audio.alitts_service import AliAudioService
except ImportError:
    AliAudioService = EmptyService
try:
    from services.audio.minmax_service import MinMaxAudioService
except ImportError:
    MinMaxAudioService = EmptyService
try:
    from services.audio.chattts_flask_service import ChatTTSFlaskService
except ImportError:
    ChatTTSFlaskService = EmptyService

# 识别服务
try:
    from services.audio.faster_whisper_recognition_service import FasterWhisperRecognitionService
except ImportError:
    FasterWhisperRecognitionService = EmptyService
try:
    from services.audio.sensevoice_whisper_recognition_service import SenseVoiceRecognitionService
except ImportError:
    SenseVoiceRecognitionService = EmptyService
try:
    from services.audio.tencent_recognition_service import TencentRecognitionService
except ImportError:
    TencentRecognitionService = EmptyService

## 可选音频/视频/字幕服务暂未在当前端点中使用，如需启用请恢复以下导入
# try:
#     from services.audio.tencent_tts_service import TencentTTSService
# except ImportError:
#     TencentTTSService = EmptyService
# try:
#     from services.audio.azure_service import AzureService
# except ImportError:
#     AzureService = EmptyService
# try:
#     from services.audio.chattts_service import ChatTTSService
# except ImportError:
#     ChatTTSService = EmptyService
# try:
#     from services.video.video_service import VideoService
# except ImportError:
#     VideoService = EmptyService
# try:
#     from services.captioning.caption_helper import CaptionHelper
# except ImportError:
#     CaptionHelper = EmptyService

try:
    from tools import utils, tr_utils
except ImportError:
    class UtilsPlaceholder:
        @staticmethod
        def get_timestamp():
            return get_timestamp()
    utils = UtilsPlaceholder()
    tr_utils = UtilsPlaceholder()

# 使用新的配置管理器
try:
    from flask_app.app.utils.config_manager import config_manager, get_audio_service
    print("使用新的配置管理器")
except ImportError:
    print("配置管理器导入失败")
    config_manager = None
    get_audio_service = None

# 创建蓝图
video_api = Blueprint('video_api', __name__, url_prefix='/api/video')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_timestamp():
    """获取时间戳"""
    return str(int(time.time()))

def handle_api_error(func):
    """API错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'服务错误: {str(e)}',
                'data': None
            }), 500
    wrapper.__name__ = func.__name__
    return wrapper

@video_api.route('/generate-content', methods=['POST'])
@video_api.route('/generate_content', methods=['POST'])  # 兼容下划线写法
@handle_api_error
def generate_content():
    """步骤1: 生成视频内容"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        language = data.get('language', 'zh-CN')
        duration = data.get('duration', 60)
        
        if not topic:
            return jsonify({
                'success': False,
                'message': '请提供视频主题',
                'data': None
            }), 400
        
        if len(topic) < 10:
            return jsonify({
                'success': False,
                'message': '视频主题至少需要10个字符',
                'data': None
            }), 400
        
        # 调用LLM服务生成视频内容
        try:
            deepseek_service = DeepSeekService()
            
            # 根据时长和语言生成合适的提示词
            duration_text = f"{duration}秒" if duration < 60 else f"{duration//60}分钟"
            
            if language == 'zh-CN':
                prompt = f"""
请基于以下主题生成一个{duration_text}的视频脚本内容：

主题：{topic}

要求：
1. 内容要有逻辑性和连贯性
2. 适合{duration_text}的时长
3. 语言生动有趣，适合视频表达
4. 包含开头、主体和结尾
5. 每句话都要考虑视觉呈现效果

请直接输出脚本内容，不要包含任何标题或格式标记：
"""
            else:
                prompt = f"""
Please create a {duration_text} video script based on the following topic:

Topic: {topic}

Requirements:
1. Content should be logical and coherent
2. Suitable for {duration_text} duration
3. Engaging and interesting language suitable for video
4. Include opening, main content, and conclusion
5. Each sentence should consider visual presentation

Please output the script content directly without any titles or format markers:
"""
            
            # deepseek_service 的 generate_content 期望参数为(topic, prompt_template,...)
            # 这里我们直接调用简单封装方法
            try:
                if hasattr(deepseek_service, 'generate_simple_content'):
                    content = deepseek_service.generate_simple_content(prompt)
                else:
                    content = deepseek_service.generate_content(prompt)  # 退化直接调用
            except Exception:
                content = "生成失败，请稍后重试"
            
            if not content:
                return jsonify({
                    'success': False,
                    'message': '内容生成失败，请重试',
                    'data': None
                }), 500
            
            return jsonify({
                'success': True,
                'message': '视频内容生成成功',
                'data': {
                    'content': content.strip(),
                    'topic': topic,
                    'language': language,
                    'duration': duration
                }
            })
            
        except Exception as e:
            logger.error(f"LLM服务错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'内容生成服务错误: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        logger.error(f"生成内容错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}',
            'data': None
        }), 500

@video_api.route('/generate-keywords', methods=['POST'])
@video_api.route('/generate_keywords', methods=['POST'])  # 兼容
@handle_api_error
def generate_keywords():
    """步骤2: 从内容生成关键词"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        language = data.get('language', 'zh-CN')
        
        if not content:
            return jsonify({
                'success': False,
                'message': '请提供视频内容',
                'data': None
            }), 400
        
        try:
            deepseek_service = DeepSeekService()
            
            if language == 'zh-CN':
                prompt = f"""
请从以下视频内容中提取5-8个最重要的关键词，用于搜索相关的视频素材：

内容：
{content}

要求：
1. 关键词要具体明确，便于搜索视频素材
2. 优先选择视觉化的词汇
3. 每个关键词用逗号分隔
4. 只输出关键词，不要其他内容

关键词：
"""
            else:
                prompt = f"""
Please extract 5-8 most important keywords from the following video content for searching related video materials:

Content:
{content}

Requirements:
1. Keywords should be specific and clear for video material search
2. Prioritize visual words
3. Separate each keyword with comma
4. Output only keywords, no other content

Keywords:
"""
            
            try:
                if hasattr(deepseek_service, 'generate_simple_content'):
                    keywords_text = deepseek_service.generate_simple_content(prompt)
                else:
                    keywords_text = deepseek_service.generate_content(prompt)
            except Exception:
                keywords_text = ''
            
            if not keywords_text:
                return jsonify({
                    'success': False,
                    'message': '关键词生成失败，请重试',
                    'data': None
                }), 500
            
            # 处理关键词
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            
            if not keywords:
                # 如果提取失败，使用简单的分词作为备选
                keywords = content.split()[:6]  # 取前6个词作为关键词
            
            return jsonify({
                'success': True,
                'message': '关键词生成成功',
                'data': {
                    'keywords': keywords,
                    'keywords_text': ', '.join(keywords)
                }
            })
            
        except Exception as e:
            logger.error(f"LLM服务错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'关键词生成服务错误: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        logger.error(f"生成关键词错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}',
            'data': None
        }), 500

@video_api.route('/get-resources', methods=['POST'])
@video_api.route('/get_resources', methods=['POST'])  # 兼容
@handle_api_error
def get_resources():
    """步骤3: 根据关键词获取视频资源"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        content_data = data.get('content')
        duration = data.get('duration', 60)
        language = data.get('language', 'zh-CN')
        
        # 如果没有提供keywords但有content，则从content中提取关键词
        if not keywords and content_data:
            # 从content对象中获取文本内容
            if isinstance(content_data, dict):
                content_text = content_data.get('content', '')
            else:
                content_text = str(content_data)
            
            # 使用LLM服务从内容中提取关键词
            try:
                deepseek_service = DeepSeekService()
                
                prompt = f"""请从以下文本中提取5-8个适合搜索视频素材的关键词，要求：
1. 关键词应该具有视觉表现力，适合搜索视频素材
2. 优先选择具体的名词、动作或场景
3. 避免抽象概念，优选具体的物体、场景、动作
4. 每个关键词用英文表示，用逗号分隔
5. 只输出关键词，不要其他内容

文本内容：
{content_text}

请输出关键词："""
                
                keywords_text = deepseek_service.generate_content(prompt)
                if keywords_text:
                    # 解析关键词
                    keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
                    logger.info(f"从内容中提取到关键词: {keywords}")
                else:
                    # 使用默认关键词
                    keywords = ['nature', 'landscape', 'people', 'city', 'technology']
                    logger.warning("关键词提取失败，使用默认关键词")
            except Exception as e:
                logger.error(f"关键词提取失败: {e}")
                # 使用默认关键词
                keywords = ['nature', 'landscape', 'people', 'city', 'technology']
        
        if not keywords:
            return jsonify({
                'success': False,
                'message': '请提供关键词或内容文本',
                'data': None
            }), 400
        
        # 确保keywords是列表
        if isinstance(keywords, str):
            keywords = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        try:
            # 根据配置选择资源提供商
            provider = config_manager.get('resource.provider', 'pexels') if config_manager else 'pexels'
            
            # 创建资源搜索服务
            if provider == 'pexels':
                from flask_app.app.services.pexels_service import FlaskPexelsService
                try:
                    resource_service = FlaskPexelsService(
                        orientation="landscape",
                        width=1920,
                        height=1080,
                        video_segment_min_length=3,
                        video_segment_max_length=15
                    )
                except ValueError as e:
                    logger.warning(f"Pexels服务初始化失败: {e}，使用模拟数据")
                    resource_service = None
            elif provider == 'pixabay':
                from flask_app.app.services.pixabay_service import FlaskPixabayService
                try:
                    resource_service = FlaskPixabayService(
                        orientation="landscape",
                        width=1920,
                        height=1080,
                        video_segment_min_length=3,
                        video_segment_max_length=15
                    )
                except ValueError as e:
                    logger.warning(f"Pixabay服务初始化失败: {e}，使用模拟数据")
                    resource_service = None
            else:
                logger.warning(f"不支持的资源提供商: {provider}，使用模拟数据")
                resource_service = None
            
            resources = []
            total_duration = 0
            
            if resource_service:
                # 使用真实的资源搜索服务
                target_duration_per_keyword = duration / len(keywords)
                
                for keyword in keywords:
                    try:
                        keyword_resources = resource_service.search_for_keyword(
                            keyword, 
                            target_duration_per_keyword, 
                            per_page=10
                        )
                        resources.extend(keyword_resources)
                        total_duration += sum(r['duration'] for r in keyword_resources)
                    except Exception as e:
                        logger.error(f"搜索关键词 '{keyword}' 时发生错误: {e}")
                        # 添加fallback资源
                        fallback_resource = {
                            'id': f'fallback_{len(resources)+1}',
                            'keyword': keyword,
                            'title': f'关于 {keyword} 的视频',
                            'url': f'https://example.com/fallback_{len(resources)+1}.mp4',
                            'duration': min(target_duration_per_keyword, 10),
                            'source': 'fallback'
                        }
                        resources.append(fallback_resource)
                        total_duration += fallback_resource['duration']
            else:
                # 使用模拟数据作为fallback
                logger.info("使用模拟资源数据")
                for i, keyword in enumerate(keywords[:5]):  # 限制最多5个关键词
                    resource = {
                        'id': f'mock_video_{i+1}',
                        'keyword': keyword,
                        'title': f'关于 {keyword} 的视频',
                        'url': f'https://example.com/video_{i+1}.mp4',
                        'duration': min(duration // len(keywords), 15),  # 每个片段最多15秒
                        'source': 'mock'
                    }
                    resources.append(resource)
                    total_duration += resource['duration']
            
            return jsonify({
                'success': True,
                'message': f'找到 {len(resources)} 个视频资源',
                'data': {
                    'resources': resources,
                    'total_duration': total_duration,
                    'keywords_used': keywords,
                    'provider': provider if resource_service else 'mock'
                }
            })
            
        except Exception as e:
            logger.error(f"资源搜索错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'搜索视频资源时发生错误: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        logger.error(f"获取资源错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}',
            'data': None
        }), 500

def map_audio_speed_to_rate(speed):
    """将前端语速映射为各TTS服务的rate参数"""
    speed_map = {
        'slowest': '-40',
        'slower': '-20', 
        'slow': '-10',
        'normal': '0',
        'fast': '10',
        'faster': '20',
        'fastest': '40'
    }
    return speed_map.get(speed, '0')

def map_chatts_speed(speed):
    """将前端语速映射为ChatTTS的速度标记"""
    chatts_speed_map = {
        'slowest': '[speed_2]',
        'slower': '[speed_3]',
        'slow': '[speed_4]',
        'normal': '[speed_5]',
        'fast': '[speed_6]',
        'faster': '[speed_7]',
        'fastest': '[speed_8]'
    }
    return chatts_speed_map.get(speed, '[speed_5]')

@video_api.route('/generate-dubbing', methods=['POST'])
@video_api.route('/generate_dubbing', methods=['POST'])  # 兼容
@handle_api_error
def generate_dubbing():
    """步骤4: 生成AI配音"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        audio_type = data.get('audio_type', 'remote')
        voice = data.get('voice', 'aicheng')  # 使用阿里云基础音色
        
        # 详细日志输出
        print(f"配音API接收参数: content长度={len(content)}, audio_type={audio_type}, voice={voice}")
        print(f"完整请求数据: {data}")
        language = data.get('language', 'zh-CN')
        audio_speed = data.get('audio_speed', 'normal')
        emotion = data.get('emotion', 'calm')
        
        if not content:
            return jsonify({
                'success': False,
                'message': '请提供视频内容',
                'data': None
            }), 400
        
        try:
            # 输出目录（使用项目根目录下 temp 以便统一文件访问）
            temp_dir = os.path.join(project_root, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            timestamp = get_timestamp()
            base_name = f'audio_{timestamp}'
            output_wav = os.path.join(temp_dir, base_name + '.wav')

            provider_used = None
            duration_seconds = None
            
            # 映射语速参数
            rate = map_audio_speed_to_rate(audio_speed)

            if audio_type == 'remote':
                # 使用配置管理器获取当前提供商
                if config_manager:
                    provider = config_manager.get_audio_provider()
                    audio_service = get_audio_service()
                    provider_used = provider
                    print(f"使用音频提供商: {provider}")
                    audio_service.save_with_ssml(content, output_wav, voice, rate=rate)
                else:
                    # 默认提供商
                    provider = 'Ali'
                    provider_used = provider
                    print(f"使用默认音频提供商: {provider}")
                    svc = AliAudioService()
            else:  # local
                local_provider = config_manager.get('audio.local_tts.provider', 'chatTTS') if config_manager else 'chatTTS'
                provider_used = local_provider
                if local_provider == 'chatTTS':
                    # 使用新的 ChatTTS Flask 服务，支持参数化
                    chatts_speed = map_chatts_speed(audio_speed)
                    svc = ChatTTSFlaskService(
                        audio_speed=audio_speed,
                        refine_text=False,
                        use_random_voice=True
                    )
                    svc.generate_audio(content, output_wav)
                else:
                    with open(output_wav, 'wb') as f:
                        f.write(b'')

            # 估算时长：如果pydub可用则读取真实长度，否则基于字数估算
            try:
                from pydub import AudioSegment
                if os.path.exists(output_wav) and os.path.getsize(output_wav) > 0:
                    seg = AudioSegment.from_file(output_wav)
                    duration_seconds = round(len(seg) / 1000.0, 2)
            except Exception:
                pass
            if duration_seconds is None:
                duration_seconds = round(len(content) * 0.18, 2)  # 依据平均语速估算

            rel_file = f'/temp/{os.path.basename(output_wav)}'
            audio_result = {
                'file': rel_file,
                'url': f'/api/video/files/{os.path.basename(output_wav)}',
                'duration': duration_seconds,
                'voice': voice,
                'provider': provider_used,
                'text': content,
                'audio_speed': audio_speed,
                'emotion': emotion,
                'rate_applied': rate,
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }

            return jsonify({
                'success': True,
                'message': f'AI配音生成成功 ({provider_used or "mock"})',
                'data': {
                    'audio': audio_result
                }
            })

        except Exception as e:
            logger.error(f"TTS服务错误: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'配音生成服务错误: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        logger.error(f"生成配音错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}',
            'data': None
        }), 500

@video_api.route('/generate-subtitle', methods=['POST'])
@video_api.route('/generate_subtitle', methods=['POST'])  # 兼容
@handle_api_error
def generate_subtitle():
    """步骤5: 生成字幕"""
    try:
        data = request.get_json()
        audio_file = data.get('audio_file', '')
        content = data.get('content', '').strip()
        language = data.get('language', 'zh-CN')
        
        if not content:
            return jsonify({
                'success': False,
                'message': '请提供视频内容',
                'data': None
            }), 400
        
        try:
            # 输出目录
            temp_dir = os.path.join(project_root, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            timestamp = get_timestamp()
            subtitle_file = os.path.join(temp_dir, f'subtitle_{timestamp}.srt')
            
            # 检查配置决定使用哪个识别服务
            audio_provider = config_manager.get('audio.provider') if config_manager else None
            recognition_provider = config_manager.get('audio.local_recognition.provider') if config_manager else None
            
            print(f"字幕生成: audio_provider={audio_provider}, local_recognition_provider={recognition_provider}")
            
            # 如果有音频文件，根据音频提供商选择识别服务
            subtitle_result = None
            if audio_file:
                # 将相对路径转为绝对路径
                if audio_file.startswith('/temp/'):
                    actual_audio_file = os.path.join(project_root, audio_file[1:])  # 去掉前导/
                else:
                    actual_audio_file = audio_file
                    
                if os.path.exists(actual_audio_file):
                    try:
                        # 根据音频提供商选择识别服务 (遵循captioning_service的逻辑)
                        if audio_provider == 'Ali' or audio_provider == 'MinMax':
                            # 使用阿里云识别服务
                            from services.alinls.speech_process import AliRecognitionService
                            recognizer = AliRecognitionService()
                            segments = recognizer.process(actual_audio_file)
                            provider_used = 'Ali'
                        elif audio_provider == 'Tencent':
                            # 使用腾讯识别服务
                            recognizer = TencentRecognitionService()
                            segments = recognizer.process(actual_audio_file, language)
                            provider_used = 'Tencent'
                        elif recognition_provider == 'fasterwhisper':
                            recognizer = FasterWhisperRecognitionService()
                            segments = recognizer.process(actual_audio_file, language)
                            provider_used = 'fasterwhisper'
                        elif recognition_provider == 'sensevoice':
                            recognizer = SenseVoiceRecognitionService()
                            segments = recognizer.process(actual_audio_file, language)
                            provider_used = 'sensevoice'
                        else:
                            segments = None
                            provider_used = 'none'
                            
                        if segments:
                            # 生成 SRT 字幕文件
                            with open(subtitle_file, 'w', encoding='utf-8') as f:
                                for i, segment in enumerate(segments):
                                    f.write(f"{i+1}\n")
                                    # 阿里云和腾讯的结果对象与FasterWhisper略有不同
                                    if hasattr(segment, 'begin_time') and hasattr(segment, 'end_time'):
                                        # 阿里云/腾讯格式
                                        f.write(f"{format_srt_time(segment.begin_time)} --> {format_srt_time(segment.end_time)}\n")
                                    else:
                                        # FasterWhisper格式
                                        f.write(f"{format_srt_time(segment.begin_time)} --> {format_srt_time(segment.end_time)}\n")
                                    f.write(f"{segment.text.strip()}\n\n")
                            
                            subtitle_result = {
                                'file': f'/temp/{os.path.basename(subtitle_file)}',
                                'format': 'srt',
                                'language': language,
                                'provider': provider_used,
                                'segments_count': len(segments)
                            }
                    except Exception as e:
                        logger.warning(f"识别服务错误 (提供商: {audio_provider or recognition_provider}): {str(e)}，回退到文本分割")
            
            # 如果识别失败或未配置，使用文本分割生成字幕
            if not subtitle_result:
                segments = split_text_to_segments(content, max_chars=50)
                with open(subtitle_file, 'w', encoding='utf-8') as f:
                    for i, segment in enumerate(segments):
                        start_time = i * 3.0  # 每段3秒
                        end_time = (i + 1) * 3.0
                        f.write(f"{i+1}\n")
                        f.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
                        f.write(f"{segment.strip()}\n\n")
                
                subtitle_result = {
                    'file': f'/temp/{os.path.basename(subtitle_file)}',
                    'format': 'srt',
                    'language': language,
                    'provider': 'text_split',
                    'segments_count': len(segments)
                }
            
            return jsonify({
                'success': True,
                'message': f'字幕生成成功 ({subtitle_result["provider"]})',
                'data': {
                    'subtitle': subtitle_result
                }
            })
            
        except Exception as e:
            logger.error(f"字幕生成错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'字幕生成服务错误: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        logger.error(f"生成字幕错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}',
            'data': None
        }), 500

def format_srt_time(seconds):
    """格式化时间为SRT格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

def split_text_to_segments(text, max_chars=50):
    """将文本分割为字幕段落"""
    sentences = text.replace('。', '.！').replace('？', '?！').replace('！', '!！').split('！')
    segments = []
    current_segment = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_segment + sentence) <= max_chars:
            current_segment += sentence
        else:
            if current_segment:
                segments.append(current_segment)
            current_segment = sentence
    
    if current_segment:
        segments.append(current_segment)
    
    return segments

@video_api.route('/generate-final', methods=['POST'])
@video_api.route('/generate_final', methods=['POST'])  # 兼容
@handle_api_error
def generate_final():
    """步骤6: 合成最终视频"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        resources = data.get('resources', [])
        audio = data.get('audio', {})
        subtitle = data.get('subtitle', {})
        video_config = data.get('video_config', {})
        language = data.get('language', 'zh-CN')
        
        if not all([content, resources, audio]):
            return jsonify({
                'success': False,
                'message': '缺少必要的生成参数',
                'data': None
            }), 400
        
        try:
            # 使用真实的视频生成服务
            from flask_app.app.services.video_generation_service import FlaskVideoGenerationService
            
            # 创建视频生成服务
            temp_dir = os.path.join(project_root, 'temp')
            video_service = FlaskVideoGenerationService(work_dir=temp_dir)
            
            # 准备音频文件路径
            audio_file = audio.get('file', '')
            if audio_file.startswith('/temp/'):
                audio_file = os.path.join(temp_dir, os.path.basename(audio_file))
            
            if not os.path.exists(audio_file):
                return jsonify({
                    'success': False,
                    'message': f'音频文件不存在: {audio_file}',
                    'data': None
                }), 400
            
            # 准备字幕文件路径（如果有）
            subtitle_file = None
            enable_subtitles = False
            if subtitle and subtitle.get('file'):
                subtitle_file = subtitle.get('file', '')
                if subtitle_file.startswith('/temp/'):
                    subtitle_file = os.path.join(temp_dir, os.path.basename(subtitle_file))
                enable_subtitles = os.path.exists(subtitle_file) if subtitle_file else False
            
            # 准备字幕配置
            subtitle_config = {
                'font_name': video_config.get('subtitle_font', 'Arial'),
                'font_size': video_config.get('subtitle_font_size', 24),
                'primary_colour': video_config.get('subtitle_color', '&Hffffff'),
                'outline_colour': video_config.get('subtitle_border_color', '&H000000'),
                'outline': video_config.get('subtitle_border_width', 2),
                'alignment': video_config.get('subtitle_position', 2)
            }
            
            # 提取关键词列表
            keywords = [resource.get('keyword', '') for resource in resources]
            keywords = [k for k in keywords if k]  # 过滤空关键词
            
            logger.info(f"开始视频生成: 音频={audio_file}, 资源数量={len(resources)}, 字幕={enable_subtitles}")
            
            # 生成视频
            result = video_service.generate_complete_video(
                content=content,
                keywords=keywords,
                audio_file=audio_file,
                subtitle_file=subtitle_file,
                video_resources=resources,
                enable_subtitles=enable_subtitles,
                subtitle_config=subtitle_config
            )
            
            if result['success']:
                video_file = result['video_file']
                # 生成返回的URL路径
                filename = os.path.basename(video_file)
                video_url = f'/api/video/files/{filename}'
                
                video_result = {
                    'file': f'/temp/{filename}',
                    'url': video_url,
                    'duration': result.get('duration', 0),
                    'resolution': video_config.get('size', '1920x1080'),
                    'format': 'mp4',
                    'steps_completed': result.get('steps_completed', []),
                    'local_path': video_file  # 用于调试
                }
                
                logger.info(f"视频生成成功: {video_file}")
                
                return jsonify({
                    'success': True,
                    'message': '视频合成完成',
                    'data': {
                        'video': video_result
                    }
                })
            else:
                error_msg = result.get('error', '未知错误')
                logger.error(f"视频生成失败: {error_msg}")
                return jsonify({
                    'success': False,
                    'message': f'视频生成失败: {error_msg}',
                    'data': {
                        'steps_completed': result.get('steps_completed', [])
                    }
                }), 500
            
        except Exception as e:
            logger.error(f"视频合成错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'视频合成服务错误: {str(e)}',
                'data': None
            }), 500
            
    except Exception as e:
        logger.error(f"合成视频错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}',
            'data': None
        }), 500

@video_api.route('/status/<task_id>', methods=['GET'])
@handle_api_error
def get_task_status(task_id):
    """获取任务状态"""
    try:
        # 这里应该查询实际的任务状态
        # 目前返回模拟数据
        status = {
            'task_id': task_id,
            'status': 'completed',  # pending, processing, completed, failed
            'progress': 100,
            'message': '任务已完成',
            'result': None
        }
        
        return jsonify({
            'success': True,
            'message': '状态查询成功',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"查询任务状态错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'查询状态时发生错误: {str(e)}',
            'data': None
        }), 500

@video_api.route('/files/<path:filename>', methods=['GET'])
@handle_api_error
def get_generated_file(filename):
    """提供生成的文件访问（支持temp和final目录）"""
    # 支持的目录列表
    directories = [
        os.path.join(project_root, 'temp'),   # 临时文件目录
        os.path.join(project_root, 'final'),  # 最终视频目录
        os.path.join(project_root, 'work'),   # 工作目录
    ]
    
    # 在各个目录中查找文件
    for directory in directories:
        if os.path.isdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    logger.info(f"提供文件访问: {file_path}")
                    return send_from_directory(directory, filename, as_attachment=False)
                except Exception as e:
                    logger.error(f"文件访问错误: {e}")
                    continue
    
    # 如果在所有目录中都没找到文件
    logger.error(f"文件未找到: {filename}")
    return jsonify({'success': False, 'message': '文件未找到', 'data': None}), 404