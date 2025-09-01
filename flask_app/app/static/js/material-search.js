// Material Search Component
function materialSearch() {
    return {
        // Data properties
        searchQuery: '',
        selectedProvider: 'pexels',
        perPage: 15,
        searchResults: [],
        isLoading: false,
        hasSearched: false,
        selectedVideo: null,
        providers: {
            pexels: { name: 'Pexels', enabled: false },
            pixabay: { name: 'Pixabay', enabled: false }
        },
        hasConfiguredProviders: false,

        // Initialize component
        async init() {
            await this.checkProviderConfiguration();
        },

        // Check provider configuration
        async checkProviderConfiguration() {
            try {
                const response = await fetch('/material/api/config');
                const data = await response.json();
                
                if (data.success && data.providers) {
                    this.providers.pexels.enabled = data.providers.pexels?.configured || false;
                    this.providers.pixabay.enabled = data.providers.pixabay?.configured || false;
                    
                    this.hasConfiguredProviders = Object.values(this.providers).some(p => p.enabled);
                    
                    // Set default provider to first enabled one
                    const enabledProviders = Object.entries(this.providers).filter(([k, p]) => p.enabled);
                    if (enabledProviders.length > 0) {
                        this.selectedProvider = enabledProviders[0][0];
                    }
                } else {
                    this.hasConfiguredProviders = false;
                }
            } catch (error) {
                console.error('Failed to check provider configuration:', error);
                this.showNotification('Failed to check configuration', 'error');
                this.hasConfiguredProviders = false;
            }
        },

        // Perform search
        async performSearch() {
            if (!this.searchQuery.trim()) {
                this.showNotification('Please enter search keywords', 'warning');
                return;
            }

            if (!this.hasConfiguredProviders) {
                this.showNotification('Please configure API keys first', 'warning');
                return;
            }

            // Check if the selected provider is enabled
            if (!this.providers[this.selectedProvider]?.enabled) {
                this.showNotification(`${this.providers[this.selectedProvider]?.name || this.selectedProvider} is not configured`, 'warning');
                return;
            }

            this.isLoading = true;
            this.hasSearched = true;
            
            try {
                const params = new URLSearchParams({
                    query: this.searchQuery.trim(),
                    provider: this.selectedProvider,
                    per_page: this.perPage
                });

                const response = await fetch(`/material/api/search?${params}`);
                const data = await response.json();

                if (data.success && data.results) {
                    this.searchResults = data.results.map(video => ({
                        ...video,
                        downloading: false
                    }));
                    
                    if (this.searchResults.length === 0) {
                        this.showNotification('No videos found for your search', 'info');
                    } else {
                        this.showNotification(`Found ${this.searchResults.length} videos`, 'success');
                    }
                } else {
                    this.showNotification(data.error || 'Search failed', 'error');
                    this.searchResults = [];
                }
            } catch (error) {
                console.error('Search failed:', error);
                this.showNotification('Search request failed', 'error');
                this.searchResults = [];
            } finally {
                this.isLoading = false;
            }
        },

        // Download video
        async downloadVideo(video) {
            if (video.downloading) return;

            video.downloading = true;
            
            try {
                const response = await fetch('/material/api/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        video_url: video.video_url,
                        filename: this.generateFilename(video)
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.showNotification(`Video downloaded: ${data.filename}`, 'success');
                } else {
                    this.showNotification(data.error || 'Download failed', 'error');
                }
            } catch (error) {
                console.error('Download failed:', error);
                this.showNotification('Download request failed', 'error');
            } finally {
                video.downloading = false;
            }
        },

        // Preview video
        previewVideo(video) {
            this.selectedVideo = video;
            const modal = new bootstrap.Modal(document.getElementById('previewModal'));
            modal.show();
        },

        // Clear results
        clearResults() {
            this.searchResults = [];
            this.hasSearched = false;
            this.searchQuery = '';
        },

        // Generate filename for download
        generateFilename(video) {
            const sanitizedTitle = video.title
                .replace(/[^a-zA-Z0-9\s-_]/g, '')
                .replace(/\s+/g, '_')
                .substring(0, 50);
            
            const timestamp = Date.now();
            return `${video.provider}_${sanitizedTitle}_${timestamp}.mp4`;
        },

        // Show notification
        showNotification(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
            notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            
            const iconMap = {
                success: 'bi-check-circle',
                error: 'bi-exclamation-triangle',
                warning: 'bi-exclamation-triangle',
                info: 'bi-info-circle'
            };

            notification.innerHTML = `
                <i class="bi ${iconMap[type] || iconMap.info} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            document.body.appendChild(notification);

            // Auto remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        },

        // Get Bootstrap alert class
        getBootstrapAlertClass(type) {
            const classMap = {
                success: 'success',
                error: 'danger',
                warning: 'warning',
                info: 'info'
            };
            return classMap[type] || 'info';
        }
    };
}

// Export for use in templates
if (typeof module !== 'undefined' && module.exports) {
    module.exports = materialSearch;
}
