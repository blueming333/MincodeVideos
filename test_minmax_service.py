#!/usr/bin/env python3
"""
测试MinMax音频合成功能
"""

import sys
import os
sys.path.append('.')

def test_minmax_service():
    """测试MinMax服务的基本功能"""
    try:
        print("开始测试MinMax音频服务...")

        # 导入MinMax服务
        from services.audio.minmax_service import MinMaxAudioService, minmax_voices

        print("✅ MinMax服务导入成功")

        # 创建服务实例（这会验证配置）
        service = MinMaxAudioService()
        print("✅ MinMax服务实例创建成功")

        # 测试获取语音列表
        voices = service.get_available_voices()
        print(f"✅ 获取到 {len(voices)} 个可用语音")

        # 测试语音列表结构
        zh_voices = minmax_voices.get('zh-CN', {})
        en_voices = minmax_voices.get('en-US', {})
        print(f"✅ 中文语音: {len(zh_voices)} 个")
        print(f"✅ 英文语音: {len(en_voices)} 个")

        print("\n🎉 MinMax服务集成测试通过！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_minmax_api_call():
    """测试实际的API调用（需要有效的API密钥）"""
    try:
        print("\n开始测试MinMax API调用...")

        # 这里可以添加实际的API调用测试
        # 但需要有效的API密钥和Group ID
        print("⚠️  API调用测试需要有效的MinMax API凭据")
        print("请在config.yml中配置正确的api_key和group_id后手动测试")

        return True

    except Exception as e:
        print(f"❌ API调用测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("MinMax音频服务集成测试")
    print("=" * 50)

    success1 = test_minmax_service()
    success2 = test_minmax_api_call()

    print("\n" + "=" * 50)
    if success1:
        print("🎉 MinMax服务集成成功！")
        print("\n配置步骤:")
        print("1. 在GUI配置页面选择 'MinMax' 作为音频提供商")
        print("2. 配置以下参数:")
        print("   - API Key: 从MinMax控制台获取")
        print("   - Group ID: 使用分配的组ID")
        print("   - Base URL: https://api.minimaxi.com")
        print("   - Model: 选择合适的模型版本")
        print("\n支持的模型:")
        print("   - speech-2.5-hd-preview (高清预览)")
        print("   - speech-2.5-turbo-preview (快速预览)")
        print("   - speech-02-hd (高清)")
        print("   - speech-02-turbo (快速)")
    else:
        print("❌ 集成测试失败")

    print("=" * 50)
    sys.exit(0 if success1 else 1)
