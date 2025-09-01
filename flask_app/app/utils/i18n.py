"""
国际化工具类
"""
import json
import os
from flask import session, request, current_app

class I18nManager:
    """国际化管理器"""
    
    def __init__(self, app=None):
        self.translations = {}
        self.default_locale = 'en'
        self.available_locales = ['en', 'zh-CN']
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化Flask应用"""
        self.load_translations()
        
        # 注册模板全局函数
        app.jinja_env.globals['_'] = self.get_text
        app.jinja_env.globals['get_locale'] = self.get_locale
        app.jinja_env.globals['get_available_locales'] = self.get_available_locales
        
        # 注册上下文处理器
        @app.context_processor
        def inject_i18n():
            return {
                'current_locale': self.get_locale(),
                'available_locales': self.get_available_locales()
            }
    
    def load_translations(self):
        """加载翻译文件"""
        locales_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'locales')
        
        for locale in self.available_locales:
            locale_file = os.path.join(locales_dir, f'{locale}.json')
            if os.path.exists(locale_file):
                try:
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.translations[locale] = json.load(f)
                except Exception as e:
                    print(f"加载语言文件 {locale_file} 失败: {e}")
                    self.translations[locale] = {}
            else:
                self.translations[locale] = {}
    
    def get_locale(self):
        """获取当前语言设置"""
        # 1. 检查session中的设置
        if 'locale' in session:
            return session['locale']
        
        # 2. 检查浏览器语言偏好
        if request:
            best_match = request.accept_languages.best_match(self.available_locales)
            if best_match:
                return best_match
        
        # 3. 返回默认语言
        return self.default_locale
    
    def set_locale(self, locale):
        """设置当前语言"""
        if locale in self.available_locales:
            session['locale'] = locale
            return True
        return False
    
    def get_available_locales(self):
        """获取可用语言列表"""
        return [
            {'code': 'en', 'name': 'English', 'native_name': 'English'},
            {'code': 'zh-CN', 'name': 'Chinese (Simplified)', 'native_name': '简体中文'}
        ]
    
    def get_text(self, key, **kwargs):
        """获取翻译文本"""
        locale = self.get_locale()
        
        # 获取翻译文本
        text = self.translations.get(locale, {}).get(key)
        
        # 如果当前语言没有翻译，尝试使用默认语言
        if text is None and locale != self.default_locale:
            text = self.translations.get(self.default_locale, {}).get(key)
        
        # 如果还是没有翻译，返回原始key
        if text is None:
            text = key
        
        # 处理参数替换
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return text

# 创建全局实例
i18n = I18nManager()
