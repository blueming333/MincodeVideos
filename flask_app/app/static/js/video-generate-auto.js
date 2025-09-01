/**
 * 自动工作流逻辑
 */

// 自动步骤方法
function loadAutoStepMethods(app) {
    // 自动步骤1: 内容生成
    app.autoStep1 = async function() {
        this.currentAutoStep = 1;
        this.currentAutoStatus = '正在生成视频脚本...';
        this.setStepStatus(1, '正在生成脚本...', true);
        
        try {
            const response = await apiRequest('/api/video/generate_content', {
                topic: this.config.topic,
                language: this.config.language,
                duration: this.config.duration
            }, 'POST', this.autoAbortController?.signal);
            
            this.results.content = response.data.content;
            this.currentStep = Math.max(this.currentStep, 2);
            this.autoProgress = 20;
            this.setStepStatus(1, '脚本生成完成 ✓', false);
            this.currentAutoStatus = '视频脚本生成完成';
        } catch (error) {
            if (error.name === 'AbortError') throw error;
            this.setStepStatus(1, '脚本生成失败 ✗', false);
            throw new Error('脚本生成失败: ' + error.message);
        }
    };
    
    // 自动步骤2: 资源获取
    app.autoStep2 = async function() {
        this.currentAutoStep = 2;
        this.currentAutoStatus = '正在获取视频资源...';
        this.setStepStatus(2, '正在获取资源...', true);
        
        try {
            const response = await apiRequest('/api/video/get_resources', {
                content: this.results.content
            }, 'POST', this.autoAbortController?.signal);
            
            this.results.resources = response.data.resources;
            this.currentStep = Math.max(this.currentStep, 3);
            this.autoProgress = 40;
            this.setStepStatus(2, `资源获取完成 ✓ (${response.data.resources?.length || 0}个)`, false);
            this.currentAutoStatus = '视频资源获取完成';
        } catch (error) {
            if (error.name === 'AbortError') throw error;
            this.setStepStatus(2, '资源获取失败 ✗', false);
            throw new Error('资源获取失败: ' + error.message);
        }
    };
    
    // 自动步骤3: 语音合成
    app.autoStep3 = async function() {
        this.currentAutoStep = 3;
        this.currentAutoStatus = '正在合成语音...';
        this.setStepStatus(3, '正在合成语音...', true);
        
        try {
            const response = await apiRequest('/api/video/generate_dubbing', {
                content: this.results.content,
                audio_type: this.config.audio.type,
                voice: this.config.audio.voice,
                audio_speed: this.config.audio.speed
            }, 'POST', this.autoAbortController?.signal);
            
            this.results.audio = response.data;
            this.currentStep = Math.max(this.currentStep, 4);
            this.autoProgress = 60;
            this.setStepStatus(3, '语音合成完成 ✓', false);
            this.currentAutoStatus = '语音合成完成';
        } catch (error) {
            if (error.name === 'AbortError') throw error;
            this.setStepStatus(3, '语音合成失败 ✗', false);
            throw new Error('语音合成失败: ' + error.message);
        }
    };
    
    // 自动步骤4: 字幕生成
    app.autoStep4 = async function() {
        if (!this.config.subtitle.enabled) {
            this.autoProgress = 80;
            this.currentAutoStatus = '跳过字幕生成...';
            return;
        }
        
        this.currentAutoStep = 4;
        this.currentAutoStatus = '正在生成字幕...';
        this.setStepStatus(4, '正在生成字幕...', true);
        
        try {
            const response = await apiRequest('/api/video/generate_subtitle', {
                audio_file: this.results.audio?.file || '',
                content: this.results.content,
                language: this.config.language
            }, 'POST', this.autoAbortController?.signal);
            
            this.results.subtitle = response.data;
            this.currentStep = Math.max(this.currentStep, 5);
            this.autoProgress = 80;
            this.setStepStatus(4, '字幕生成完成 ✓', false);
            this.currentAutoStatus = '字幕生成完成';
        } catch (error) {
            if (error.name === 'AbortError') throw error;
            this.setStepStatus(4, '字幕生成失败 ✗', false);
            throw new Error('字幕生成失败: ' + error.message);
        }
    };
    
    // 自动步骤5: 视频合成
    app.autoStep5 = async function() {
        this.currentAutoStep = 5;
        this.currentAutoStatus = '正在合成最终视频...';
        this.setStepStatus(5, '正在合成视频...', true);
        this.progress = 0;
        
        // 模拟视频合成进度
        const progressInterval = setInterval(() => {
            if (this.progress < 90 && this.isAutoRunning) {
                this.progress += Math.random() * 8;
                this.autoProgress = 80 + (this.progress / 90) * 20;
            }
        }, 800);
        
        try {
            const response = await apiRequest('/api/video/generate_final', {
                audio_file: this.results.audio?.file || '',
                subtitle_file: this.results.subtitle?.file || '',
                resources: this.results.resources || [],
                enable_subtitle: this.config.subtitle.enabled,
                video_layout: this.config.video.layout,
                video_fps: parseInt(this.config.video.fps),
                enable_transition: this.config.video.enable_transition
            }, 'POST', this.autoAbortController?.signal);
            
            clearInterval(progressInterval);
            this.progress = 100;
            this.autoProgress = 100;
            
            this.results.video = response.data;
            this.setStepStatus(5, '视频合成完成 ✓', false);
            this.currentAutoStatus = '视频生成完成！';
        } catch (error) {
            clearInterval(progressInterval);
            if (error.name === 'AbortError') throw error;
            this.setStepStatus(5, '视频合成失败 ✗', false);
            throw new Error('视频合成失败: ' + error.message);
        }
    };
}

// API请求封装函数
async function apiRequest(url, data = null, method = 'GET', signal = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        signal
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: '请求失败' }));
        throw new Error(errorData.message || `HTTP ${response.status}`);
    }
    
    return await response.json();
}

// Toast 消息函数
function showToast(message, type = 'info') {
    // 创建或获取toast容器
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-white bg-${getBootstrapColorClass(type)} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // 自动移除
    setTimeout(() => {
        toast.remove();
    }, 5000);
    
    // 点击关闭
    const closeBtn = toast.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
}

function getBootstrapColorClass(type) {
    switch (type) {
        case 'success': return 'success';
        case 'error': return 'danger';
        case 'warning': return 'warning';
        case 'info': return 'info';
        default: return 'secondary';
    }
}

// 工具函数
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 导出到全局
window.loadAutoStepMethods = loadAutoStepMethods;
window.apiRequest = apiRequest;
window.showToast = showToast;
window.loadAutoWorkflowMethods = function(app) {
    loadAutoStepMethods(app);
};
