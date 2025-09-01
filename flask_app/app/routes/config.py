"""
Configuration routes - 系统配置管理
"""
import sys
import os
import json
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for

# 添加原项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import yaml

# 使用新的配置管理器
try:
    from flask_app.app.utils.config_manager import config_manager, get_config, update_config, reload_config
    config_manager_available = True
except ImportError as e:
    print(f"Warning: Could not import config manager: {e}")
    config_manager_available = False

# 向后兼容的配置导入
try:
    from config.config import languages
    from config.config import local_audio_tts_providers, local_audio_recognition_providers
    original_config_available = True
except ImportError as e:
    print(f"Warning: Could not import config modules: {e}")
    original_config_available = False
    languages = {'zh-CN': '简体中文', 'en': 'English', 'ja': '日本語'}
    local_audio_tts_providers = ['chatTTS', 'GPTSoVITS', 'CosyVoice']
    local_audio_recognition_providers = ['fasterwhisper', 'sensevoice']

bp = Blueprint('config', __name__)

def load_config_file():
    """从YAML文件加载配置"""
    if config_manager_available:
        return config_manager.get_config()
    else:
        # 向后兼容的加载方式
        try:
            current_file = os.path.abspath(__file__)
            # 从 flask_app/app/routes 目录向上3级到达项目根目录 MincodeVideos
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            config_path = os.path.join(root_dir, 'config', 'config.yml')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    return loaded_config or get_default_config()
            else:
                return get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return get_default_config()

def get_default_config():
    """获取默认配置"""
    return {
        'ui': {'language': 'zh-CN'},
        'llm': {'provider': 'OpenAI'},
        'audio': {'provider': 'Azure'},
        'resource': {'provider': 'pexels'},
        'publisher': {'driver_type': 'chrome'}
    }

@bp.route('/')
def index():
    """配置首页 - 分类展示所有配置选项"""
    config = load_config_file()
    print(f"传递给模板的配置: {config}")
    return render_template('config/index.html', config=config, config_json=json.dumps(config))

@bp.route('/language')
def language():
    """语言设置"""
    config = load_config_file()
    return render_template('config/language.html', 
                         languages=languages, 
                         current_language=config.get('ui', {}).get('language', 'zh-CN'))

@bp.route('/llm')
def llm():
    """大语言模型配置"""
    config = load_config_file()
    return render_template('config/llm.html', config=config.get('llm', {}))

@bp.route('/audio')
def audio():
    """音频服务配置"""
    config = load_config_file()
    return render_template('config/audio.html', 
                         config=config.get('audio', {}),
                         local_tts_providers=local_audio_tts_providers,
                         local_recognition_providers=local_audio_recognition_providers)

@bp.route('/resource')
def resource():
    """资源服务配置"""
    config = load_config_file()
    return render_template('config/resource.html', config=config.get('resource', {}))

@bp.route('/publisher')
def publisher():
    """发布平台配置"""
    config = load_config_file()
    return render_template('config/publisher.html', config=config.get('publisher', {}))

@bp.route('/save', methods=['POST'])
def save():
    """保存配置"""
    try:
        data = request.get_json()
        
        # 如果是完整配置对象，直接保存
        if 'config' in data:
            new_config = data['config']
            if config_manager_available:
                config_manager.update_config(new_config)
                success = config_manager.save_config()
            else:
                # 向后兼容的保存方式
                success = save_config_legacy(new_config)
                
            if success:
                return jsonify({'success': True, 'message': '配置保存成功'})
            else:
                return jsonify({'success': False, 'message': '配置保存失败'})
        
        # 如果是单个配置项
        section = data.get('section')
        key = data.get('key')
        value = data.get('value')
        
        if section and key:
            if config_manager_available:
                # 使用配置管理器
                key_path = f"{section}.{key}" if key else section
                config_manager.set(key_path, value)
                success = config_manager.save_config()
            else:
                # 向后兼容方式
                config = load_config_file()
                if section not in config:
                    config[section] = {}
                
                keys = key.split('.')
                config_ref = config[section]
                for k in keys[:-1]:
                    if not isinstance(config_ref, dict):
                        config_ref = {}
                    if k not in config_ref:
                        config_ref[k] = {}
                    config_ref = config_ref[k]
                
                if isinstance(config_ref, dict):
                    config_ref[keys[-1]] = value
                
                success = save_config_legacy(config)
            
            if success:
                return jsonify({'success': True, 'message': '配置保存成功'})
            else:
                return jsonify({'success': False, 'message': '配置保存失败'})
        else:
            return jsonify({'success': False, 'message': '参数错误'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

def save_config_legacy(config_data):
    """向后兼容的配置保存方法"""
    try:
        current_file = os.path.abspath(__file__)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        config_path = os.path.join(root_dir, 'config', 'config.yml')
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        print(f"配置已保存到: {config_path}")
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False
@bp.route('/api/current')
def get_current_config():
    """获取当前配置"""
    try:
        config = load_config_file()
        return jsonify({'success': True, 'data': config})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取配置失败: {str(e)}'})

@bp.route('/api/reload', methods=['POST'])
def reload_config_api():
    """重新加载配置"""
    try:
        if config_manager_available:
            config_manager.reload_config()
            message = "配置已重新加载（使用配置管理器）"
        else:
            message = "配置已重新加载（使用传统方式）"
        
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'重新加载配置失败: {str(e)}'})

@bp.route('/api/audio_voices')
def get_audio_voices_api():
    """获取当前音频提供商的语音选项"""
    try:
        if config_manager_available:
            voices = config_manager.get_audio_voices()
            provider = config_manager.get_audio_provider()
        else:
            # 向后兼容方式
            from flask_app.app.routes.video import get_audio_voices
            voices = get_audio_voices()
            config = load_config_file()
            provider = config.get('audio', {}).get('provider', 'Unknown')
        
        return jsonify({
            'success': True, 
            'data': {
                'voices': voices,
                'provider': provider
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取语音选项失败: {str(e)}'})

@bp.route('/test/<provider>')

@bp.route('/test/<provider>')
def test_provider(provider):
    """测试服务提供商连接"""
    try:
        config = load_config_file()
        
        if provider not in config.get('llm', {}):
            return jsonify({'success': False, 'message': f'未找到 {provider} 的配置'})
        
        llm_config = config['llm'][provider]
        
        # 根据不同的提供商进行实际的API测试
        result = test_llm_connection(provider, llm_config)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'测试失败: {str(e)}'})

def test_llm_connection(provider, config):
    """实际测试LLM连接"""
    import requests
    import time
    
    try:
        if provider == 'OpenAI':
            return test_openai_connection(config)
        elif provider == 'DeepSeek':
            return test_deepseek_connection(config)
        elif provider == 'Moonshot':
            return test_moonshot_connection(config)
        elif provider == 'Azure':
            return test_azure_openai_connection(config)
        elif provider == 'Ollama':
            return test_ollama_connection(config)
        elif provider == 'Qianfan':
            return test_qianfan_connection(config)
        elif provider == 'Tongyi':
            return test_tongyi_connection(config)
        elif provider == 'Baichuan':
            return test_baichuan_connection(config)
        else:
            return {'success': False, 'message': f'不支持的提供商: {provider}'}
    except Exception as e:
        return {'success': False, 'message': f'连接测试失败: {str(e)}'}

def test_openai_connection(config):
    """测试OpenAI连接"""
    import requests
    
    api_key = config.get('api_key', '')
    if not api_key or api_key == 'YOUR_API_KEY':
        return {'success': False, 'message': '请先配置有效的API Key'}
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': config.get('model_name', 'gpt-3.5-turbo'),
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'max_tokens': 5
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'message': 'OpenAI连接测试成功！'}
        elif response.status_code == 401:
            return {'success': False, 'message': 'API Key无效或已过期'}
        elif response.status_code == 429:
            return {'success': False, 'message': 'API调用频率超限，请稍后再试'}
        else:
            return {'success': False, 'message': f'连接失败: HTTP {response.status_code}'}
    except requests.exceptions.Timeout:
        return {'success': False, 'message': '连接超时，请检查网络'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'网络错误: {str(e)}'}

def test_deepseek_connection(config):
    """测试DeepSeek连接"""
    import requests
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.deepseek.com/')
    
    if not api_key or api_key == 'YOUR_API_KEY':
        return {'success': False, 'message': '请先配置有效的API Key'}
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': config.get('model_name', 'deepseek-chat'),
        'messages': [{'role': 'user', 'content': '你好'}],
        'max_tokens': 5
    }
    
    try:
        url = base_url.rstrip('/') + '/v1/chat/completions'
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return {'success': True, 'message': 'DeepSeek连接测试成功！'}
        elif response.status_code == 401:
            return {'success': False, 'message': 'API Key无效或已过期'}
        elif response.status_code == 429:
            return {'success': False, 'message': 'API调用频率超限，请稍后再试'}
        else:
            return {'success': False, 'message': f'连接失败: HTTP {response.status_code} - {response.text[:200]}'}
    except requests.exceptions.Timeout:
        return {'success': False, 'message': '连接超时，请检查网络'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'网络错误: {str(e)}'}

def test_moonshot_connection(config):
    """测试Moonshot连接"""
    import requests
    
    api_key = config.get('api_key', '')
    if not api_key or api_key == 'YOUR_API_KEY':
        return {'success': False, 'message': '请先配置有效的API Key'}
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': config.get('model_name', 'moonshot-v1-8k'),
        'messages': [{'role': 'user', 'content': '你好'}],
        'max_tokens': 5
    }
    
    try:
        response = requests.post(
            'https://api.moonshot.cn/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'message': 'Moonshot连接测试成功！'}
        elif response.status_code == 401:
            return {'success': False, 'message': 'API Key无效或已过期'}
        else:
            return {'success': False, 'message': f'连接失败: HTTP {response.status_code}'}
    except requests.exceptions.Timeout:
        return {'success': False, 'message': '连接超时，请检查网络'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'网络错误: {str(e)}'}

def test_azure_openai_connection(config):
    """测试Azure OpenAI连接"""
    import requests
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', '')
    
    if not api_key or api_key == 'YOUR_API_KEY':
        return {'success': False, 'message': '请先配置有效的API Key'}
    
    if not base_url:
        return {'success': False, 'message': '请先配置Base URL'}
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Azure OpenAI需要特定的URL格式
    try:
        # 简单的健康检查
        response = requests.get(f"{base_url.rstrip('/')}/openai/deployments", headers=headers, timeout=10)
        
        if response.status_code == 200:
            return {'success': True, 'message': 'Azure OpenAI连接测试成功！'}
        elif response.status_code == 401:
            return {'success': False, 'message': 'API Key无效'}
        else:
            return {'success': False, 'message': f'连接失败: HTTP {response.status_code}'}
    except requests.exceptions.Timeout:
        return {'success': False, 'message': '连接超时，请检查网络'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'网络错误: {str(e)}'}

def test_ollama_connection(config):
    """测试Ollama连接"""
    import requests
    
    base_url = config.get('base_url', 'http://127.0.0.1:11434/')
    
    try:
        # 检查Ollama服务是否运行
        response = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                return {'success': True, 'message': f'Ollama连接成功，发现 {len(models)} 个模型'}
            else:
                return {'success': True, 'message': 'Ollama连接成功，但未发现任何模型'}
        else:
            return {'success': False, 'message': f'Ollama服务异常: HTTP {response.status_code}'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'message': 'Ollama服务未启动，请检查服务状态'}
    except requests.exceptions.Timeout:
        return {'success': False, 'message': '连接超时，请检查Ollama服务'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'网络错误: {str(e)}'}

def test_qianfan_connection(config):
    """测试百度千帆连接"""
    api_key = config.get('api_key', '')
    secret_key = config.get('secret_key', '')
    
    if not api_key or api_key == 'YOUR_API_KEY':
        return {'success': False, 'message': '请先配置API Key'}
    
    if not secret_key or secret_key == 'YOUR_SK_KEY':
        return {'success': False, 'message': '请先配置Secret Key'}
    
    # 千帆需要先获取access_token，这里简化为配置检查
    return {'success': True, 'message': '千帆配置检查通过，需要实际调用验证'}

def test_tongyi_connection(config):
    """测试通义千问连接"""
    api_key = config.get('api_key', '')
    
    if not api_key or api_key == 'YOUR_API_KEY':
        return {'success': False, 'message': '请先配置API Key'}
    
    # 通义千问API测试，这里简化为配置检查
    return {'success': True, 'message': '通义千问配置检查通过，需要实际调用验证'}

def test_baichuan_connection(config):
    """测试百川连接"""
    api_key = config.get('api_key', '')
    
    if not api_key or api_key == 'YOUR_API_KEY':
        return {'success': False, 'message': '请先配置API Key'}
    
    # 百川API测试，这里简化为配置检查  
    return {'success': True, 'message': '百川配置检查通过，需要实际调用验证'}