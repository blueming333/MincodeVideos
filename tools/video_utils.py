#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright notice and include this permission notice.
#
#  For commercial use, including but not limited to selling, distributing, or using the Software as part of any commercial product or service, you must obtain explicit authorization from the author.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Author: 程序那些事
#  email: flydean@163.com
#  Website: [www.flydean.com](http://www.flydean.com)
#  GitHub: [https://github.com/ddean2009/MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus)
#
#  All rights reserved.
#

import os
import time
from datetime import datetime
from typing import List, Dict, Optional
try:
    import streamlit as st
except ImportError:
    # 如果streamlit未安装，创建一个模拟的st对象用于测试
    class MockST:
        @staticmethod
        def cache_data(ttl=300):
            def decorator(func):
                return func
            return decorator
    st = MockST()


@st.cache_data(ttl=300)  # 缓存5分钟
def get_video_files_info(final_dir: str = "final") -> List[Dict]:
    """
    获取final目录下的所有视频文件信息

    Args:
        final_dir: 视频文件目录，默认为"final"

    Returns:
        包含视频文件信息的字典列表，每个字典包含文件名、大小、创建时间等信息
    """
    video_files = []
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']

    try:
        # 如果是相对路径，转换为绝对路径（以项目根目录为基准）
        if not os.path.isabs(final_dir):
            base_dir = os.path.dirname(os.path.dirname(__file__))
            final_dir = os.path.join(base_dir, final_dir)

        # 检查目录是否存在
        if not os.path.exists(final_dir):
            print(f"视频目录不存在: {final_dir}")
            return video_files

        # 遍历目录获取视频文件
        for filename in os.listdir(final_dir):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                file_path = os.path.join(final_dir, filename)

                try:
                    # 获取文件信息
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    create_time = file_stat.st_ctime

                    # 跳过空文件
                    if file_size == 0:
                        continue

                    # 格式化文件大小
                    size_formatted = format_file_size(file_size)

                    # 格式化创建时间
                    create_time_formatted = format_timestamp(create_time)

                    # 提取时间戳（用于排序）
                    timestamp = extract_timestamp_from_filename(filename)

                    video_info = {
                        'filename': filename,
                        'filepath': file_path,
                        'size': file_size,
                        'size_formatted': size_formatted,
                        'create_time': create_time,
                        'create_time_formatted': create_time_formatted,
                        'timestamp': timestamp
                    }

                    video_files.append(video_info)

                except OSError as e:
                    print(f"获取文件信息失败 {filename}: {e}")
                    continue

        # 按时间戳降序排序（最新的在前面）
        video_files.sort(key=lambda x: x['timestamp'] or x['create_time'], reverse=True)

    except Exception as e:
        print(f"扫描视频文件时出错: {e}")

    return video_files


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读的格式

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        格式化后的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    i = 0
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def format_timestamp(timestamp: float) -> str:
    """
    格式化时间戳为可读的日期时间字符串

    Args:
        timestamp: Unix时间戳

    Returns:
        格式化后的日期时间字符串
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "未知时间"


def extract_timestamp_from_filename(filename: str) -> Optional[float]:
    """
    从文件名中提取时间戳（针对final-数字.mp4格式）

    Args:
        filename: 文件名

    Returns:
        提取的时间戳，如果无法提取则返回None
    """
    try:
        # 处理final-数字.mp4格式
        if filename.startswith('final-') and filename.endswith('.mp4'):
            timestamp_str = filename[6:-4]  # 移除'final-'和'.mp4'
            # 将毫秒级时间戳转换为秒级
            timestamp = int(timestamp_str) / 1000
            return timestamp
    except (ValueError, IndexError):
        pass

    return None


def get_video_thumbnail(video_path: str, thumbnail_path: str = None) -> Optional[str]:
    """
    为视频生成缩略图（可选功能，需要ffmpeg）

    Args:
        video_path: 视频文件路径
        thumbnail_path: 缩略图保存路径，如果为None则使用临时路径

    Returns:
        缩略图路径，如果生成失败则返回None
    """
    try:
        import subprocess

        if thumbnail_path is None:
            # 生成临时缩略图路径
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            thumbnail_path = os.path.join(video_dir, f"{video_name}_thumbnail.jpg")

        # 使用ffmpeg生成缩略图（取视频第1秒的帧）
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:01',
            '-vframes', '1',
            '-q:v', '2',
            thumbnail_path,
            '-y'  # 覆盖现有文件
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return thumbnail_path

    except (subprocess.CalledProcessError, FileNotFoundError):
        # ffmpeg不可用或执行失败
        return None


def get_video_duration(video_path: str) -> Optional[str]:
    """
    获取视频时长（可选功能，需要ffmpeg）

    Args:
        video_path: 视频文件路径

    Returns:
        视频时长字符串，如果获取失败则返回None
    """
    try:
        import subprocess
        import re

        # 使用ffprobe获取视频信息
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return format_duration(duration)

    except (subprocess.CalledProcessError, FileNotFoundError, KeyError, ValueError):
        pass

    return None


def format_duration(seconds: float) -> str:
    """
    格式化秒数为时长字符串

    Args:
        seconds: 秒数

    Returns:
        格式化后的时长字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"
