import streamlit as st
import requests
import json
import os
from urllib.parse import urlencode
import zipfile
import tempfile
from datetime import datetime

# 添加项目根目录到路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import load_config
from tools.tr_utils import tr
from pages.common import common_ui

def init_session_state():
    """初始化会话状态"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'total_pages' not in st.session_state:
        st.session_state.total_pages = 1
    if 'last_query' not in st.session_state:
        st.session_state.last_query = ""

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
        response = requests.get(url, headers=headers, params=params)
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
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Pixabay API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def search_materials(query, provider="pexels", page=1, per_page=15):
    """搜索素材"""
    config = load_config()
    
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

def download_video(url, filename):
    """下载视频文件"""
    try:
        response = requests.get(url, stream=True)
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
        st.error(f"Download failed: {str(e)}")
        return None

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

def display_video_grid(results):
    """以网格形式显示视频结果"""
    if not results:
        st.info("未找到相关结果")
        return
    
    # 网格：每行3列
    grid_container = st.container(border=True)
    with grid_container:
        cols = st.columns(3)
        for idx, video in enumerate(results):
            col = cols[idx % 3]
            with col:
                card = st.container(border=True)
                with card:
                    # 显示缩略图
                    if video["thumbnail"]:
                        try:
                            # 对于较新版本的streamlit，使用use_column_width
                            st.image(video["thumbnail"], use_column_width=True)
                        except TypeError:
                            # 对于较旧版本，使用width参数
                            st.image(video["thumbnail"], width=300)
                    
                    # 显示视频信息
                    title = video['title'][:30] + "..." if len(video['title']) > 30 else video['title']
                    st.markdown(f"**{title}**")
                    st.caption(f"👤 {video['user']} · 🏷️ {video['provider'].title()}")
                    if video['duration'] > 0:
                        st.caption(f"⏱️ {video['duration']}s · 📐 {video['width']}x{video['height']}")
                    else:
                        st.caption(f"📐 {video['width']}x{video['height']}")
                    
                    # 创建按钮行
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        # 下载按钮
                        if st.button("📥 下载", key=f"download_{video['provider']}_{video['id']}", use_container_width=True):
                            with st.spinner("下载中..."):
                                # 生成文件名
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                extension = video["video_url"].split('.')[-1] if '.' in video["video_url"] else 'mp4'
                                filename = f"{video['provider']}_{video['id']}_{timestamp}.{extension}"
                                
                                # 下载文件
                                file_path = download_video(video["video_url"], filename)
                                if file_path:
                                    st.success(f"✅ 下载成功: {filename}")
                                    st.info(f"📁 保存到: {file_path}")
                                else:
                                    st.error(f"❌ 下载失败")
                    
                    with btn_col2:
                        # 预览按钮
                        if st.button("👁️ 预览", key=f"preview_{video['provider']}_{video['id']}", use_container_width=True):
                            st.session_state.selected_video = video["video_url"]
                            st.session_state.selected_video_name = title
                            st.toast(f"正在预览 {title}")
    
    # 底部播放器（可选）
    if 'selected_video' in st.session_state and st.session_state.selected_video:
        st.markdown('---')
        st.markdown(f"### 🎬 正在预览: {st.session_state.get('selected_video_name', '')}")
        st.video(st.session_state.selected_video)

def perform_search(query, provider, per_page):
    """执行搜索"""
    if query.strip():
        with st.spinner("搜索中..."):
            results = search_materials(query, provider, 1, per_page)
            
            if "error" in results:
                st.error(f"❌ 搜索失败: {results['error']}")
                st.session_state.search_results = []
            else:
                # 格式化结果
                if provider == "pexels":
                    formatted = format_pexels_results(results)
                else:
                    formatted = format_pixabay_results(results)
                
                if "error" in formatted:
                    st.error(f"❌ 搜索失败: {formatted['error']}")
                    st.session_state.search_results = []
                else:
                    st.session_state.search_results = formatted["results"]
                    st.session_state.current_page = 1
                    st.session_state.total_pages = max(1, formatted["total"] // per_page + (1 if formatted["total"] % per_page > 0 else 0))
                    
                    if st.session_state.search_results:
                        st.success(f"✅ 找到 {len(st.session_state.search_results)} 个结果")
                    else:
                        st.info("未找到相关结果")
    else:
        st.warning("请输入搜索关键词")

def main():
    common_ui()
    
    st.markdown("<h2 style='text-align: center;padding-top: 0rem;'>🔍 素材搜索</h2>", unsafe_allow_html=True)
    
    init_session_state()
    
    st.markdown("从各种提供商搜索和下载视频素材")
    
    # 在顶部创建搜索区域
    toolbar = st.container(border=True)
    with toolbar:
        st.subheader("搜索设置")
        
        # 创建搜索表单
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            query = st.text_input(
                "搜索关键词",
                placeholder="输入关键词搜索视频...",
                label_visibility="collapsed",
                key="search_input"
            )
        
        with col2:
            provider = st.selectbox(
                "提供商",
                options=["pexels", "pixabay"],
                format_func=lambda x: "Pexels" if x == "pexels" else "Pixabay",
                label_visibility="collapsed"
            )
        
        with col3:
            per_page = st.selectbox(
                "每页结果数",
                options=[9, 15, 21, 30],
                index=1,
                label_visibility="collapsed"
            )
        
        with col4:
            search_clicked = st.button("🔍 搜索", type="primary", use_container_width=True)
    
    # 执行搜索
    if search_clicked and query:
        perform_search(query, provider, per_page)
        st.session_state.last_query = query
    
    # 显示搜索结果
    if st.session_state.search_results:
        # 显示统计信息
        result_toolbar = st.container(border=True)
        with result_toolbar:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"搜索结果 ({len(st.session_state.search_results)} 个)")
            with col2:
                if st.button("🔄 清空结果", use_container_width=True):
                    st.session_state.search_results = []
                    st.rerun()
        
        # 显示结果网格
        display_video_grid(st.session_state.search_results)
    else:
        info_container = st.container(border=True)
        with info_container:
            st.info("💡 输入关键词并点击搜索来查找视频素材")
        
        # 显示使用说明
        help_container = st.container(border=True)
        with help_container:
            st.markdown("""
            ### 使用说明
            
            1. **配置API密钥**: 在配置文件 `config/config.yml` 中的 `resource` 部分设置API密钥：
               ```yaml
               resource:
                 pexels:
                   api_key: YOUR_PEXELS_API_KEY
                 pixabay:
                   api_key: YOUR_PIXABAY_API_KEY
               ```
            2. **搜索素材**: 输入关键词，选择提供商，点击搜索
            3. **预览视频**: 点击预览按钮可以在线观看视频
            4. **下载素材**: 点击下载按钮将视频保存到本地
            5. **管理文件**: 下载的文件保存在 `work/downloads/` 目录中
            
            ### 支持的提供商
            
            - **Pexels**: 提供高质量的免费视频素材
            - **Pixabay**: 提供丰富的免费视频和图片资源
            
            ### 提示
            
            - 搜索关键词支持英文，效果更佳
            - 下载的视频会自动添加时间戳避免重名
            - 建议根据网络情况调整每页结果数量
            """)

if __name__ == "__main__":
    main()
