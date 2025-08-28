# MinMax音频合成功能集成说明

## 功能概述

MoneyPrinterPlus现已集成了MinMax的音频合成功能，为用户提供更多样化的TTS（文本转语音）选择。MinMax服务支持多种语音模型和高品质音频输出。

## 核心特性

### 🎯 主要功能
- **多模型支持**: 支持speech-2.5-hd-preview、speech-2.5-turbo-preview等多种模型
- **高品质音频**: 支持高清音频输出，多种采样率和比特率选项
- **多语言支持**: 支持中文、英文等多种语言
- **流式/非流式**: 支持非流式合成，符合项目需求
- **主备地址**: 内置主备API地址切换机制，确保服务稳定性

### 🔧 技术特性
- **容错机制**: 自动切换主备地址
- **参数验证**: 完善的配置验证
- **错误处理**: 详细的错误信息和用户反馈
- **标准化接口**: 遵循项目现有的AudioService接口标准

## 架构集成

### 📁 文件结构
```
services/audio/
├── minmax_service.py          # MinMax服务实现
├── audio_service.py           # 抽象基类
├── azure_service.py           # Azure服务
├── alitts_service.py          # 阿里服务
└── tencent_tts_service.py     # 腾讯服务
```

### 🔗 集成点
1. **服务工厂**: `main.py` 中的 `get_audio_service()` 函数
2. **语音列表**: `main.py` 中的 `get_audio_voices()` 函数
3. **GUI配置**: `gui.py` 中的音频提供商配置界面
4. **配置文件**: `config/config.yml` 中的MinMax配置项

## 配置说明

### 1. 配置文件 (`config/config.yml`)
```yaml
audio:
  provider: MinMax  # 设置为MinMax
  MinMax:
    api_key: YOUR_MINMAX_API_KEY      # MinMax API密钥
    group_id: YOUR_GROUP_ID           # 用户组ID
    base_url: https://api.minimaxi.com     # 主API地址
    backup_url: https://api-bj.minimaxi.com # 备用API地址
    model: speech-2.5-turbo-preview   # 模型版本
```

### 2. GUI配置界面
在Web界面中：
1. 进入"设置"页面
2. 选择"远程音频提供商"为"MinMax"
3. 配置以下参数：
   - **API Key**: 从MinMax控制台获取
   - **Group ID**: 使用分配的组ID
   - **Base URL**: API基础地址（通常无需修改）
   - **Model**: 选择合适的模型版本

## 支持的模型

| 模型 | 说明 | 特点 |
|------|------|------|
| speech-2.5-hd-preview | 高清预览版 | 高质量，适合预览 |
| speech-2.5-turbo-preview | 快速预览版 | 快速合成，适合测试 |
| speech-02-hd | 高清版 | 高质量音频输出 |
| speech-02-turbo | 快速版 | 快速合成，效率优先 |
| speech-01-hd | 经典高清版 | 稳定的高清输出 |
| speech-01-turbo | 经典快速版 | 快速合成的经典版 |

## 语音列表

### 中文语音
- **male-qn-qingse**: 男声-轻快
- **female-tianmei**: 女声-甜美
- **male-tianmei**: 男声-天美
- **female-qn-qingse**: 女声-轻快
- **male-qn-jingying**: 男声-精英
- **female-qn-jingying**: 女声-精英
- **male-qn-dongman**: 男声-动漫
- **female-qn-dongman**: 女声-动漫

### 英文语音
- **male-en-us**: 男声-英文
- **female-en-us**: 女声-英文
- **English_Trustworth_Man**: 男声-英文-值得信赖

## API参数说明

### 请求参数
```json
{
  "model": "speech-2.5-turbo-preview",
  "text": "要合成的文本内容",
  "stream": false,
  "language_boost": "auto",
  "output_format": "hex",
  "voice_setting": {
    "voice_id": "male-qn-qingse",
    "speed": 1.0,
    "vol": 1.0,
    "pitch": 0,
    "emotion": "happy"
  },
  "audio_setting": {
    "sample_rate": 32000,
    "bitrate": 128000,
    "format": "mp3",
    "channel": 1
  }
}
```

### 响应参数
```json
{
  "data": {
    "audio": "hex编码的音频数据",
    "status": 2
  },
  "extra_info": {
    "audio_length": 5746,
    "audio_sample_rate": 32000,
    "audio_size": 100845,
    "audio_bitrate": 128000,
    "word_count": 300,
    "usage_characters": 630
  },
  "trace_id": "请求跟踪ID",
  "base_resp": {
    "status_code": 0,
    "status_msg": ""
  }
}
```

## 使用方式

### 1. 基本使用
```python
from services.audio.minmax_service import MinMaxAudioService

# 创建服务实例
service = MinMaxAudioService()

# 保存音频文件
service.save_with_ssml("你好，欢迎使用MinMax语音合成", "output.mp3", "male-qn-qingse", "1.0")

# 或者直接获取音频数据
audio_data = service.read_with_ssml("文本内容", "female-tianmei", "1.2")
```

### 2. Web界面使用
1. 启动应用: `streamlit run gui.py`
2. 进入"自动短视频生成器"页面
3. 选择音频提供商为"MinMax"
4. 配置相关参数
5. 使用视频生成流程

## 错误处理

### 常见错误及解决方案

#### 1. 配置错误
**错误**: "请设置MinMax API Key" 或 "请设置MinMax Group ID"
**解决**: 在配置文件或GUI中正确设置API Key和Group ID

#### 2. 网络错误
**错误**: 请求超时或连接失败
**解决**:
- 检查网络连接
- 服务会自动切换到备用地址重试
- 检查API密钥是否有效

#### 3. API错误
**错误**: MinMax API返回业务错误
**解决**:
- 检查Group ID是否正确
- 确认模型版本是否支持
- 查看MinMax控制台的错误详情

## 性能优化

### 1. 模型选择
- **高清需求**: 选择speech-2.5-hd-preview或speech-02-hd
- **速度优先**: 选择speech-2.5-turbo-preview或speech-02-turbo
- **平衡选择**: speech-01-hd或speech-01-turbo

### 2. 参数调优
- **语速**: 0.5-2.0之间调整
- **音量**: 0.1-2.0之间调整
- **采样率**: 根据需求选择16000、32000、44100等

## 扩展性

### 自定义功能
MinMaxAudioService类支持以下扩展：

1. **添加新模型**: 在`_synthesize_audio`方法中支持新的模型版本
2. **自定义语音**: 扩展`get_available_voices`方法添加新语音
3. **参数调整**: 修改音频设置参数以适应不同需求
4. **错误重试**: 自定义重试策略和错误处理逻辑

### 集成新功能
```python
# 示例：添加字幕生成功能
def generate_with_subtitle(self, text, voice, speed):
    # 实现带字幕的音频生成
    pass
```

## 最佳实践

### 1. 配置管理
- 使用环境变量管理敏感信息（如API Key）
- 定期轮换API密钥
- 监控API使用量和费用

### 2. 错误处理
- 实现完善的日志记录
- 设置合理的超时时间
- 准备备用方案

### 3. 性能监控
- 监控API响应时间
- 统计音频生成成功率
- 跟踪资源使用情况

## 故障排除

### 调试模式
启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 常见问题
1. **Q: 如何获取API Key和Group ID？**
   A: 登录MinMax控制台，在接口密钥管理中获取

2. **Q: 支持哪些音频格式？**
   A: 支持MP3、WAV、FLAC等主流格式

3. **Q: 如何调整音频质量？**
   A: 通过修改采样率和比特率参数调整

### 故障排除

#### 1. `float() argument must be a string or a real number, not 'NoneType'`
**原因**: `get_audio_rate()`函数中缺少MinMax的语速处理逻辑，导致返回None值
**解决**: 已修复，在v1.0.2版本中添加了完整的MinMax语速映射

#### 2. `subprocess.CalledProcessError: Command '['ffmpeg', ...]' returned non-zero exit status 254`
**原因**: FFmpeg命令执行失败，可能是音频文件格式问题或参数错误
**解决**:
- 检查音频文件是否存在且不为空
- 查看FFmpeg的详细错误输出
- 确保音频文件格式正确
- 检查磁盘空间是否充足

#### 3. MinMax API调用失败
**原因**: API密钥错误、网络问题或服务不可用
**解决**:
- 确认API Key和Group ID正确
- 检查网络连接
- 服务会自动切换到备用地址重试
- 查看MinMax控制台的错误详情

#### 4. 音频文件生成后为空或损坏
**原因**: API返回的数据格式问题或本地文件写入失败
**解决**:
- 检查API响应数据格式
- 确认本地存储空间充足
- 查看详细的错误日志信息

#### 调试模式
启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 快速诊断
```bash
# 检查FFmpeg是否正常
ffmpeg -version

# 检查Python环境
python -c "from services.audio.minmax_service import MinMaxAudioService; print('MinMax导入成功')"

# 测试API连接
python -c "
from services.audio.minmax_service import MinMaxAudioService
service = MinMaxAudioService()
result = service.read_with_ssml('Hello world', 'male-en-us', '1.0')
print('API测试结果:', '成功' if result else '失败')
"
```

## 更新日志

### v1.0.2 (2024-12-XX)
- ✅ 修复MinMax音频服务类型转换错误 (None值处理)
- ✅ 完善get_audio_rate()函数，支持MinMax语速映射
- ✅ 优化FFmpeg错误处理和调试信息
- ✅ 增强参数验证和错误恢复机制

### v1.0.1 (2024-12-XX)
- ✅ 添加新的英文语音：English_Trustworth_Man (男声-英文-值得信赖)
- ✅ 更新语音列表和语音字典
- ✅ 完善文档说明

### v1.0.0 (2024-12-XX)
- ✅ 初始版本发布
- ✅ 支持非流式音频合成
- ✅ 集成主备地址切换机制
- ✅ 提供完整的GUI配置界面
- ✅ 支持多语言语音选择
- ✅ 实现完善的错误处理

---

**作者**: 程序那些事
**技术支持**: MinMax团队
**更新时间**: 2024年12月
