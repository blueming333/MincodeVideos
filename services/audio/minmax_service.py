#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright information and must not imply that the modified version is an official version of the Software.
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
import base64
import requests
import json
from typing import Optional

from config.config import my_config
from services.audio.audio_service import AudioService
from tools.utils import must_have_value


class MinMaxAudioService(AudioService):
    """
    MinMax音频合成功能服务类
    支持文本转语音，使用MinMax的T2A v2 API
    """

    def __init__(self):
        super().__init__()
        self.api_key = my_config['audio']['MinMax']['api_key']
        self.group_id = my_config['audio']['MinMax']['group_id']
        self.base_url = my_config['audio']['MinMax'].get('base_url', 'https://api.minimaxi.com')
        self.backup_url = my_config['audio']['MinMax'].get('backup_url', 'https://api-bj.minimaxi.com')
        self.model = my_config['audio']['MinMax'].get('model', 'speech-2.5-turbo-preview')
        # 高级可选配置（提供合理默认值）
        self.language_boost = my_config['audio']['MinMax'].get('language_boost', 'auto')
        # 语速/音量/音调默认值符合官方范围
        self.default_speed = float(my_config['audio']['MinMax'].get('speed', 1.0))
        self.default_vol = float(my_config['audio']['MinMax'].get('vol', 1.2))
        self.default_pitch = int(my_config['audio']['MinMax'].get('pitch', 0))
        self.default_emotion = my_config['audio']['MinMax'].get('emotion', 'calm')
        # 音频输出设置：优先遵循配置；保存文件时若目标为.wav，会自动覆盖为wav以便字幕识别
        self.audio_sample_rate = int(my_config['audio']['MinMax'].get('sample_rate', 32000))
        self.audio_bitrate = int(my_config['audio']['MinMax'].get('bitrate', 128000))
        self.audio_format = my_config['audio']['MinMax'].get('format', 'mp3')  # mp3 | wav | flac | pcm
        self.audio_channel = int(my_config['audio']['MinMax'].get('channel', 1))
        # 其它可选
        self.latex_read = bool(my_config['audio']['MinMax'].get('latex_read', False))
        self.text_normalization = bool(my_config['audio']['MinMax'].get('text_normalization', False))
        self.subtitle_enable = bool(my_config['audio']['MinMax'].get('subtitle_enable', False))
        self.output_format = my_config['audio']['MinMax'].get('output_format', 'hex')  # hex | url
        # 发音词典与音色混合（与voice_id二选一）
        self.pronunciation_dict = my_config['audio']['MinMax'].get('pronunciation_dict', None)
        self.timbre_weights = my_config['audio']['MinMax'].get('timbre_weights', None)
        self.use_backup = False

        # 验证必需配置
        must_have_value(self.api_key, "请设置MinMax API Key")
        must_have_value(self.group_id, "请设置MinMax Group ID")

        # 设置请求头
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _get_api_url(self) -> str:
        """获取API地址，支持主备切换"""
        base = self.backup_url if self.use_backup else self.base_url
        return f"{base}/v1/t2a_v2?GroupId={self.group_id}"

    def _switch_to_backup(self):
        """切换到备用地址"""
        self.use_backup = not self.use_backup
        print(f"切换到备用地址: {self._get_api_url()}")

    def save_with_ssml(self, text: str, file_name: str, voice: str, rate: str = "1.0"):
        """
        保存音频文件（带SSML支持）

        Args:
            text: 要合成的文本
            file_name: 输出文件名
            voice: 语音ID
            rate: 语速 (0.5-2.0)
        """
        try:
            # 确保rate参数不为None
            if rate is None:
                rate = "1.0"

            # 根据目标文件后缀动态决定返回的音频格式
            target_ext = os.path.splitext(file_name)[1].lower()
            target_format = 'wav' if target_ext == '.wav' else self.audio_format

            # 调用API生成音频（根据目标格式自适配）
            synth_result = self._synthesize_audio(text, voice, rate, target_format)

            # 根据output_format处理数据
            audio_binary = None
            if not synth_result:
                print("音频合成失败")
                return False

            if isinstance(synth_result, dict) and synth_result.get('type') == 'url':
                # 通过URL下载音频
                audio_url = synth_result['value']
                resp = requests.get(audio_url, timeout=60)
                if resp.status_code == 200:
                    audio_binary = resp.content
                else:
                    print(f"下载音频失败: {resp.status_code} - {resp.text}")
                    return False
            else:
                # hex 字符串
                audio_hex = synth_result if isinstance(synth_result, str) else None
                if not audio_hex:
                    print("未获取到音频hex数据")
                    return False
                audio_binary = bytes.fromhex(audio_hex)

            # 保存到文件
            with open(file_name, 'wb') as f:
                f.write(audio_binary)

            print(f"音频文件已保存: {file_name}")
            return True

        except Exception as e:
            print(f"保存音频文件时出错: {e}")
            return False

    def read_with_ssml(self, text: str, voice: str, rate: str = "1.0"):
        """
        直接播放音频（返回音频数据）

        Args:
            text: 要合成的文本
            voice: 语音ID
            rate: 语速 (0.5-2.0)

        Returns:
            音频数据（十六进制字符串）
        """
        try:
            # 确保rate参数不为None
            if rate is None:
                rate = "1.0"
            result = self._synthesize_audio(text, voice, rate, self.audio_format)
            if isinstance(result, dict) and result.get('type') == 'url':
                # 直接返回URL以便上层处理
                return result['value']
            return result
        except Exception as e:
            print(f"生成音频时出错: {e}")
            return None

    def _synthesize_audio(self, text: str, voice: str, speed: str = "1.0", target_format: str = None) -> Optional[str | dict]:
        """
        调用MinMax API合成音频

        Args:
            text: 要合成的文本
            voice: 语音ID
            speed: 语速

        Returns:
            音频数据（十六进制字符串）
        """
        # 参数验证
        if speed is None:
            speed = "1.0"

        try:
            speed_float = float(speed)
            # 确保语速在有效范围内 (0.5-2.0)
            if speed_float < 0.5:
                speed_float = 0.5
            elif speed_float > 2.0:
                speed_float = 2.0
        except (ValueError, TypeError):
            print(f"无效的语速参数: {speed}，使用默认值 1.0")
            speed_float = 1.0

        # 语音设置（遵循官方范围并使用配置/入参）
        # 允许从会话态覆盖 vol
        vol = st.session_state.get("audio_vol") if 'st' in globals() else None
        if vol is None:
            vol = self.default_vol
        if vol <= 0:
            vol = 1.0
        if vol > 10:
            vol = 10.0
        pitch = self.default_pitch
        if pitch < -12:
            pitch = -12
        if pitch > 12:
            pitch = 12
        # 允许从会话态覆盖 emotion
        import streamlit as st
        emotion = st.session_state.get("audio_emotion") or self.default_emotion

        # 音频输出设置
        fmt = (target_format or self.audio_format or 'mp3').lower()
        # 若目标为wav，优先使用16k单声道，便于后续ASR
        sample_rate = 16000 if fmt == 'wav' else self.audio_sample_rate
        channel = 1 if fmt == 'wav' else self.audio_channel
        bitrate = self.audio_bitrate if fmt == 'mp3' else None

        # 组装请求体
        request_data = {
            "model": self.model,
            "text": text,
            "stream": False,
            "language_boost": self.language_boost,
            "output_format": self.output_format,
            "voice_setting": {
                # voice_id 与 timbre_weights 二选一
                "voice_id": voice,
                "speed": speed_float,
                "vol": vol,
                "pitch": pitch,
                "emotion": emotion
            },
            "audio_setting": {
                "sample_rate": sample_rate,
                "format": fmt,
                "channel": channel
            },
            "latex_read": self.latex_read,
            "text_normalization": self.text_normalization,
            "subtitle_enable": self.subtitle_enable
        }

        # 可选：bitrate 仅 mp3 生效
        if bitrate is not None:
            request_data["audio_setting"]["bitrate"] = bitrate

        # 可选：发音词典
        if isinstance(self.pronunciation_dict, dict) and self.pronunciation_dict:
            request_data["pronunciation_dict"] = self.pronunciation_dict

        # 可选：timbre_weights 覆盖 voice_id
        if isinstance(self.timbre_weights, list) and len(self.timbre_weights) > 0:
            # timbre_weights 形如 [{"voice_id": "xxx", "weight": 50}, ...]
            request_data["voice_setting"].pop("voice_id", None)
            request_data["timbre_weights"] = self.timbre_weights

        max_retries = 2
        for attempt in range(max_retries):
            try:
                # 发送请求
                response = requests.post(
                    self._get_api_url(),
                    headers=self.headers,
                    json=request_data,
                    timeout=30
                )

                # 检查响应状态
                if response.status_code == 200:
                    result = response.json()

                    # 检查业务状态
                    if result.get('base_resp', {}).get('status_code') == 0:
                        audio_data = result.get('data', {}).get('audio')
                        if audio_data:
                            if self.output_format == 'url':
                                return {"type": "url", "value": audio_data}
                            return audio_data
                        else:
                            print("API返回成功但无音频数据")
                            return None
                    else:
                        error_msg = result.get('base_resp', {}).get('status_msg', '未知错误')
                        print(f"MinMax API业务错误: {error_msg}")
                        return None
                else:
                    print(f"HTTP请求失败: {response.status_code} - {response.text}")

                    # 如果是主地址失败，尝试备用地址
                    if not self.use_backup and attempt == 0:
                        print("尝试切换到备用地址...")
                        self._switch_to_backup()
                        continue
                    else:
                        return None

            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
                if not self.use_backup and attempt == 0:
                    self._switch_to_backup()
                    continue

            except requests.exceptions.RequestException as e:
                print(f"请求异常: {e}")
                if not self.use_backup and attempt == 0:
                    self._switch_to_backup()
                    continue
                break

        print("所有重试都失败了")
        return None

    def get_available_voices(self) -> list:
        """
        获取可用的语音列表
        基于MinMax文档中提到的语音ID
        """
        return [
            {"id": "male-qn-qingse", "name": "男声-轻快", "language": "zh-CN"},
            {"id": "female-tianmei", "name": "女声-甜美", "language": "zh-CN"},
            {"id": "male-tianmei", "name": "男声-天美", "language": "zh-CN"},
            {"id": "female-qn-qingse", "name": "女声-轻快", "language": "zh-CN"},
            {"id": "male-qn-jingying", "name": "男声-精英", "language": "zh-CN"},
            {"id": "female-qn-jingying", "name": "女声-精英", "language": "zh-CN"},
            {"id": "male-qn-dongman", "name": "男声-动漫", "language": "zh-CN"},
            {"id": "female-qn-dongman", "name": "女声-动漫", "language": "zh-CN"},
            {"id": "male-en-us", "name": "男声-英文", "language": "en-US"},
            {"id": "female-en-us", "name": "女声-英文", "language": "en-US"},
            {"id": "English_Trustworth_Man", "name": "男声-英文-值得信赖", "language": "en-US"},
            {"id": "English_magnetic_voiced_man", "name": "男声-英文-磁性", "language": "en-US"},
            {"id": "English_expressive_narrator", "name": "男声-英文-表现力旁白", "language": "en-US"},
            {"id": "English_Aussie_Bloke", "name": "男声-英文-澳式", "language": "en-US"},
            {"id": "English_radiant_girl", "name": "女声-英文-明媚", "language": "en-US"},
            {"id": "English_compelling_lady1", "name": "女声-英文-吸引力1", "language": "en-US"},
        ]

    def get_voice_info(self, voice_id: str) -> dict:
        """
        获取语音信息

        Args:
            voice_id: 语音ID

        Returns:
            语音信息字典
        """
        voices = self.get_available_voices()
        for voice in voices:
            if voice['id'] == voice_id:
                return voice
        return {}


# 导出语音列表供其他模块使用
minmax_voices = {
    "zh-CN": {
        "male-qn-qingse": "男声-轻快",
        "female-tianmei": "女声-甜美",
        "male-tianmei": "男声-天美",
        "female-qn-qingse": "女声-轻快",
        "male-qn-jingying": "男声-精英",
        "female-qn-jingying": "女声-精英",
        "male-qn-dongman": "男声-动漫",
        "female-qn-dongman": "女声-动漫",
    },
    "en-US": {
        "English_magnetic_voiced_man": "男声-英文-磁性",
        "male-en-us": "男声-英文",
        "female-en-us": "女声-英文",
        "English_Trustworth_Man": "男声-英文-值得信赖",
        "English_expressive_narrator": "男声-英文-表现力旁白",
        "English_Aussie_Bloke": "男声-英文-澳式",
        "English_radiant_girl": "女声-英文-明媚",
        "English_compelling_lady1": "女声-英文-吸引力1",
    }
}
