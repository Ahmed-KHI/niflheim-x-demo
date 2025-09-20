// Niflheim-X Demo Application JavaScript

class ApiClient {
    constructor() {
        this.baseUrl = '';
        this.timeout = 30000; // 30 seconds
    }

    async makeRequest(endpoint, options = {}) {
        const startTime = Date.now();
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(this.baseUrl + endpoint, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            const responseTime = Date.now() - startTime;
            
            return {
                success: true,
                data: data,
                responseTime: responseTime
            };
            
        } catch (error) {
            const responseTime = Date.now() - startTime;
            return {
                success: false,
                error: error.message,
                responseTime: responseTime
            };
        }
    }

    async chat(message) {
        return this.makeRequest('/api/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }

    async toolDemo(task) {
        return this.makeRequest('/api/tool_demo', {
            method: 'POST',
            body: JSON.stringify({ task })
        });
    }

    async memoryDemo(message) {
        return this.makeRequest('/api/memory_demo', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }

    async multiAgentDemo(topic) {
        return this.makeRequest('/api/multi_agent_demo', {
            method: 'POST',
            body: JSON.stringify({ topic })
        });
    }

    async getFrameworkInfo() {
        return this.makeRequest('/api/framework_info');
    }

    setupEventSource(url, onMessage, onError) {
        try {
            const eventSource = new EventSource(url);
            
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    onMessage(data);
                } catch (e) {
                    console.error('Failed to parse SSE data:', e);
                }
            };
            
            eventSource.onerror = function(event) {
                console.error('EventSource error:', event);
                eventSource.close();
                onError(new Error('Connection lost'));
            };
            
            return eventSource;
        } catch (error) {
            onError(error);
            return null;
        }
    }
}

class NiflheimDemo {
    constructor() {
        this.metrics = {
            totalRequests: 0,
            successCount: 0,
            responseTimes: [],
            currentDemo: 'Chat'
        };
        this.init();
        this.setupEventListeners();
    }

    init() {
        console.log('🚀 Niflheim-X Demo App Initialized');
        this.updateMetrics();
        this.showWelcomeAnimation();
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add loading states to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', function() {
                if (!this.classList.contains('loading')) {
                    this.classList.add('loading');
                    setTimeout(() => {
                        this.classList.remove('loading');
                    }, 2000);
                }
            });
        });

        // Performance monitoring
        this.setupPerformanceMonitoring();
    }

    showWelcomeAnimation() {
        // Add entrance animation to hero elements
        const heroElements = document.querySelectorAll('.hero-content > *');
        heroElements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                el.style.transition = 'all 0.6s ease';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, index * 200);
        });
    }

    setupPerformanceMonitoring() {
        // Monitor API calls and update metrics
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();
            
            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();
                
                this.updatePerformanceMetrics(endTime - startTime, response.ok);
                return response;
            } catch (error) {
                const endTime = performance.now();
                this.updatePerformanceMetrics(endTime - startTime, false);
                throw error;
            }
        };
    }

    updatePerformanceMetrics(responseTime, success) {
        this.metrics.totalRequests++;
        this.metrics.responseTimes.push(responseTime);
        
        if (success) {
            this.metrics.successCount++;
        }

        // Keep only last 10 response times for average
        if (this.metrics.responseTimes.length > 10) {
            this.metrics.responseTimes.shift();
        }

        this.updateMetrics();
    }

    updateMetrics() {
        const avgTime = this.metrics.responseTimes.length > 0 
            ? Math.round(this.metrics.responseTimes.reduce((a, b) => a + b, 0) / this.metrics.responseTimes.length)
            : 0;
        
        const successRate = this.metrics.totalRequests > 0 
            ? Math.round((this.metrics.successCount / this.metrics.totalRequests) * 100)
            : 100;

        // Update UI elements if they exist
        const avgResponseTimeEl = document.getElementById('avgResponseTime');
        const totalRequestsEl = document.getElementById('totalRequests');
        const successRateEl = document.getElementById('successRate');
        const activeDemoEl = document.getElementById('activeDemo');

        if (avgResponseTimeEl) avgResponseTimeEl.textContent = `${avgTime}ms`;
        if (totalRequestsEl) totalRequestsEl.textContent = this.metrics.totalRequests;
        if (successRateEl) successRateEl.textContent = `${successRate}%`;
        if (activeDemoEl) activeDemoEl.textContent = this.metrics.currentDemo;
    }

    setActiveDemo(demoName) {
        this.metrics.currentDemo = demoName;
        this.updateMetrics();
    }

    // Utility methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 80px; right: 20px; z-index: 1050; max-width: 400px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    async makeApiCall(endpoint, data = {}, method = 'POST') {
        try {
            const response = await fetch(endpoint, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: method !== 'GET' ? JSON.stringify(data) : undefined
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, data: result };
        } catch (error) {
            console.error('API call failed:', error);
            return { success: false, error: error.message };
        }
    }

    formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleTimeString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Animation Utilities
class AnimationUtils {
    static typeWriter(element, text, speed = 50) {
        element.textContent = '';
        let i = 0;
        
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }

    static fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.opacity = Math.min(progress / duration, 1);
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }

    static slideIn(element, direction = 'left', duration = 300) {
        const startTransform = direction === 'left' ? 'translateX(-100px)' : 'translateX(100px)';
        
        element.style.transform = startTransform;
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            const ease = Math.min(progress / duration, 1);
            
            element.style.transform = `translateX(${(1 - ease) * (direction === 'left' ? -100 : 100)}px)`;
            element.style.opacity = ease;
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }
}

// Initialize app when DOM is loaded
let app, apiClient;

document.addEventListener('DOMContentLoaded', function() {
    app = new NiflheimDemo();
    apiClient = new ApiClient();
    window.apiClient = apiClient;  // Make apiClient globally available
    
    // Initialize framework info display
    loadFrameworkInfo();
    
    // Setup intersection observer for animations
    setupScrollAnimations();
});

async function loadFrameworkInfo() {
    try {
        const result = await apiClient.getFrameworkInfo();
        if (result.success) {
            console.log('Framework info loaded:', result.data);
        }
    } catch (error) {
        console.error('Failed to load framework info:', error);
    }
}

function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                
                // Add staggered animation for child elements
                const children = entry.target.querySelectorAll('.feature-card, .demo-card, .stat-card');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.style.opacity = '1';
                        child.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.features-section, .demo-teasers, .comparison-section').forEach(section => {
        observer.observe(section);
    });
}

// Export for use in other files
window.NiflheimDemo = NiflheimDemo;
window.ApiClient = ApiClient;
window.AnimationUtils = AnimationUtils;