// Niflheim-X Demo Page Interactions

// Utility function for HTML escaping
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

class DemoManager {
    constructor() {
        this.currentDemo = 'chat';
        this.activeConnections = new Map();
        this.apiClient = null;
        this.init();
    }

    init() {
        // Wait for apiClient to be available
        this.waitForApiClient().then(() => {
            this.setupChatDemo();
            this.setupToolDemo();
            this.setupMemoryDemo();
            this.setupMultiAgentDemo();
            this.setupStreamingDemo();
            this.setupTabNavigation();
            
            console.log('🎮 Demo Manager Initialized');
        });
    }

    async waitForApiClient() {
        // Wait for global apiClient to be available
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds max wait
        
        while (!window.apiClient && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (!window.apiClient) {
            console.error('❌ ApiClient not available after 5 seconds, creating fallback');
            // Create fallback ApiClient if window.ApiClient constructor is available
            if (window.ApiClient) {
                window.apiClient = new window.ApiClient();
            } else {
                // Create a minimal fallback
                window.apiClient = {
                    chat: async (message) => ({ success: false, error: 'ApiClient not ready' }),
                    toolDemo: async (task) => ({ success: false, error: 'ApiClient not ready' }),
                    memoryDemo: async (message) => ({ success: false, error: 'ApiClient not ready' }),
                    multiAgentDemo: async (topic) => ({ success: false, error: 'ApiClient not ready' }),
                    getFrameworkInfo: async () => ({ success: false, error: 'ApiClient not ready' }),
                    setupEventSource: () => null
                };
            }
        }
        
        this.apiClient = window.apiClient;
        console.log('✅ ApiClient ready for demos');
    }

    setupTabNavigation() {
        // Track active demo for metrics
        document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetId = e.target.getAttribute('href').substring(1);
                const demoName = this.getDemoName(targetId);
                if (app) {
                    app.setActiveDemo(demoName);
                }
            });
        });
    }

    getDemoName(tabId) {
        const names = {
            'chat-demo': 'Smart Chat',
            'tools-demo': 'Tool Integration', 
            'memory-demo': 'Memory Systems',
            'multi-agent-demo': 'Multi-Agent',
            'streaming-demo': 'Streaming'
        };
        return names[tabId] || 'Demo';
    }

    // Chat Demo Implementation
    setupChatDemo() {
        const chatInput = document.getElementById('chatInput');
        const chatSend = document.getElementById('chatSend');
        const chatMessages = document.getElementById('chatMessages');
        const chatStatus = document.getElementById('chatStatus');

        if (!chatInput || !chatSend) return;

        const sendMessage = async () => {
            const message = chatInput.value.trim();
            if (!message) return;

            this.addChatMessage(message, 'user');
            chatInput.value = '';
            chatSend.disabled = true;
            chatStatus.textContent = 'Thinking...';

            try {
                const result = await this.apiClient.chat(message);
                
                if (result.success) {
                    this.addChatMessage(result.data.response, 'bot');
                    chatStatus.textContent = `Response received at ${app.formatTimestamp(result.data.timestamp)}`;
                } else {
                    this.addChatMessage(`Error: ${result.error}`, 'bot', true);
                    chatStatus.textContent = 'Failed to get response';
                }
            } catch (error) {
                this.addChatMessage(`Error: ${error.message}`, 'bot', true);
                chatStatus.textContent = 'Connection error';
            }

            chatSend.disabled = false;
        };

        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    addChatMessage(content, type, isError = false) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'user' 
            ? '<i class="fas fa-user"></i>' 
            : '<i class="fas fa-robot"></i>';

        const content_div = document.createElement('div');
        content_div.className = 'message-content';
        if (isError) {
            content_div.style.color = '#dc3545';
            content_div.style.fontStyle = 'italic';
        }
        content_div.innerHTML = `<strong>${type === 'user' ? 'You' : 'Niflheim Agent'}:</strong> ${escapeHtml(content)}`;

        const time_div = document.createElement('div');
        time_div.className = 'message-time';
        time_div.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content_div);
        messageDiv.appendChild(time_div);

        chatMessages.appendChild(messageDiv);
        
        // Add animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Tool Demo Implementation
    setupToolDemo() {
        const toolInput = document.getElementById('toolInput');
        const toolSend = document.getElementById('toolSend');
        const toolOutput = document.getElementById('toolOutput');
        const toolResult = document.getElementById('toolResult');

        if (!toolInput || !toolSend) return;

        const executeTask = async () => {
            const task = toolInput.value.trim();
            if (!task) return;

            toolSend.disabled = true;
            toolSend.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
            toolOutput.style.display = 'none';

            try {
                const result = await this.apiClient.toolDemo(task);
                
                if (result.success) {
                    toolResult.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <strong>Task:</strong> ${escapeHtml(task)}
                        </div>
                        <div class="alert alert-success mb-0">
                            <i class="fas fa-check-circle me-2"></i>
                            ${escapeHtml(result.data.response)}
                        </div>
                    `;
                } else {
                    toolResult.innerHTML = `
                        <div class="alert alert-danger mb-0">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error: ${escapeHtml(result.error)}
                        </div>
                    `;
                }
                
                toolOutput.style.display = 'block';
                AnimationUtils.fadeIn(toolOutput);
                
            } catch (error) {
                toolResult.innerHTML = `
                    <div class="alert alert-danger mb-0">
                        <i class="fas fa-times-circle me-2"></i>
                        Connection error: ${escapeHtml(error.message)}
                    </div>
                `;
                toolOutput.style.display = 'block';
            }

            toolSend.disabled = false;
            toolSend.innerHTML = '<i class="fas fa-cog me-1"></i>Execute';
        };

        toolSend.addEventListener('click', executeTask);
        toolInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') executeTask();
        });

        // Quick example buttons
        document.querySelectorAll('.tool-example').forEach(btn => {
            btn.addEventListener('click', (e) => {
                toolInput.value = e.target.dataset.example;
            });
        });
    }

    // Memory Demo Implementation
    setupMemoryDemo() {
        const memoryInput = document.getElementById('memoryInput');
        const memorySend = document.getElementById('memorySend');
        const memoryOutput = document.getElementById('memoryOutput');
        const memoryResult = document.getElementById('memoryResult');
        const memoryItems = document.getElementById('memoryItems');

        if (!memoryInput || !memorySend) return;

        let storedMemories = [];

        const storeMemory = async () => {
            const message = memoryInput.value.trim();
            if (!message) return;

            memorySend.disabled = true;
            memorySend.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Storing...';

            try {
                const result = await this.apiClient.memoryDemo(message);
                
                if (result.success) {
                    storedMemories.push(message);
                    this.updateMemoryDisplay(storedMemories);
                    
                    memoryResult.innerHTML = `
                        <div class="alert alert-success mb-0">
                            <i class="fas fa-brain me-2"></i>
                            ${escapeHtml(result.data.response)}
                        </div>
                    `;
                } else {
                    memoryResult.innerHTML = `
                        <div class="alert alert-danger mb-0">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error: ${escapeHtml(result.error)}
                        </div>
                    `;
                }
                
                memoryOutput.style.display = 'block';
                AnimationUtils.fadeIn(memoryOutput);
                
            } catch (error) {
                memoryResult.innerHTML = `
                    <div class="alert alert-danger mb-0">
                        <i class="fas fa-times-circle me-2"></i>
                        Error: ${escapeHtml(error.message)}
                    </div>
                `;
                memoryOutput.style.display = 'block';
            }

            memorySend.disabled = false;
            memorySend.innerHTML = '<i class="fas fa-brain me-1"></i>Remember';
        };

        memorySend.addEventListener('click', storeMemory);
        memoryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') storeMemory();
        });

        // Memory test buttons
        document.querySelectorAll('.memory-test').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const question = e.target.dataset.question;
                try {
                    const result = await this.apiClient.memoryDemo(question);
                    if (result.success) {
                        memoryResult.innerHTML = `
                            <div class="alert alert-info mb-0">
                                <strong>Q:</strong> ${escapeHtml(question)}<br>
                                <strong>A:</strong> ${escapeHtml(result.data.response)}
                            </div>
                        `;
                        memoryOutput.style.display = 'block';
                    }
                } catch (error) {
                    console.error('Memory test failed:', error);
                }
            });
        });
    }

    updateMemoryDisplay(memories) {
        const memoryItems = document.getElementById('memoryItems');
        if (!memoryItems) return;

        if (memories.length === 0) {
            memoryItems.innerHTML = '<small class="text-muted">No memories stored yet...</small>';
            return;
        }

        memoryItems.innerHTML = memories.map((memory, index) => `
            <div class="memory-item border rounded p-2 mb-2">
                <small class="text-muted">#${index + 1}</small>
                <div>${escapeHtml(memory)}</div>
            </div>
        `).join('');
    }

    // Multi-Agent Demo Implementation
    setupMultiAgentDemo() {
        const multiAgentInput = document.getElementById('multiAgentInput');
        const multiAgentSend = document.getElementById('multiAgentSend');
        const multiAgentOutput = document.getElementById('multiAgentOutput');
        const collaborationResult = document.getElementById('collaborationResult');

        if (!multiAgentInput || !multiAgentSend) return;

        const collaborateAgents = async () => {
            const topic = multiAgentInput.value.trim();
            if (!topic) return;

            multiAgentSend.disabled = true;
            multiAgentSend.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Collaborating...';
            
            // Animate agent status
            this.animateAgentProgress();

            try {
                const result = await this.apiClient.multiAgentDemo(topic);
                
                if (result.success) {
                    collaborationResult.innerHTML = `
                        <div class="card">
                            <div class="card-header">
                                <strong>Topic:</strong> ${escapeHtml(topic)}
                            </div>
                            <div class="card-body">
                                <div class="alert alert-success">
                                    <i class="fas fa-users me-2"></i>
                                    ${escapeHtml(result.data.response)}
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Mark all agents as complete
                    this.setAgentsStatus('complete');
                } else {
                    collaborationResult.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error: ${escapeHtml(result.error)}
                        </div>
                    `;
                    this.setAgentsStatus('waiting');
                }
                
                multiAgentOutput.style.display = 'block';
                AnimationUtils.fadeIn(multiAgentOutput);
                
            } catch (error) {
                collaborationResult.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-times-circle me-2"></i>
                        Error: ${escapeHtml(error.message)}
                    </div>
                `;
                multiAgentOutput.style.display = 'block';
                this.setAgentsStatus('waiting');
            }

            multiAgentSend.disabled = false;
            multiAgentSend.innerHTML = '<i class="fas fa-users me-1"></i>Collaborate';
        };

        multiAgentSend.addEventListener('click', collaborateAgents);
        multiAgentInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') collaborateAgents();
        });

        // Task example buttons
        document.querySelectorAll('.task-example').forEach(btn => {
            btn.addEventListener('click', (e) => {
                multiAgentInput.value = e.target.dataset.task;
            });
        });
    }

    animateAgentProgress() {
        const agents = ['researcherAgent', 'writerAgent', 'reviewerAgent'];
        
        // Reset all agents
        this.setAgentsStatus('waiting');
        
        // Animate progress
        agents.forEach((agentId, index) => {
            setTimeout(() => {
                this.setAgentStatus(agentId, 'working');
            }, index * 1000);
            
            setTimeout(() => {
                this.setAgentStatus(agentId, 'complete');
            }, (index + 1) * 1500);
        });
    }

    setAgentStatus(agentId, status) {
        const agent = document.getElementById(agentId);
        if (!agent) return;

        const statusElement = agent.querySelector('.agent-status');
        if (statusElement) {
            statusElement.className = `agent-status ${status}`;
        }
    }

    setAgentsStatus(status) {
        ['researcherAgent', 'writerAgent', 'reviewerAgent'].forEach(agentId => {
            this.setAgentStatus(agentId, status);
        });
    }

    // Streaming Demo Implementation
    setupStreamingDemo() {
        const streamInput = document.getElementById('streamInput');
        const streamSend = document.getElementById('streamSend');
        const streamContent = document.getElementById('streamContent');
        const streamProgress = document.getElementById('streamProgress');
        const streamStatus = document.getElementById('streamStatus');
        const streamIndicator = document.getElementById('streamIndicator');

        if (!streamInput || !streamSend) return;

        const startStreaming = async () => {
            const message = streamInput.value.trim();
            if (!message) return;

            streamSend.disabled = true;
            streamSend.innerHTML = '<i class="fas fa-stop me-1"></i>Streaming...';
            streamContent.textContent = '';
            streamProgress.style.width = '0%';
            streamStatus.textContent = 'Connecting...';
            streamIndicator.classList.add('active');

            try {
                const url = `/api/stream_demo?message=${encodeURIComponent(message)}`;
                let eventSource = this.apiClient.setupEventSource(url, 
                    (data) => this.handleStreamData(data),
                    (error) => this.handleStreamError(error)
                );

                // Store reference for cleanup
                this.activeConnections.set('stream', eventSource);

            } catch (error) {
                this.handleStreamError(error);
            }
        };

        streamSend.addEventListener('click', startStreaming);
        streamInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') startStreaming();
        });
    }

    handleStreamData(data) {
        const streamContent = document.getElementById('streamContent');
        const streamProgress = document.getElementById('streamProgress');
        const streamStatus = document.getElementById('streamStatus');
        const streamIndicator = document.getElementById('streamIndicator');
        const streamSend = document.getElementById('streamSend');

        if (data.error) {
            streamContent.textContent += `\nError: ${data.error}`;
            streamStatus.textContent = 'Stream error';
            this.resetStreamingUI();
            return;
        }

        if (data.done) {
            streamStatus.textContent = 'Stream completed';
            streamProgress.style.width = '100%';
            this.resetStreamingUI();
            return;
        }

        if (data.word) {
            streamContent.textContent += data.word + ' ';
            streamProgress.style.width = `${data.progress}%`;
            streamStatus.textContent = `Streaming... ${Math.round(data.progress)}%`;
            
            // Auto-scroll to bottom
            streamContent.scrollTop = streamContent.scrollHeight;
        }
        
        if (data.chunk) {
            streamContent.textContent += data.chunk;
            streamStatus.textContent = 'Streaming...';
            
            // Auto-scroll to bottom
            streamContent.scrollTop = streamContent.scrollHeight;
        }
    }

    handleStreamError(error) {
        const streamContent = document.getElementById('streamContent');
        const streamStatus = document.getElementById('streamStatus');
        
        streamContent.textContent += `\nConnection error: ${error.message || 'Unknown error'}`;
        streamStatus.textContent = 'Connection failed';
        this.resetStreamingUI();
    }

    resetStreamingUI() {
        const streamSend = document.getElementById('streamSend');
        const streamIndicator = document.getElementById('streamIndicator');

        if (streamSend) {
            streamSend.disabled = false;
            streamSend.innerHTML = '<i class="fas fa-play me-1"></i>Stream';
        }

        if (streamIndicator) {
            streamIndicator.classList.remove('active');
        }

        // Clean up connections
        const connection = this.activeConnections.get('stream');
        if (connection) {
            connection.close();
            this.activeConnections.delete('stream');
        }
    }

    // Cleanup method
    cleanup() {
        this.activeConnections.forEach(connection => {
            if (connection.close) connection.close();
        });
        this.activeConnections.clear();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.demoManager = new DemoManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.demoManager) {
        window.demoManager.cleanup();
    }
});
