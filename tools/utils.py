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
#

import os
import random
import subprocess
import time
import streamlit as st
from typing import Optional

from tools.file_utils import generate_temp_filename


def generate_operator():
    operators = ['+', '-']
    return random.choice(operators)


def random_with_system_time():
    system_time = int(time.time() * 1000)
    random_seed = (system_time + random.randint(0, 10000))
    return random_seed


def get_images_with_prefix(img_dir, img_file_prefix):
    # 确保提供的是绝对路径
    img_dir = os.path.abspath(img_dir)

    # 持有所有匹配前缀的图片文件的列表
    images_with_prefix = []

    # 遍历img_dir中的文件
    for filename in os.listdir(img_dir):
        # print('filename:', filename)
        # print('img_file_prefix:',img_file_prefix)
        # print(filename.startswith(img_file_prefix))
        # 检查文件名是否以img_file_prefix开头 并且后缀是.jpg
        if filename.startswith(img_file_prefix) and (filename.endswith('.png') or filename.endswith('.jpg')):
            # 构建完整的文件路径
            file_path = os.path.join(img_dir, filename)
            # 确保这是一个文件而不是目录
            if os.path.isfile(file_path):
                images_with_prefix.append(file_path)

    return images_with_prefix


def get_file_from_dir(file_dir, extension):
    extension_list = [ext.strip() for ext in extension.split(',')]
    # 确保提供的是绝对路径
    file_dir = os.path.abspath(file_dir)

    # 所有文件的列表
    file_list = []

    # 遍历file_dir中的文件
    for filename in os.listdir(file_dir):
        # print('filename:', filename)
        file_extension = os.path.splitext(filename)[1]
        # 检查文件名是否以img_file_prefix开头 并且后缀是.txt
        if file_extension in extension_list:
            # 构建完整的文件路径
            file_path = os.path.join(file_dir, filename)
            # 确保这是一个文件而不是目录
            if os.path.isfile(file_path):
                file_list.append(file_path)

    return file_list


def get_file_map_from_dir(file_dir, extension):
    extension_list = [ext.strip() for ext in extension.split(',')]
    # 确保提供的是绝对路径
    # 所有文件的列表
    file_map = {}
    if file_dir is not None and os.path.exists(file_dir):
        file_dir = os.path.abspath(file_dir)

        # 遍历file_dir中的文件
        for filename in os.listdir(file_dir):
            # print('filename:', filename)
            file_extension = os.path.splitext(filename)[1]
            # 检查文件名是否以img_file_prefix开头 并且后缀是.txt
            if file_extension in extension_list:
                # 构建完整的文件路径
                file_path = os.path.join(file_dir, filename)
                # 确保这是一个文件而不是目录
                if os.path.isfile(file_path):
                    file_map[file_path] = os.path.split(file_path)[1]

    return file_map


def get_text_from_dir(text_dir):
    return get_file_from_dir(text_dir, ".txt")


def get_mp4_from_dir(video_dir):
    return get_file_from_dir(video_dir, ".mp4")


def get_session_option(option: str) -> Optional[str]:
    return st.session_state.get(option)


def get_must_session_option(option: str, msg: str) -> Optional[str]:
    result = st.session_state.get(option)
    if not result:
        st.toast(msg, icon="⚠️")
        st.stop()
    return result


def must_have_value(option: str, msg: str) -> Optional[str]:
    if not option:
        st.toast(msg, icon="⚠️")
        st.stop()
    return option


def run_ffmpeg_command(command):
    try:
        result = subprocess.run(command, capture_output=True, check=True, text=True)
        if result.returncode != 0:
            print(f"FFmpeg returned an error: {result.stderr}")
        else:
            print("Command executed successfully.")
    except Exception as e:
        print(f"An error occurred while execute ffmpeg command {e}")


def extent_audio(audio_file, pad_dur=2):
    """
    延长音频文件时长

    Args:
        audio_file: 音频文件路径
        pad_dur: 要添加的时长（秒）
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(audio_file):
            print(f"错误: 音频文件不存在 - {audio_file}")
            return False

        # 检查文件大小
        file_size = os.path.getsize(audio_file)
        if file_size == 0:
            print(f"错误: 音频文件为空 - {audio_file}")
            return False

        temp_file = generate_temp_filename(audio_file)

        # 根据输入文件后缀选择合适的编码参数
        _, ext = os.path.splitext(audio_file)
        ext = ext.lower()
        if ext == '.wav':
            # 生成真正的PCM WAV，便于后续字幕(wave模块)读取
            command = [
                'ffmpeg',
                '-i', audio_file,
                '-af', f'apad=pad_dur={pad_dur}',
                '-c:a', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                temp_file
            ]
        else:
            # 其它情况保持压缩编码，例如mp3
            command = [
                'ffmpeg',
                '-i', audio_file,
                '-af', f'apad=pad_dur={pad_dur}',
                '-c:a', 'mp3',
                temp_file
            ]

        print(f"执行FFmpeg命令: {' '.join(command)}")

        # 执行命令，增加超时时间
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # 不自动抛出异常，以便我们处理
            timeout=30    # 设置30秒超时
        )

        if result.returncode == 0:
            print("FFmpeg 执行成功")
            # 重命名最终的文件
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                os.remove(audio_file)
                os.renames(temp_file, audio_file)
                print(f"音频文件延长成功: {audio_file}")
                return True
            else:
                print("错误: FFmpeg 执行成功但输出文件无效")
                return False
        else:
            print(f"FFmpeg 执行失败 (退出码: {result.returncode})")
            print(f"标准输出: {result.stdout}")
            print(f"标准错误: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"FFmpeg 执行超时 (30秒): {audio_file}")
        return False
    except Exception as e:
        print(f"延长音频时出现异常: {e}")
        return False
