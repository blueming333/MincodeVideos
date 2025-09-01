"""
国际化API路由
"""
from flask import Blueprint, request, jsonify, session
from ..utils.i18n import i18n

i18n_api = Blueprint('i18n_api', __name__)

@i18n_api.route('/api/i18n/locale', methods=['GET'])
def get_locale():
    """获取当前语言设置"""
    return jsonify({
        'current_locale': i18n.get_locale(),
        'available_locales': i18n.get_available_locales()
    })

@i18n_api.route('/api/i18n/locale', methods=['POST'])
def set_locale():
    """设置语言"""
    data = request.get_json()
    locale = data.get('locale')
    
    if not locale:
        return jsonify({'error': 'locale is required'}), 400
    
    if i18n.set_locale(locale):
        return jsonify({
            'success': True,
            'locale': locale,
            'message': 'Language changed successfully'
        })
    else:
        return jsonify({
            'error': f'Unsupported locale: {locale}',
            'available_locales': i18n.get_available_locales()
        }), 400

@i18n_api.route('/api/i18n/translations/<locale>')
def get_translations(locale):
    """获取指定语言的翻译文件"""
    if locale not in [l['code'] for l in i18n.get_available_locales()]:
        return jsonify({'error': f'Unsupported locale: {locale}'}), 400
    
    translations = i18n.translations.get(locale, {})
    return jsonify(translations)
