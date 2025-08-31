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

try:
    from config.config import my_config, save_config, languages
    from config.config import local_audio_tts_providers, local_audio_recognition_providers
    original_config_available = True
except ImportError as e:
    print(f"Warning: Could not import config modules: {e}")
    original_config_available = False

# 如果原有配置模块不可用，提供默认配置
if not original_config_available:
    # 提供默认值
    my_config = {
        'ui': {'language': 'zh-CN'},
        'llm': {'provider': 'OpenAI'},
        'audio': {'provider': 'Azure'},
        'resource': {'provider': 'pexels'},
        'publisher': {'driver_type': 'chrome'}
    }
    languages = {'zh-CN': '简体中文', 'en': 'English', 'ja': '日本語'}
    local_audio_tts_providers = ['chatTTS', 'GPTSoVITS', 'CosyVoice']
    local_audio_recognition_providers = ['fasterwhisper', 'sensevoice']
    
    def save_config():
        # 正确计算配置文件路径  
        current_file = os.path.abspath(__file__)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        config_path = os.path.join(root_dir, 'config', 'config.yml')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(my_config, f, default_flow_style=False, allow_unicode=True)
            print(f"配置已保存到: {config_path}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def test_config(*args):
        return True

bp = Blueprint('config', __name__)

def load_config_file():
    """从YAML文件加载配置"""
    global my_config
    try:
        # 正确计算配置文件路径
        current_file = os.path.abspath(__file__)
        print(f"当前文件路径: {current_file}")
        
        # 从flask_app/app/routes/config.py 回到根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        config_path = os.path.join(root_dir, 'config', 'config.yml')
        print(f"配置文件路径: {config_path}")
        print(f"配置文件是否存在: {os.path.exists(config_path)}")
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config is not None:
                    my_config = loaded_config
                    print(f"成功加载配置，包含 {len(loaded_config)} 个主要配置项")
                    print(f"配置项: {list(loaded_config.keys())}")
                else:
                    print("配置文件为空，使用默认配置")
                    my_config = get_default_config()
        else:
            print("配置文件不存在，使用默认配置")
            my_config = get_default_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        my_config = get_default_config()
    return my_config

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
            global my_config
            my_config = data['config']
            save_config()
            return jsonify({'success': True, 'message': '配置保存成功'})
        
        # 如果是单个配置项
        section = data.get('section')
        key = data.get('key')
        value = data.get('value')
        
        if section and key:
            # 加载当前配置
            config = load_config_file()
            
            # 确保配置节存在
            if section not in config:
                config[section] = {}
            
            # 处理嵌套配置
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
            
            # 更新全局配置并保存
            my_config = config
            save_config()
            
            return jsonify({'success': True, 'message': '配置保存成功'})
        else:
            return jsonify({'success': False, 'message': '参数错误'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

@bp.route('/api/current')
def get_current_config():
    """获取当前配置"""
    try:
        config = load_config_file()
        return jsonify({'success': True, 'data': config})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取配置失败: {str(e)}'})

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