"""
素材搜索路由
"""

import os
import requests
import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from urllib.parse import urlencode
import tempfile

# 添加项目根目录到路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from flask_app.app.utils.config_manager import config_manager
    config_manager_available = True
except ImportError:
    config_manager_available = False
    # 向后兼容
    try:
        from config.config import load_config
        legacy_config_available = True
    except ImportError:
        legacy_config_available = False

material_bp = Blueprint('material', __name__)

# 为了与其他路由文件保持一致，添加别名
bp = material_bp

def get_config():
    """获取配置"""
    if config_manager_available:
        return config_manager.get_config()
    elif legacy_config_available:
        return load_config()
    return {}

def get_pexels_videos(query, page=1, per_page=15, api_key=None):
    """从Pexels获取视频"""
    if not api_key:
        return {"error": "Pexels API key not configured"}
    
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": api_key
    }
    params = {
        "query": query,
        "page": page,
        "per_page": per_page
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Pexels API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def get_pixabay_videos(query, page=1, per_page=15, api_key=None):
    """从Pixabay获取视频"""
    if not api_key:
        return {"error": "Pixabay API key not configured"}
    
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": api_key,
        "q": query,
        "page": page,
        "per_page": per_page,
        "video_type": "all",
        "category": "all"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Pixabay API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def search_materials(query, provider="pexels", page=1, per_page=15):
    """搜索素材"""
    config = get_config()
    
    if not config:
        return {"error": "Configuration not loaded"}
    
    # 获取resource配置
    resource_config = config.get("resource", {})
    
    if provider == "pexels":
        pexels_config = resource_config.get("pexels", {})
        api_key = pexels_config.get("api_key")
        return get_pexels_videos(query, page, per_page, api_key)
    elif provider == "pixabay":
        pixabay_config = resource_config.get("pixabay", {})
        api_key = pixabay_config.get("api_key")
        return get_pixabay_videos(query, page, per_page, api_key)
    else:
        return {"error": "Unsupported provider"}

def format_pexels_results(data):
    """格式化Pexels结果"""
    if "error" in data:
        return data
    
    formatted_results = []
    for video in data.get("videos", []):
        # 获取最佳质量的视频链接
        video_files = video.get("video_files", [])
        if video_files:
            # 选择第一个HD质量的视频，如果没有则选择第一个
            hd_video = next((vf for vf in video_files if vf.get("quality") == "hd"), video_files[0])
            
            formatted_results.append({
                "id": video.get("id"),
                "title": f"Pexels Video {video.get('id')}",
                "thumbnail": video.get("image"),
                "video_url": hd_video.get("link"),
                "duration": video.get("duration", 0),
                "width": video.get("width", 0),
                "height": video.get("height", 0),
                "provider": "pexels",
                "user": video.get("user", {}).get("name", "Unknown")
            })
    
    return {
        "results": formatted_results,
        "total": data.get("total_results", 0),
        "page": data.get("page", 1),
        "per_page": data.get("per_page", 15)
    }

def format_pixabay_results(data):
    """格式化Pixabay结果"""
    if "error" in data:
        return data
    
    formatted_results = []
    for video in data.get("hits", []):
        # 获取视频链接（优先选择medium质量）
        videos = video.get("videos", {})
        video_url = videos.get("medium", {}).get("url") or videos.get("small", {}).get("url")
        
        if video_url:
            formatted_results.append({
                "id": video.get("id"),
                "title": video.get("tags", "Pixabay Video"),
                "thumbnail": f"https://i.vimeocdn.com/video/{video.get('picture_id')}_295x166.jpg",
                "video_url": video_url,
                "duration": video.get("duration", 0),
                "width": videos.get("medium", {}).get("width", 0),
                "height": videos.get("medium", {}).get("height", 0),
                "provider": "pixabay",
                "user": video.get("user", "Unknown")
            })
    
    return {
        "results": formatted_results,
        "total": data.get("total", 0),
        "page": 1,
        "per_page": len(formatted_results)
    }

def download_video(url, filename):
    """下载视频文件"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            # 创建work目录下的downloads文件夹
            downloads_dir = os.path.join("work", "downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            file_path = os.path.join(downloads_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return file_path
        else:
            return None
    except Exception as e:
        current_app.logger.error(f"Download failed: {str(e)}")
        return None

def perform_search(query, provider, page=1, per_page=15):
    """执行搜索"""
    config = get_config()
    resource_config = config.get("resource", {})
    
    if provider == "pexels":
        pexels_config = resource_config.get("pexels", {})
        api_key = pexels_config.get("api_key", "")
        if not api_key or api_key == "API_KEY":
            return {"error": "Pexels API key not configured"}
        return get_pexels_videos(query, page, per_page, api_key)
    elif provider == "pixabay":
        pixabay_config = resource_config.get("pixabay", {})
        api_key = pixabay_config.get("api_key", "")
        if not api_key or api_key == "API_KEY":
            return {"error": "Pixabay API key not configured"}
        return get_pixabay_videos(query, page, per_page, api_key)
    else:
        return {"error": f"Unsupported provider: {provider}"}

@bp.route('/search')
def search():
    """素材搜索页面"""
    return render_template('material/search.html')

@bp.route('/api/search', methods=['GET'])
def search_materials_api():
    """搜索API"""
    query = request.args.get('query', '').strip()
    provider = request.args.get('provider', 'pexels')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 15))
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        results = perform_search(query, provider, page, per_page)
        
        if "error" in results:
            return jsonify(results), 400
        
        # 格式化结果
        if provider == "pexels":
            formatted = format_pexels_results(results)
        else:
            formatted = format_pixabay_results(results)
        
        if "error" in formatted:
            return jsonify(formatted), 400
        
        return jsonify({
            "success": True,
            "results": formatted.get("results", []),
            "total": formatted.get("total", 0),
            "page": formatted.get("page", 1),
            "per_page": formatted.get("per_page", per_page)
        })
        
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@bp.route('/api/download', methods=['POST'])
def download_video():
    """下载API"""
    video_url = request.args.get('url')
    filename = request.args.get('filename')
    
    if not video_url or not filename:
        return jsonify({"error": "URL and filename are required"}), 400
    
    try:
        file_path = download_video(video_url, filename)
        if file_path:
            return jsonify({
                "success": True,
                "message": f"Download successful: {filename}",
                "file_path": file_path
            })
        else:
            return jsonify({"error": "Download failed"}), 500
            
    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@bp.route('/api/config')
def get_config_status():
    """获取配置信息"""
    config = get_config()
    resource_config = config.get("resource", {})
    
    # 检查API密钥是否配置
    providers = {}
    
    pexels_config = resource_config.get("pexels", {})
    pexels_key = pexels_config.get("api_key", "")
    providers["pexels"] = {
        "name": "Pexels",
        "configured": bool(pexels_key and pexels_key != "API_KEY" and len(pexels_key.strip()) > 0)
    }
    
    pixabay_config = resource_config.get("pixabay", {})
    pixabay_key = pixabay_config.get("api_key", "")
    providers["pixabay"] = {
        "name": "Pixabay", 
        "configured": bool(pixabay_key and pixabay_key != "API_KEY" and len(pixabay_key.strip()) > 0)
    }
    
    return jsonify({
        "success": True,
        "providers": providers
    })
