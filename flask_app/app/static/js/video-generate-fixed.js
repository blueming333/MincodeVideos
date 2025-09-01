/**
 * 视频生成工作流 JavaScript
 */

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

// 主应用函数
function videoGeneratePage() {
    return {
        // 基础状态
        currentStep: 1,
        isLoading: false,
        progress: 0,
        
        // 全自动工作流相关
        isAutoRunning: false,
        autoProgress: 0,
        currentAutoStep: 0,
        currentAutoStatus: '等待开始...',
        autoAbortController: null,
        
        // 步骤状态管理
        stepStatus: {
            1: null, 2: null, 3: null, 4: null, 5: null
        },
        stepLoading: {
            1: false, 2: false, 3: false, 4: false, 5: false
        },
        
        // 配置数据
        config: {
            topic: '',
            language: 'zh-CN',
            duration: 120,
            video: {
                layout: 'landscape',
                fps: '30',
                size: '1280x720',
                enable_transition: true
            },
            audio: {
                type: 'remote',
                language: 'zh-CN',
                voice: 'aicheng',
                speed: 'normal'
            },
            subtitle: {
                enabled: true,
                font: 'PingFang SC Regular',
                size: 24,
                position: 2,
                color: '#FFFFFF',
                border_color: '#000000',
                border_width: 0
            }
        },
        
        // 结果数据
        results: {
            content: null,
            resources: null,
            audio: null,
            subtitle: null,
            video: null
        },
        
        // 初始化方法
        init() {
            console.log('视频生成页面已初始化');
            this.updateVideoSize();
        },
        
        // 步骤状态方法
        getStepClass(step) {
            if (this.stepLoading[step]) return 'active bg-warning';
            if (step < this.currentStep) return 'completed bg-success text-white';
            if (step === this.currentStep) return 'active bg-primary text-white';
            return 'bg-secondary text-white';
        },
        
        getStepLoading(step) {
            return this.stepLoading[step];
        },
        
        getStepStatusClass(step) {
            const status = this.stepStatus[step];
            if (!status) return '';
            if (status.includes('成功') || status.includes('完成')) return 'text-success';
            if (status.includes('进行中') || status.includes('处理中')) return 'text-warning';
            if (status.includes('失败') || status.includes('错误')) return 'text-danger';
            return 'text-muted';
        },
        
        setStepStatus(step, status, loading = false) {
            this.stepStatus[step] = status;
            this.stepLoading[step] = loading;
        },
        
        // 验证方法
        canStartAutoWorkflow() {
            return this.config.topic.trim().length > 10 && !this.isAutoRunning;
        },
        
        canGenerateVideo() {
            return this.results.content && 
                   this.results.resources && 
                   this.results.audio && 
                   (this.config.subtitle.enabled ? this.results.subtitle : true);
        },
        
        // 配置更新方法
        updateVideoSize() {
            const layout = this.config.video.layout;
            if (layout === 'landscape') {
                this.config.video.size = '1280x720';
            } else if (layout === 'portrait') {
                this.config.video.size = '720x1280';
            } else { // square
                this.config.video.size = '720x720';
            }
        },
        
        // 工作流控制方法
        resetWorkflow(showToastMessage = true) {
            this.currentStep = 1;
            this.results = {
                content: null,
                resources: null,
                audio: null,
                subtitle: null,
                video: null
            };
            this.progress = 0;
            this.autoProgress = 0;
            this.currentAutoStep = 0;
            this.currentAutoStatus = '等待开始...';
            
            // 重置步骤状态
            for (let i = 1; i <= 5; i++) {
                this.stepStatus[i] = null;
                this.stepLoading[i] = false;
            }
            
            if (showToastMessage) {
                showToast('工作流已重置', 'info');
            }
        },
        
        editContent() {
            const newContent = prompt('编辑视频脚本:', this.results.content);
            if (newContent && newContent.trim()) {
                this.results.content = newContent.trim();
                showToast('内容已更新', 'success');
            }
        },
        
        shareVideo() {
            if (navigator.share && this.results.video?.url) {
                navigator.share({
                    title: 'AI生成的视频',
                    text: '使用MincodeVideos生成的AI视频',
                    url: this.results.video.url
                });
            } else {
                navigator.clipboard.writeText(this.results.video?.url || '').then(() => {
                    showToast('视频链接已复制到剪贴板', 'success');
                });
            }
        },

        // 全自动工作流主方法
        async runAutoWorkflow() {
            if (!this.canStartAutoWorkflow()) {
                showToast('请先输入视频主题（至少10个字符）', 'warning');
                return;
            }
            
            this.isAutoRunning = true;
            this.autoProgress = 0;
            this.currentAutoStep = 0;
            this.autoAbortController = new AbortController();
            
            // 重置所有结果和状态
            this.resetWorkflow(false);
            
            try {
                // 依次执行所有步骤
                await this.autoStep1();
                if (!this.isAutoRunning) return;
                
                await this.autoStep2();
                if (!this.isAutoRunning) return;
                
                await this.autoStep3();
                if (!this.isAutoRunning) return;
                
                await this.autoStep4();
                if (!this.isAutoRunning) return;
                
                await this.autoStep5();
                
                // 完成
                this.autoProgress = 100;
                this.currentAutoStatus = '全部完成！🎉';
                showToast('视频生成完成！', 'success');
                
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error('Auto workflow error:', error);
                    this.currentAutoStatus = `错误: ${error.message}`;
                    showToast('自动生成过程中发生错误', 'error');
                }
            } finally {
                this.isAutoRunning = false;
            }
        },
        
        // 停止自动工作流
        stopAutoWorkflow() {
            this.isAutoRunning = false;
            this.currentAutoStatus = '已停止';
            if (this.autoAbortController) {
                this.autoAbortController.abort();
            }
            // 停止所有步骤的加载状态
            for (let i = 1; i <= 5; i++) {
                this.stepLoading[i] = false;
            }
            showToast('自动生成已停止', 'info');
        },

        // 自动步骤1: 内容生成
        async autoStep1() {
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
        },
        
        // 自动步骤2: 资源获取
        async autoStep2() {
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
        },
        
        // 自动步骤3: 语音合成
        async autoStep3() {
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
        },
        
        // 自动步骤4: 字幕生成
        async autoStep4() {
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
        },
        
        // 自动步骤5: 视频合成
        async autoStep5() {
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
        },

        // 步骤1: 内容生成
        async generateContent() {
            if (!this.config.topic.trim()) {
                showToast('请输入视频主题', 'warning');
                return;
            }
            
            this.isLoading = true;
            this.setStepStatus(1, '正在生成脚本...', true);
            
            try {
                const response = await apiRequest('/api/video/generate_content', {
                    topic: this.config.topic,
                    language: this.config.language,
                    duration: this.config.duration
                }, 'POST');
                
                this.results.content = response.data.content;
                this.currentStep = Math.max(this.currentStep, 2);
                this.setStepStatus(1, '脚本生成完成 ✓', false);
                showToast('内容生成成功！', 'success');
            } catch (error) {
                this.setStepStatus(1, '脚本生成失败 ✗', false);
                showToast('内容生成失败', 'error');
            } finally {
                this.isLoading = false;
            }
        },
        
        // 步骤2: 资源获取
        async getResources() {
            this.isLoading = true;
            this.setStepStatus(2, '正在获取资源...', true);
            
            try {
                const response = await apiRequest('/api/video/get_resources', {
                    content: this.results.content
                }, 'POST');
                
                this.results.resources = response.data.resources;
                this.currentStep = Math.max(this.currentStep, 3);
                this.setStepStatus(2, `资源获取完成 ✓ (${response.data.resources?.length || 0}个)`, false);
                showToast('资源获取成功！', 'success');
            } catch (error) {
                this.setStepStatus(2, '资源获取失败 ✗', false);
                showToast('资源获取失败', 'error');
            } finally {
                this.isLoading = false;
            }
        },
        
        // 步骤3: 语音合成
        async generateAudio() {
            this.isLoading = true;
            this.setStepStatus(3, '正在合成语音...', true);
            
            try {
                const response = await apiRequest('/api/video/generate_dubbing', {
                    content: this.results.content,
                    audio_type: this.config.audio.type,
                    voice: this.config.audio.voice,
                    audio_speed: this.config.audio.speed
                }, 'POST');
                
                this.results.audio = response.data;
                this.currentStep = Math.max(this.currentStep, 4);
                this.setStepStatus(3, '语音合成完成 ✓', false);
                showToast('语音合成成功！', 'success');
            } catch (error) {
                this.setStepStatus(3, '语音合成失败 ✗', false);
                showToast('语音合成失败', 'error');
            } finally {
                this.isLoading = false;
            }
        },
        
        // 步骤4: 字幕生成
        async generateSubtitle() {
            this.isLoading = true;
            this.setStepStatus(4, '正在生成字幕...', true);
            
            try {
                const response = await apiRequest('/api/video/generate_subtitle', {
                    audio_file: this.results.audio?.file || '',
                    content: this.results.content,
                    language: this.config.language
                }, 'POST');
                
                this.results.subtitle = response.data;
                this.currentStep = Math.max(this.currentStep, 5);
                this.setStepStatus(4, '字幕生成完成 ✓', false);
                showToast('字幕生成成功！', 'success');
            } catch (error) {
                this.setStepStatus(4, '字幕生成失败 ✗', false);
                showToast('字幕生成失败', 'error');
            } finally {
                this.isLoading = false;
            }
        },
        
        // 步骤5: 视频合成
        async generateVideo() {
            this.isLoading = true;
            this.progress = 0;
            this.setStepStatus(5, '正在合成视频...', true);
            
            // 模拟进度更新
            const progressInterval = setInterval(() => {
                if (this.progress < 90) {
                    this.progress += Math.random() * 10;
                }
            }, 500);
            
            try {
                const response = await apiRequest('/api/video/generate_final', {
                    audio_file: this.results.audio?.file || '',
                    subtitle_file: this.results.subtitle?.file || '',
                    resources: this.results.resources || [],
                    enable_subtitle: this.config.subtitle.enabled,
                    video_layout: this.config.video.layout,
                    video_fps: parseInt(this.config.video.fps),
                    enable_transition: this.config.video.enable_transition
                }, 'POST');
                
                clearInterval(progressInterval);
                this.progress = 100;
                
                this.results.video = response.data;
                this.setStepStatus(5, '视频合成完成 ✓', false);
                showToast('视频生成完成！', 'success');
            } catch (error) {
                clearInterval(progressInterval);
                this.setStepStatus(5, '视频合成失败 ✗', false);
                showToast('视频生成失败', 'error');
            } finally {
                this.isLoading = false;
            }
        },
        
        // 测试音频
        async testAudio() {
            try {
                const response = await apiRequest('/api/video/test_audio', {
                    text: '这是一个测试音频，用于预览语音效果',
                    voice_config: this.config.audio
                }, 'POST');
                
                if (response.data.audio_url) {
                    const audio = new Audio(response.data.audio_url);
                    audio.play();
                }
            } catch (error) {
                showToast('语音测试失败', 'error');
            }
        }
    };
}

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('视频生成页面脚本已加载');
});

// 导出全局函数
window.videoGeneratePage = videoGeneratePage;
window.apiRequest = apiRequest;
window.showToast = showToast;
