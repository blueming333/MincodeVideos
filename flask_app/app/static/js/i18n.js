/**
 * 前端国际化管理器
 */
class I18nManager {
    constructor() {
        this.currentLocale = 'en';
        this.translations = {};
        this.fallbackLocale = 'en';
        this.availableLocales = [
            { code: 'en', name: 'English', nativeName: 'English' },
            { code: 'zh-CN', name: 'Chinese (Simplified)', nativeName: '简体中文' }
        ];
        
        this.init();
    }

    async init() {
        try {
            // 获取当前语言设置
            const response = await fetch('/api/i18n/locale');
            const data = await response.json();
            this.currentLocale = data.current_locale || 'en';
            this.availableLocales = data.available_locales || this.availableLocales;
            
            // 加载翻译文件
            await this.loadTranslations(this.currentLocale);
            
            // 如果当前语言不是fallback语言，也加载fallback语言
            if (this.currentLocale !== this.fallbackLocale) {
                await this.loadTranslations(this.fallbackLocale);
            }
            
            // 初始化页面文本
            this.updatePageTexts();
            
        } catch (error) {
            console.error('国际化初始化失败:', error);
        }
    }

    async loadTranslations(locale) {
        try {
            const response = await fetch(`/api/i18n/translations/${locale}`);
            const translations = await response.json();
            
            if (!this.translations[locale]) {
                this.translations[locale] = {};
            }
            Object.assign(this.translations[locale], translations);
            
        } catch (error) {
            console.error(`加载语言包 ${locale} 失败:`, error);
        }
    }

    t(key, params = {}) {
        // 获取翻译文本
        let text = this.translations[this.currentLocale]?.[key];
        
        // 如果当前语言没有翻译，尝试使用fallback语言
        if (text === undefined && this.currentLocale !== this.fallbackLocale) {
            text = this.translations[this.fallbackLocale]?.[key];
        }
        
        // 如果还是没有翻译，返回key本身
        if (text === undefined) {
            text = key;
        }
        
        // 处理参数替换
        if (params && typeof text === 'string') {
            Object.keys(params).forEach(param => {
                text = text.replace(new RegExp(`{${param}}`, 'g'), params[param]);
            });
        }
        
        return text;
    }

    async setLocale(locale) {
        if (!this.availableLocales.find(l => l.code === locale)) {
            console.error(`不支持的语言: ${locale}`);
            return false;
        }

        try {
            // 发送请求到后端设置语言
            const response = await fetch('/api/i18n/locale', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ locale })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentLocale = locale;
                
                // 加载新语言的翻译
                await this.loadTranslations(locale);
                
                // 更新页面文本
                this.updatePageTexts();
                
                // 触发语言切换事件
                document.dispatchEvent(new CustomEvent('localeChanged', {
                    detail: { locale, translations: this.translations[locale] }
                }));
                
                return true;
            } else {
                console.error('设置语言失败:', data.error);
                return false;
            }
        } catch (error) {
            console.error('设置语言时发生错误:', error);
            return false;
        }
    }

    updatePageTexts() {
        // 更新所有带有 data-i18n 属性的元素
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const text = this.t(key);
            
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.type === 'button' || element.type === 'submit') {
                    element.value = text;
                } else {
                    element.placeholder = text;
                }
            } else {
                element.textContent = text;
            }
        });

        // 更新带有 data-i18n-html 属性的元素（支持HTML内容）
        document.querySelectorAll('[data-i18n-html]').forEach(element => {
            const key = element.getAttribute('data-i18n-html');
            const text = this.t(key);
            element.innerHTML = text;
        });

        // 更新带有 data-i18n-attr 属性的元素（更新属性值）
        document.querySelectorAll('[data-i18n-attr]').forEach(element => {
            const attrMap = JSON.parse(element.getAttribute('data-i18n-attr'));
            Object.keys(attrMap).forEach(attr => {
                const key = attrMap[attr];
                const text = this.t(key);
                element.setAttribute(attr, text);
            });
        });
    }

    getCurrentLocale() {
        return this.currentLocale;
    }

    getAvailableLocales() {
        return this.availableLocales;
    }

    // 格式化数字（考虑本地化）
    formatNumber(number, options = {}) {
        return new Intl.NumberFormat(this.currentLocale, options).format(number);
    }

    // 格式化日期（考虑本地化）
    formatDate(date, options = {}) {
        return new Intl.DateTimeFormat(this.currentLocale, options).format(date);
    }
}

// 创建全局实例
window.i18n = new I18nManager();

// 为Alpine.js提供全局翻译函数
window.t = (key, params) => window.i18n.t(key, params);
