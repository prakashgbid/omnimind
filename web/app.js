// OSA Real-time Monitor Application

class OSAMonitor {
    constructor() {
        this.ws = null;
        this.logs = [];
        this.sessions = [];
        this.currentFilter = 'all';
        this.metrics = {
            thoughts: 0,
            chains: 0,
            contexts: 0,
            blockers: 0,
            patterns: 0,
            efficiency: 0
        };
        this.thoughtNodes = [];
        this.isConnected = false;
        
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.loadSessions();
        this.startMetricsUpdate();
        this.initThoughtGraph();
        
        // Auto-save session every 5 minutes
        setInterval(() => this.autoSaveSession(), 300000);
    }

    connectWebSocket() {
        try {
            this.ws = new WebSocket('ws://localhost:8765');
            
            this.ws.onopen = () => {
                console.log('Connected to OSA');
                this.updateStatus(true);
                this.addLog('system', 'Connected to OSA Intelligence System');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus(false);
                this.addLog('error', 'Connection error occurred');
            };

            this.ws.onclose = () => {
                console.log('Disconnected from OSA');
                this.updateStatus(false);
                this.addLog('system', 'Disconnected from OSA');
                
                // Attempt reconnection after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };
        } catch (error) {
            console.error('Failed to connect:', error);
            this.updateStatus(false);
            
            // Fallback: Generate demo data if can't connect
            this.startDemoMode();
        }
    }

    handleMessage(data) {
        switch(data.type) {
            case 'log':
                this.addLog(data.category, data.message, data.metadata);
                break;
            case 'metrics':
                this.updateMetrics(data.metrics);
                break;
            case 'thought':
                this.addThoughtNode(data.thought);
                break;
            case 'status':
                this.updateSystemStatus(data.status);
                break;
        }
    }

    addLog(type, message, metadata = {}) {
        const timestamp = new Date();
        const log = {
            id: Date.now() + Math.random(),
            type,
            message,
            timestamp,
            metadata
        };
        
        this.logs.push(log);
        this.renderLog(log);
        
        // Keep only last 1000 logs in memory
        if (this.logs.length > 1000) {
            this.logs.shift();
        }
    }

    renderLog(log) {
        const container = document.getElementById('log-container');
        
        // Check if should show based on filter
        if (this.currentFilter !== 'all' && log.type !== this.currentFilter) {
            return;
        }
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${log.type}`;
        logEntry.innerHTML = `
            <div class="log-time">${this.formatTime(log.timestamp)}</div>
            <div class="log-type ${log.type}">${log.type.toUpperCase()}</div>
            <div class="log-message">${this.formatMessage(log.message)}</div>
        `;
        
        container.appendChild(logEntry);
        
        // Auto-scroll to bottom
        container.scrollTop = container.scrollHeight;
        
        // Limit displayed logs to 100
        while (container.children.length > 100) {
            container.removeChild(container.firstChild);
        }
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3
        });
    }

    formatMessage(message) {
        // Highlight important keywords
        message = message.replace(/\b(thinking|learning|executing|blocked|alternative|pattern|confidence)\b/gi, 
            '<strong>$1</strong>');
        
        // Add emoji for certain patterns
        message = message.replace(/success/gi, '✅ $&');
        message = message.replace(/error/gi, '❌ $&');
        message = message.replace(/warning/gi, '⚠️ $&');
        
        return message;
    }

    updateMetrics(metrics) {
        this.metrics = { ...this.metrics, ...metrics };
        
        // Update UI
        document.getElementById('thoughts-count').textContent = 
            this.formatNumber(this.metrics.thoughts);
        document.getElementById('chains-count').textContent = 
            this.metrics.chains;
        document.getElementById('contexts-count').textContent = 
            this.metrics.contexts;
        document.getElementById('blockers-count').textContent = 
            this.metrics.blockers;
        document.getElementById('patterns-count').textContent = 
            this.metrics.patterns;
        document.getElementById('efficiency-value').textContent = 
            `${this.metrics.efficiency}%`;
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    updateStatus(connected) {
        this.isConnected = connected;
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.getElementById('status-text');
        
        if (connected) {
            statusDot.classList.add('active');
            statusDot.classList.remove('inactive');
            statusText.textContent = 'Connected';
        } else {
            statusDot.classList.remove('active');
            statusDot.classList.add('inactive');
            statusText.textContent = 'Disconnected';
        }
    }

    initThoughtGraph() {
        this.renderThoughtGraph();
        
        // Update graph every 2 seconds
        setInterval(() => this.renderThoughtGraph(), 2000);
    }

    renderThoughtGraph() {
        const container = document.getElementById('thought-graph');
        container.innerHTML = '';
        
        // Create sample thought nodes (would be real data from OSA)
        const nodes = this.thoughtNodes.slice(-8); // Show last 8 thoughts
        
        nodes.forEach((node, index) => {
            const element = document.createElement('div');
            element.className = 'thought-node';
            element.style.left = `${20 + (index % 3) * 100}px`;
            element.style.top = `${30 + Math.floor(index / 3) * 90}px`;
            element.innerHTML = node.label;
            element.title = node.content;
            
            container.appendChild(element);
            
            // Draw connections
            if (index > 0) {
                const connection = document.createElement('div');
                connection.className = 'thought-connection';
                
                const prevNode = nodes[index - 1];
                const x1 = 20 + ((index - 1) % 3) * 100 + 40;
                const y1 = 30 + Math.floor((index - 1) / 3) * 90 + 40;
                const x2 = parseInt(element.style.left) + 40;
                const y2 = parseInt(element.style.top) + 40;
                
                const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
                const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
                
                connection.style.left = `${x1}px`;
                connection.style.top = `${y1}px`;
                connection.style.width = `${length}px`;
                connection.style.transform = `rotate(${angle}deg)`;
                
                container.appendChild(connection);
            }
        });
    }

    addThoughtNode(thought) {
        this.thoughtNodes.push({
            id: thought.id,
            label: thought.type.substring(0, 4).toUpperCase(),
            content: thought.content,
            timestamp: new Date()
        });
        
        // Keep only last 50 thoughts
        if (this.thoughtNodes.length > 50) {
            this.thoughtNodes.shift();
        }
    }

    loadSessions() {
        const saved = localStorage.getItem('osa_sessions');
        if (saved) {
            this.sessions = JSON.parse(saved);
            this.renderSessions();
        }
    }

    renderSessions() {
        const container = document.getElementById('sessions-list');
        container.innerHTML = '';
        
        this.sessions.slice(-5).reverse().forEach(session => {
            const element = document.createElement('div');
            element.className = 'session-item';
            element.innerHTML = `
                <div class="session-info">
                    <div class="session-name">${session.name}</div>
                    <div class="session-meta">
                        ${new Date(session.timestamp).toLocaleDateString()} • 
                        ${session.logs.length} logs
                    </div>
                </div>
                <button class="btn btn-secondary" onclick="monitor.loadSession('${session.id}')">
                    Load
                </button>
            `;
            container.appendChild(element);
        });
    }

    saveSession() {
        const name = prompt('Session name:') || `Session ${new Date().toISOString()}`;
        
        const session = {
            id: Date.now().toString(),
            name,
            timestamp: new Date().toISOString(),
            logs: this.logs,
            metrics: this.metrics
        };
        
        this.sessions.push(session);
        localStorage.setItem('osa_sessions', JSON.stringify(this.sessions));
        
        this.renderSessions();
        this.showNotification('Session saved successfully');
    }

    loadSession(sessionId) {
        const session = this.sessions.find(s => s.id === sessionId);
        if (session) {
            this.logs = session.logs;
            this.metrics = session.metrics;
            
            // Re-render logs
            const container = document.getElementById('log-container');
            container.innerHTML = '';
            this.logs.forEach(log => this.renderLog(log));
            
            // Update metrics
            this.updateMetrics(this.metrics);
            
            this.showNotification(`Loaded session: ${session.name}`);
        }
    }

    autoSaveSession() {
        if (this.logs.length > 0) {
            const session = {
                id: Date.now().toString(),
                name: `Auto-save ${new Date().toLocaleTimeString()}`,
                timestamp: new Date().toISOString(),
                logs: this.logs,
                metrics: this.metrics
            };
            
            this.sessions.push(session);
            
            // Keep only last 20 sessions
            if (this.sessions.length > 20) {
                this.sessions.shift();
            }
            
            localStorage.setItem('osa_sessions', JSON.stringify(this.sessions));
        }
    }

    exportLogs() {
        const data = {
            timestamp: new Date().toISOString(),
            logs: this.logs,
            metrics: this.metrics,
            thoughtNodes: this.thoughtNodes
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], 
            { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `osa-logs-${Date.now()}.json`;
        a.click();
        
        this.showNotification('Logs exported successfully');
    }

    clearLogs() {
        if (confirm('Clear all logs? This cannot be undone.')) {
            this.logs = [];
            document.getElementById('log-container').innerHTML = '';
            this.addLog('system', 'Logs cleared');
        }
    }

    toggleFilter(filter) {
        this.currentFilter = filter;
        
        // Update UI
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Re-render logs
        const container = document.getElementById('log-container');
        container.innerHTML = '';
        this.logs.forEach(log => this.renderLog(log));
    }

    showNotification(message) {
        // Simple notification (could be replaced with a toast library)
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--accent-green);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    startMetricsUpdate() {
        // Simulate metrics updates (would be real data from OSA)
        setInterval(() => {
            if (this.isConnected) {
                this.metrics.thoughts += Math.floor(Math.random() * 10);
                this.metrics.chains += Math.floor(Math.random() * 2);
                this.metrics.contexts = Math.floor(Math.random() * 5) + 1;
                this.metrics.efficiency = Math.min(100, 
                    this.metrics.efficiency + Math.random() * 2);
                
                this.updateMetrics(this.metrics);
            }
        }, 1000);
    }

    startDemoMode() {
        console.log('Starting demo mode...');
        
        // Simulate incoming logs
        const demoMessages = [
            { type: 'thinking', message: 'Deep thinking about user goal: Build viral app' },
            { type: 'thinking', message: 'Generating reasoning chains with depth 5' },
            { type: 'learning', message: 'Pattern recognized: Similar to previous social app' },
            { type: 'executing', message: 'Spawning Claude instance for backend development' },
            { type: 'delegation', message: 'Delegating frontend to Claude_2' },
            { type: 'thinking', message: 'Identified potential blocker: API rate limits' },
            { type: 'thinking', message: 'Generated 3 alternative solutions' },
            { type: 'learning', message: 'Storing solution for future reuse' },
            { type: 'executing', message: 'Implementing authentication system' },
            { type: 'thinking', message: 'Confidence level: 87%' }
        ];
        
        let index = 0;
        setInterval(() => {
            if (!this.isConnected) {
                const msg = demoMessages[index % demoMessages.length];
                this.addLog(msg.type, msg.message);
                
                // Add thought nodes
                if (index % 3 === 0) {
                    this.addThoughtNode({
                        id: Date.now(),
                        type: msg.type,
                        content: msg.message
                    });
                }
                
                index++;
            }
        }, 2000);
    }
}

// Global instance
let monitor;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    monitor = new OSAMonitor();
});

// Global functions for HTML onclick handlers
function clearLogs() {
    monitor.clearLogs();
}

function exportLogs() {
    monitor.exportLogs();
}

function saveSession() {
    monitor.saveSession();
}

function toggleFilter(filter) {
    monitor.toggleFilter(filter);
}