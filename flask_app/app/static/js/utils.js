/**
 * API请求工具函数
 */

// API基础配置
const API_BASE_URL = '';

/**
 * 发送API请求
 * @param {string} url - 请求URL
 * @param {Object} data - 请求数据
 * @param {string} method - 请求方法 (GET, POST, PUT, DELETE)
 * @param {Object} options - 额外选项
 */
async function apiRequest(url, data = null, method = 'GET', options = {}) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            ...options.headers
        },
        ...options
    };

    // 添加请求体
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(API_BASE_URL + url, config);
        
        // 检查响应状态
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP错误: ${response.status}`);
        }

        const result = await response.json();
        
        // 检查业务逻辑成功状态
        if (result.success === false) {
            throw new Error(result.message || '请求失败');
        }

        return result;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// 视频生成器应用
function videoGeneratorApp() {
    return {
        // 基础配置
        config: {
            topic: '',
            language: 'zh-CN',
            duration: 60,
            video: {
                layout: 'landscape',
                size: '1920x1080',
                fps: 30
            },
            audio: {
                type: 'remote',
                voice: 'aicheng',  // 使用阿里云基础音色
                speed: 'normal',
                emotion: 'calm'
            }
        },
        
        // 生成结果
        results: {
            content: null,
            keywords: null,
            resources: null,
            audio: null,
            subtitle: null,
            video: null
        },
        // 手动文案输入
        manualContent: '',
        
        // 状态管理
        isLoading: false,
        currentAction: null,
        errors: {},
        
        // 初始化
        init() {
            console.log('视频生成器初始化完成');
        },
        
        // 验证方法
        canGenerateContent() {
            return this.config.topic.trim().length > 10;
        },
        
        canGenerateVideo() {
            return this.results.content && this.results.keywords && this.results.resources;
        },
        
        // 步骤1: 生成视频内容
        async generateContent() {
            if (!this.canGenerateContent()) {
                this.errors.topic = '请输入至少10个字符的视频主题';
                return;
            }
            
            this.errors = {};
            this.isLoading = true;
            this.currentAction = 'content';
            
            try {
                const response = await this.callAPI('/api/video/generate_content', {
                    topic: this.config.topic,
                    language: this.config.language,
                    duration: this.config.duration
                });
                
                if (response.success) {
                    this.results.content = response.data.content;
                    this.showSuccess('视频内容生成成功！');
                } else {
                    this.showError(response.message || '生成内容失败');
                }
            } catch (error) {
                this.showError('网络错误，请重试');
                console.error('Generate content error:', error);
            } finally {
                this.isLoading = false;
                this.currentAction = null;
            }
        },
        
        // 步骤2: 生成关键词
        async generateKeywords() {
            if (!this.results.content) return;
            
            this.isLoading = true;
            this.currentAction = 'keywords';
            
            try {
                const response = await this.callAPI('/api/video/generate_keywords', {
                    content: this.results.content,
                    language: this.config.language
                });
                
                if (response.success) {
                    this.results.keywords = response.data.keywords;
                    this.showSuccess('关键词提取成功！');
                } else {
                    this.showError(response.message || '生成关键词失败');
                }
            } catch (error) {
                this.showError('网络错误，请重试');
                console.error('Generate keywords error:', error);
            } finally {
                this.isLoading = false;
                this.currentAction = null;
            }
        },
        
        // 步骤3: 获取视频资源
        async getResources() {
            if (!this.results.keywords) return;
            
            this.isLoading = true;
            this.currentAction = 'resources';
            
            try {
                const keywords = Array.isArray(this.results.keywords) 
                    ? this.results.keywords 
                    : this.results.keywords.split(',').map(k => k.trim());
                    
                const response = await this.callAPI('/api/video/get_resources', {
                    keywords: keywords,
                    duration: this.config.duration,
                    language: this.config.language
                });
                
                if (response.success) {
                    this.results.resources = response.data.resources;
                    this.showSuccess(`找到 ${response.data.resources.length} 个视频资源！`);
                } else {
                    this.showError(response.message || '获取资源失败');
                }
            } catch (error) {
                this.showError('网络错误，请重试');
                console.error('Get resources error:', error);
            } finally {
                this.isLoading = false;
                this.currentAction = null;
            }
        },
        
        // 步骤4: 生成配音
        async generateDubbing() {
            if (!this.results.content) return;
            
            this.isLoading = true;
            this.currentAction = 'dubbing';
            
            try {
                const response = await this.callAPI('/api/video/generate_dubbing', {
                    content: this.results.content,
                    audio_type: this.config.audio.type,
                    voice: this.config.audio.voice,
                    audio_speed: this.config.audio.speed,
                    emotion: this.config.audio.emotion,
                    language: this.config.language
                });
                
                if (response.success) {
                    this.results.audio = response.data.audio;
                    this.showSuccess('AI配音生成成功！');
                } else {
                    this.showError(response.message || '生成配音失败');
                }
            } catch (error) {
                this.showError('网络错误，请重试');
                console.error('Generate dubbing error:', error);
            } finally {
                this.isLoading = false;
                this.currentAction = null;
            }
        },
        
        // 步骤5: 生成字幕
        async generateSubtitle() {
            if (!this.results.audio) return;
            
            this.isLoading = true;
            this.currentAction = 'subtitle';
            
            try {
                const response = await this.callAPI('/api/video/generate_subtitle', {
                    audio_file: this.results.audio.file,
                    content: this.results.content,
                    language: this.config.language
                });
                
                if (response.success) {
                    this.results.subtitle = response.data.subtitle;
                    this.showSuccess('字幕生成成功！');
                } else {
                    this.showError(response.message || '生成字幕失败');
                }
            } catch (error) {
                this.showError('网络错误，请重试');
                console.error('Generate subtitle error:', error);
            } finally {
                this.isLoading = false;
                this.currentAction = null;
            }
        },
        
        // 步骤6: 合成最终视频
        async generateFinalVideo() {
            if (!this.canGenerateVideo()) return;
            
            this.isLoading = true;
            this.currentAction = 'video';
            
            try {
                const response = await this.callAPI('/api/video/generate_final', {
                    content: this.results.content,
                    resources: this.results.resources,
                    audio: this.results.audio,
                    subtitle: this.results.subtitle,
                    video_config: this.config.video,
                    language: this.config.language
                });
                
                if (response.success) {
                    this.results.video = response.data.video;
                    this.showSuccess('视频合成完成！');
                } else {
                    this.showError(response.message || '视频生成失败');
                }
            } catch (error) {
                this.showError('网络错误，请重试');
                console.error('Generate final video error:', error);
            } finally {
                this.isLoading = false;
                this.currentAction = null;
            }
        },
        
        // 辅助方法
        updateVideoSize() {
            const sizeMap = {
                landscape: '1920x1080',
                portrait: '1080x1920',
                square: '1080x1080'
            };
            this.config.video.size = sizeMap[this.config.video.layout];
        },
        
        editContent() {
            // 允许用户编辑生成的内容
            const newContent = prompt('编辑视频内容:', this.results.content);
            if (newContent && newContent.trim()) {
                this.results.content = newContent.trim();
                this.showSuccess('内容已更新');
            }
        },
        
        testAudio() {
            if (this.results.audio?.url) {
                const audio = new Audio(this.results.audio.url);
                audio.play().catch(e => {
                    this.showError('音频播放失败');
                });
            }
        },
        
        downloadVideo() {
            if (this.results.video?.url) {
                const a = document.createElement('a');
                a.href = this.results.video.url;
                a.download = `video_${Date.now()}.mp4`;
                a.click();
            }
        },
        
        shareVideo() {
            if (this.results.video?.url) {
                if (navigator.share) {
                    navigator.share({
                        title: '我用AI生成的视频',
                        url: this.results.video.url
                    });
                } else {
                    navigator.clipboard.writeText(this.results.video.url);
                    this.showSuccess('视频链接已复制到剪贴板');
                }
            }
        },
        
        regenerateVideo() {
            if (confirm('确定要重新生成视频吗？这将清除当前的生成结果。')) {
                this.resetAll();
            }
        },
        
        resetAll() {
            this.results = {
                content: null,
                keywords: null,
                resources: null,
                audio: null,
                subtitle: null,
                video: null
            };
            this.errors = {};
            this.isLoading = false;
            this.currentAction = null;
            this.showSuccess('工作流已重置');
        },
        // 使用手动输入文案
        useManualContent() {
            if (this.manualContent && this.manualContent.trim().length >= 10) {
                this.results.content = this.manualContent.trim();
                this.showSuccess('已使用手动文案');
            } else {
                this.showError('手动文案长度至少10个字符');
            }
        },
        // 从手动文案直接提取关键词
        async extractKeywordsFromManual() {
            if (!this.manualContent || this.manualContent.trim().length < 5) {
                this.showError('请先输入足够的文案内容');
                return;
            }
            // 若尚未设为content，也先赋值
            if (!this.results.content) {
                this.results.content = this.manualContent.trim();
            }
            this.isLoading = true;
            this.currentAction = 'keywords';
            try {
                const response = await this.callAPI('/api/video/generate_keywords', {
                    content: this.manualContent.trim(),
                    language: this.config.language
                });
                if (response.success) {
                    this.results.keywords = response.data.keywords;
                    this.showSuccess('关键词提取成功！');
                } else {
                    this.showError(response.message || '关键词提取失败');
                }
            } catch (e) {
                this.showError('网络错误，提取失败');
            } finally {
                this.isLoading = false;
                this.currentAction = null;
            }
        },
        
        // API调用方法
        async callAPI(endpoint, data) {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        },
        
        // 消息提示方法
        showSuccess(message) {
            // 可以集成第三方通知库，这里先用简单的alert
            console.log('Success:', message);
            this.showToast(message, 'success');
        },
        
        showError(message) {
            console.error('Error:', message);
            this.showToast(message, 'error');
        },
        
        showToast(message, type = 'info') {
            // 创建简单的toast通知
            const toast = document.createElement('div');
            toast.className = `alert alert-${type === 'error' ? 'danger' : 'success'} position-fixed top-0 end-0 m-3`;
            toast.style.zIndex = '9999';
            toast.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}-fill me-2"></i>
                    ${message}
                    <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
                </div>
            `;
            
            document.body.appendChild(toast);
            
            // 3秒后自动消失
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 3000);
        }
    };
}

/**
 * 显示Toast通知
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success, error, warning, info)
 * @param {number} duration - 显示时长（毫秒）
 */
function showToast(message, type = 'info', duration = 3000) {
    // 移除现有的toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }

    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    
    // 设置图标
    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };

    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi ${icons[type]} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .toast-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            backdrop-filter: blur(10px);
            animation: slideInRight 0.3s ease-out;
        }

        .toast-success {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.9), rgba(21, 128, 61, 0.9));
            color: white;
        }

        .toast-error {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(185, 28, 28, 0.9));
            color: white;
        }

        .toast-warning {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.9), rgba(180, 83, 9, 0.9));
            color: white;
        }

        .toast-info {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(30, 64, 175, 0.9));
            color: white;
        }

        .toast-content {
            display: flex;
            align-items: center;
            padding: 16px 20px;
        }

        .toast-content .btn-close {
            margin-left: auto;
            background: none;
            border: none;
            color: inherit;
            opacity: 0.8;
            cursor: pointer;
            font-size: 18px;
        }

        .toast-content .btn-close:hover {
            opacity: 1;
        }

        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;

    // 添加样式到头部
    if (!document.querySelector('#toast-styles')) {
        style.id = 'toast-styles';
        document.head.appendChild(style);
    }

    // 添加到页面
    document.body.appendChild(toast);

    // 自动移除
    if (duration > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }, duration);
    }
}

/**
 * 显示加载指示器
 * @param {string} message - 加载消息
 */
function showLoading(message = '加载中...') {
    // 移除现有的加载指示器
    hideLoading();

    const loading = document.createElement('div');
    loading.id = 'global-loading';
    loading.innerHTML = `
        <div class="loading-backdrop">
            <div class="loading-content">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="loading-text">${message}</div>
            </div>
        </div>
    `;

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        #global-loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10000;
        }

        .loading-backdrop {
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .loading-content {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            min-width: 200px;
        }

        .loading-text {
            color: #6c757d;
            font-size: 1.1rem;
        }
    `;

    if (!document.querySelector('#loading-styles')) {
        style.id = 'loading-styles';
        document.head.appendChild(style);
    }

    document.body.appendChild(loading);
}

/**
 * 隐藏加载指示器
 */
function hideLoading() {
    const loading = document.querySelector('#global-loading');
    if (loading) {
        loading.remove();
    }
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 格式化时间
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时间
 */
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function} 节流后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 导出到全局作用域
window.apiRequest = apiRequest;
window.videoGeneratorApp = videoGeneratorApp;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.formatFileSize = formatFileSize;
window.formatTime = formatTime;
window.debounce = debounce;
window.throttle = throttle;