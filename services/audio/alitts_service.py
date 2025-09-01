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

from pydub import AudioSegment
from pydub.playback import play

from services.alinls.speech_synthesizer import NlsSpeechSynthesizer
from services.alinls.token import getToken
from services.audio.audio_service import AudioService
from tools.utils import must_have_value

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# print("当前脚本的绝对路径是:", script_path)

# 脚本所在的目录
script_dir = os.path.dirname(script_path)
# 音频输出目录
audio_output_dir = os.path.join(script_dir, "../../work")
audio_output_dir = os.path.abspath(audio_output_dir)


class AliAudioService(AudioService):

    def __init__(self):
        super().__init__()
        
        # 尝试使用配置管理器获取配置
        try:
            # 如果在Flask环境中，尝试使用配置管理器
            try:
                from flask_app.app.utils.config_manager import config_manager
                config = config_manager.get_config()
                ali_config = config.get('audio', {}).get('Ali', {})
            except ImportError:
                # 如果配置管理器不可用，使用传统方式
                from config.config import my_config
                ali_config = my_config.get('audio', {}).get('Ali', {})
        except ImportError:
            # 如果都不可用，使用环境变量或默认值
            ali_config = {}
        
        self.ALI_ACCESS_AKID = ali_config.get('access_key_id') or os.getenv('ALI_ACCESS_AKID', '')
        self.ALI_ACCESS_AKKEY = ali_config.get('access_key_secret') or os.getenv('ALI_ACCESS_AKKEY', '') 
        self.ALI_APP_KEY = ali_config.get('app_key') or os.getenv('ALI_APP_KEY', '')
        
        must_have_value(self.ALI_ACCESS_AKID, "请设置Ali access key id")
        must_have_value(self.ALI_ACCESS_AKKEY, "请设置Ali access key secret")
        must_have_value(self.ALI_APP_KEY, "请设置Ali app key")
        self.token = getToken(self.ALI_ACCESS_AKID, self.ALI_ACCESS_AKKEY)

    def on_metainfo(self, message, *args):
        print("on_metainfo message=>{}".format(message))

    def on_error(self, message, *args):
        print("on_error args=>{}".format(args))

    def on_close(self, *args):
        print("on_close: args=>{}".format(args))
        try:
            self.__f.close()
        except Exception as e:
            print("close file failed since:", e)

    def on_data(self, data, *args):
        try:
            self.__f.write(data)
        except Exception as e:
            print("write data failed:", e)

    def on_completed(self, message, *args):
        print("on_completed:args=>{} message=>{}".format(args, message))

    def save_with_ssml(self, text, file_name, voice, rate="0"):
        self.__f = open(file_name, "wb")
        # 阿里tts支持一次性合成300字符以内的文字，如果大于300字，需要开通长文本tts功能。
        long_tts = False
        if len(text) > 300:
            long_tts = True
        nls_speech_synthesizer = NlsSpeechSynthesizer(
            token=self.token,
            appkey=self.ALI_APP_KEY,
            long_tts=long_tts,
            on_metainfo=self.on_metainfo,
            on_data=self.on_data,
            on_completed=self.on_completed,
            on_error=self.on_error,
            on_close=self.on_close,
            callback_args=[""]
        )
        r = nls_speech_synthesizer.start(text, voice=voice, aformat='wav', wait_complete=True, speech_rate=int(rate))
        print("ali tts done with result:{}".format(r))
        
        # 确保文件被关闭
        try:
            if hasattr(self, '__f') and self.__f:
                self.__f.close()
                print(f"文件已关闭: {file_name}")
        except Exception as e:
            print(f"关闭文件失败: {e}")
        
        # 检查文件是否生成成功
        try:
            if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                print(f"音频文件生成成功: {file_name}, 大小: {os.path.getsize(file_name)} 字节")
                return True
            else:
                print(f"音频文件生成失败或为空: {file_name}")
                return False
        except Exception as e:
            print(f"检查文件状态失败: {e}")
            return False

    def read_with_ssml(self, text, voice, rate="0"):
        temp_file = os.path.join(audio_output_dir, "temp.wav")
        self.save_with_ssml(text, temp_file, voice, rate)
        # 读取音频文件
        audio = AudioSegment.from_file(temp_file)
        # 剪辑音频（例如，剪辑前5秒）
        # audio_snippet = audio[:5000]
        # 播放剪辑后的音频
        play(audio)
