"""
视频生成API路由
集成原有main.py的视频生成工作流程
"""
from flask import Blueprint, request, jsonify, current_app
import os
import sys
import json
import traceback
from datetime import datetime

# 导入适配层函数
from ..video_workflow import (
    generate_video_content_api,
    generate_keyword_from_content_api,
    get_video_resource_api,
    generate_video_dubbing_api,
    generate_subtitle_api,
    generate_ai_video_api,
    complete_video_generation_workflow
)

video_api_bp = Blueprint('video_api', __name__, url_prefix='/video/api')

@video_api_bp.route('/generate_content', methods=['POST'])
def generate_content():
    """生成视频内容和关键词"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        language = data.get('language', 'zh-CN')
        duration = data.get('duration', 120)
        
        if not topic.strip():
            return jsonify({
                'success': False,
                'message': '主题不能为空'
            }), 400
        
        current_app.logger.info(f"开始生成内容，主题: {topic}")
        
        # 生成视频内容
        content = generate_video_content_api(topic, language, duration)
        if not content:
            return jsonify({
                'success': False,
                'message': '内容生成失败'
            }), 500
        
        # 生成关键词
        keywords = generate_keyword_from_content_api(content)
        if not keywords:
            return jsonify({
                'success': False,
                'message': '关键词生成失败'
            }), 500
        
        current_app.logger.info(f"内容生成成功，长度: {len(content)}, 关键词数量: {len(keywords) if isinstance(keywords, list) else 0}")
        
        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'keywords': keywords
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"生成内容失败: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'生成内容失败: {str(e)}'
        }), 500

@video_api_bp.route('/get_resources', methods=['POST'])
def get_resources():
    """获取视频资源"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        duration = data.get('duration', 120)
        
        if not keywords:
            return jsonify({
                'success': False,
                'message': '关键词不能为空'
            }), 400
        
        current_app.logger.info(f"开始获取视频资源，关键词: {keywords}")
        
        # 获取视频资源
        resources = get_video_resource_api(keywords, duration)
        if not resources:
            return jsonify({
                'success': False,
                'message': '获取视频资源失败'
            }), 500
        
        current_app.logger.info(f"资源获取成功，数量: {len(resources) if isinstance(resources, list) else 1}")
        
        return jsonify({
            'success': True,
            'data': {
                'resources': resources
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取资源失败: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'获取资源失败: {str(e)}'
        }), 500

@video_api_bp.route('/generate_dubbing', methods=['POST'])
def generate_dubbing():
    """生成视频配音"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        voice_config = data.get('voice_config', {})
        
        if not content.strip():
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400
        
        current_app.logger.info(f"开始生成配音，内容长度: {len(content)}")
        
        # 生成配音
        audio_path = generate_video_dubbing_api(content, voice_config)
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({
                'success': False,
                'message': '配音生成失败'
            }), 500
        
        current_app.logger.info(f"配音生成成功: {audio_path}")
        
        return jsonify({
            'success': True,
            'data': {
                'audio': {
                    'path': audio_path,
                    'url': f'/static/audio/{os.path.basename(audio_path)}'
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"生成配音失败: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'生成配音失败: {str(e)}'
        }), 500

@video_api_bp.route('/generate_subtitle', methods=['POST'])
def generate_subtitle():
    """生成视频字幕"""
    try:
        data = request.get_json()
        audio_path = data.get('audio_path', '')
        content = data.get('content', '')
        
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({
                'success': False,
                'message': '音频文件不存在'
            }), 400
        
        current_app.logger.info(f"开始生成字幕，音频: {audio_path}")
        
        # 生成字幕
        subtitle_path = generate_subtitle_api(audio_path, content)
        if not subtitle_path or not os.path.exists(subtitle_path):
            return jsonify({
                'success': False,
                'message': '字幕生成失败'
            }), 500
        
        current_app.logger.info(f"字幕生成成功: {subtitle_path}")
        
        return jsonify({
            'success': True,
            'data': {
                'subtitle': {
                    'path': subtitle_path,
                    'url': f'/static/subtitles/{os.path.basename(subtitle_path)}'
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"生成字幕失败: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'生成字幕失败: {str(e)}'
        }), 500

@video_api_bp.route('/generate_final_video', methods=['POST'])
def generate_final_video():
    """生成最终视频"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        resources = data.get('resources', [])
        audio = data.get('audio', {})
        subtitle = data.get('subtitle', {})
        config = data.get('config', {})
        
        current_app.logger.info("开始生成最终视频")
        
        # 准备参数
        video_config = {
            'content': content,
            'resources': resources,
            'audio_path': audio.get('path', ''),
            'subtitle_path': subtitle.get('path', ''),
            'video_size': config.get('video', {}).get('size', '1280x720'),
            'fps': int(config.get('video', {}).get('fps', 30)),
            'layout': config.get('video', {}).get('layout', 'landscape'),
            'language': config.get('language', 'zh-CN')
        }
        
        # 生成视频
        video_path = generate_ai_video_api(video_config)
        if not video_path or not os.path.exists(video_path):
            return jsonify({
                'success': False,
                'message': '视频生成失败'
            }), 500
        
        current_app.logger.info(f"视频生成成功: {video_path}")
        
        # 生成访问URL
        video_filename = os.path.basename(video_path)
        video_url = f'/static/videos/{video_filename}'
        
        return jsonify({
            'success': True,
            'data': {
                'video': {
                    'path': video_path,
                    'url': video_url,
                    'filename': video_filename,
                    'size': os.path.getsize(video_path) if os.path.exists(video_path) else 0
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"生成最终视频失败: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'生成最终视频失败: {str(e)}'
        }), 500

@video_api_bp.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态（用于长时间运行的任务）"""
    try:
        # 这里可以实现任务状态跟踪
        # 暂时返回简单状态
        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'status': 'completed',
                'progress': 100
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取任务状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取任务状态失败: {str(e)}'
        }), 500

@video_api_bp.route('/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    try:
        # 返回前端需要的配置
        frontend_config = {
            'languages': {
                'zh-CN': '中文',
                'en-US': 'English',
                'ja-JP': '日本語'
            },
            'audio_types': {
                'remote': '在线语音',
                'local': '本地上传'
            },
            'audio_voices': {
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
        }
        
        return jsonify({
            'success': True,
            'data': frontend_config
        })
        
    except Exception as e:
        current_app.logger.error(f"获取配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}'
        }), 500

@video_api_bp.errorhandler(Exception)
def handle_error(error):
    """全局错误处理"""
    current_app.logger.error(f"API错误: {str(error)}")
    current_app.logger.error(traceback.format_exc())
    
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500