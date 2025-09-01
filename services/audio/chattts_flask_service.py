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

import datetime
import lzma
import os
import zipfile
from io import BytesIO

import numpy as np
import requests
import torch
from pydub import AudioSegment

from config.config import my_config
from tools.file_utils import read_file, convert_mp3_to_wav
from tools.utils import must_have_value, random_with_system_time
import pybase16384 as b14

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# print("当前脚本的绝对路径是:", script_path)

# 脚本所在的目录
script_dir = os.path.dirname(script_path)

# 音频输出目录
audio_output_dir = os.path.join(script_dir, "../../work")
audio_output_dir = os.path.abspath(audio_output_dir)


def encode_spk_emb(spk_emb: torch.Tensor) -> str:
    arr: np.ndarray = spk_emb.to(dtype=torch.float16, device="cpu").detach().numpy()
    s = b14.encode_to_string(
        lzma.compress(
            arr.tobytes(),
            format=lzma.FORMAT_RAW,
            filters=[{"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME}],
        ),
    )
    del arr
    return s

class ChatTTSFlaskService:
    """ChatTTS 服务的 Flask 版本，去除 streamlit 依赖"""
    
    def __init__(self, audio_speed='normal', refine_text=False, refine_text_prompt="", 
                 text_seed=20, audio_temperature=0.3, audio_top_p=0.7, audio_top_k=20,
                 use_random_voice=True, audio_seed=None, audio_voice_file=None):
        self.service_location = my_config['audio']['local_tts']['chatTTS']['server_location']
        must_have_value(self.service_location, "请设置ChatTTS server location")
        
        # 确保 URL 格式正确
        if not self.service_location.endswith('/'):
            self.service_location += '/'
        self.service_location = self.service_location + 'generate_voice'
        
        # 参数化配置
        self.skip_refine_text = not refine_text
        self.refine_text_prompt = refine_text_prompt or ""
        self.text_seed = text_seed or 20
        self.audio_temperature = audio_temperature or 0.3
        self.audio_top_p = audio_top_p or 0.7
        self.audio_top_k = audio_top_k or 20
        
        # 语速映射
        self.audio_speed = self._map_speed(audio_speed)
        
        # 语音设置
        if use_random_voice:
            self.audio_seed = audio_seed or random_with_system_time()
            self.audio_content = None
        else:
            self.audio_seed = None
            self.audio_content = None
            if audio_voice_file and os.path.exists(audio_voice_file):
                if audio_voice_file.endswith('.pt'):
                    self.audio_content = encode_spk_emb(torch.load(audio_voice_file, map_location=torch.device('cpu')))
                elif audio_voice_file.endswith('.txt'):
                    self.audio_content = read_file(audio_voice_file)

    def _map_speed(self, speed):
        """将前端语速映射为 ChatTTS 速度标记"""
        speed_map = {
            'slowest': '[speed_2]',
            'slower': '[speed_3]',
            'slow': '[speed_4]',
            'normal': '[speed_5]',
            'fast': '[speed_6]',
            'faster': '[speed_7]',
            'fastest': '[speed_8]'
        }
        return speed_map.get(speed, '[speed_5]')

    def generate_audio(self, content, output_file):
        """生成音频文件"""
        # main infer params
        body = {
            "text": [content],
            "stream": False,
            "lang": None,
            "skip_refine_text": self.skip_refine_text,
            "refine_text_only": False,
            "use_decoder": True,
            "audio_seed": int(self.audio_seed) if self.audio_seed else 0,
            "text_seed": int(self.text_seed),
            "do_text_normalization": True,
            "do_homophone_replacement": False,
        }

        # refine text params
        params_refine_text = {
            "prompt": self.refine_text_prompt,
            "top_P": float(self.audio_top_p),
            "top_K": int(self.audio_top_k),
            "temperature": float(self.audio_temperature),
            "repetition_penalty": 1,
            "max_new_token": 384,
            "min_new_token": 0,
            "show_tqdm": True,
            "ensure_non_empty": True,
            "stream_batch": 24,
        }
        body["params_refine_text"] = params_refine_text

        # infer code params
        params_infer_code = {
            "prompt": self.audio_speed,
            "top_P": float(self.audio_top_p),
            "top_K": int(self.audio_top_k),
            "temperature": float(self.audio_temperature),
            "repetition_penalty": 1.05,
            "max_new_token": 2048,
            "min_new_token": 0,
            "show_tqdm": True,
            "ensure_non_empty": True,
            "stream_batch": True,
            "spk_emb": self.audio_content if not self.audio_seed else None,
        }
        body["params_infer_code"] = params_infer_code

        print(f"ChatTTS request to {self.service_location}: {body}")

        try:
            response = requests.post(self.service_location, json=body)
            response.raise_for_status()
            with zipfile.ZipFile(BytesIO(response.content), "r") as zip_ref:
                # 提取到临时目录
                temp_dir = os.path.dirname(output_file)
                zip_ref.extractall(temp_dir)
                file_names = zip_ref.namelist()
                
                if file_names:
                    temp_output = os.path.join(temp_dir, file_names[0])
                    # 转换为目标格式
                    convert_mp3_to_wav(temp_output, output_file)
                    
                    # 清理临时文件
                    if temp_output != output_file and os.path.exists(temp_output):
                        os.remove(temp_output)
                    
                    print(f"ChatTTS audio generated: {output_file}")
                    return output_file
                else:
                    raise Exception("No files in ChatTTS response")

        except requests.exceptions.RequestException as e:
            print(f"ChatTTS Request Error: {e}")
            raise e
        except Exception as e:
            print(f"ChatTTS Processing Error: {e}")
            raise e

    # 兼容原接口
    def chat_with_content(self, content, audio_output_file):
        return self.generate_audio(content, audio_output_file)