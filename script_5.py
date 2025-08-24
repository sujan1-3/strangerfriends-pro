# Create the main application file with real functionality
app_js_real_content = '''// StrangerFriends - Real-world Application with WebRTC Integration
class StrangerFriendsApp {
    constructor() {
        this.socket = null;
        this.webrtc = null;
        this.currentScreen = 'hero';
        this.userCountry = null;
        this.partnerCountry = null;
        this.chatStartTime = null;
        this.chatTimer = null;
        this.stats = {
            activeUsers: 0,
            totalConnections: 0,
            activeRooms: 0,
            waitingUsers: 0
        };
        
        // App state
        this.isConnected = false;
        this.isMediaInitialized = false;
        this.preferences = {
            gender: 'both',
            preference: 'both'
        };

        this.init();
    }

    async init() {
        console.log('🚀 Initializing StrangerFriends App...');
        
        // Show loading screen
        this.showLoadingScreen();
        
        try {
            // Check browser support
            await this.checkBrowserSupport();
            
            // Initialize Socket.IO connection
            await this.initializeSocket();
            
            // Initialize WebRTC manager
            this.initializeWebRTC();
            
            // Bind UI events
            this.bindUIEvents();
            
            // Load user stats
            this.loadStats();
            
            // Hide loading screen and show hero
            setTimeout(() => {
                this.hideLoadingScreen();
                this.showHeroSection();
            }, 2000);
            
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError('Failed to initialize application. Please refresh the page.');
        }
    }

    async checkBrowserSupport() {
        const support = {
            webRTC: !!(window.RTCPeerConnection),
            getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            webSocket: !!(window.WebSocket),
            socketIO: !!(window.io)
        };

        console.log('Browser support:', support);

        const unsupported = Object.entries(support)
            .filter(([key, value]) => !value)
            .map(([key]) => key);

        if (unsupported.length > 0) {
            throw new Error(`Unsupported features: ${unsupported.join(', ')}`);
        }
    }

    async initializeSocket() {
        return new Promise((resolve, reject) => {
            console.log('🔌 Connecting to server...');
            
            const serverUrl = window.location.origin;
            this.socket = io(serverUrl, {
                transports: ['websocket', 'polling'],
                timeout: 10000,
                forceNew: true
            });

            this.socket.on('connect', () => {
                console.log('✅ Connected to server');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                resolve();
            });

            this.socket.on('disconnect', (reason) => {
                console.log('❌ Disconnected from server:', reason);
                this.isConnected = false;
                this.updateConnectionStatus(false);
                
                if (reason === 'io server disconnect') {
                    // Reconnect manually
                    this.socket.connect();
                }
            });

            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
                reject(error);
            });

            // WebRTC signaling events
            this.setupSocketEvents();
        });
    }

    setupSocketEvents() {
        this.socket.on('waiting-for-match', () => {
            console.log('⏳ Waiting for match...');
            this.showWaitingScreen();
        });

        this.socket.on('match-found', (data) => {
            console.log('🎯 Match found!', data);
            this.partnerCountry = data.partner.country;
            this.startVideoChat();
        });

        this.socket.on('partner-left', (data) => {
            console.log('👋 Partner left:', data.reason);
            this.handlePartnerLeft(data.reason);
        });

        this.socket.on('report-submitted', () => {
            this.showNotification('Report submitted successfully', 'success');
            this.closeModal(document.getElementById('report-modal'));
        });
    }

    initializeWebRTC() {
        console.log('🎥 Initializing WebRTC...');
        this.webrtc = new WebRTCManager();
        this.webrtc.setSocket(this.socket);

        // WebRTC event handlers
        this.webrtc.on('country-detected', (country) => {
            console.log('🌍 Country detected:', country);
            this.userCountry = country;
            this.displayUserCountry(country);
        });

        this.webrtc.on('media-initialized', () => {
            console.log('📹 Media initialized');
            this.isMediaInitialized = true;
            this.hideVideoPlaceholder('local');
        });

        this.webrtc.on('remote-stream', () => {
            console.log('📺 Remote stream received');
            this.hideVideoPlaceholder('remote');
            this.updateConnectionIndicator('connected');
        });

        this.webrtc.on('peer-connected', () => {
            console.log('🤝 Peer connected');
            this.updateConnectionIndicator('connected');
        });

        this.webrtc.on('peer-disconnected', () => {
            console.log('💔 Peer disconnected');
            this.updateConnectionIndicator('disconnected');
        });

        this.webrtc.on('match-found', () => {
            // Start the call immediately when match is found
            setTimeout(() => {
                this.webrtc.startCall();
            }, 1000);
        });

        this.webrtc.on('media-error', (error) => {
            console.error('Media error:', error);
            this.showPermissionModal();
        });
    }

    bindUIEvents() {
        // Hero section
        const startBtn = document.getElementById('start-chatting-btn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.showGenderSelection());
        }

        // Gender selection
        document.querySelectorAll('.gender-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectGender(e.target.closest('.gender-btn')));
        });

        // Navigation buttons
        const backBtn = document.getElementById('back-to-home');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showHeroSection());
        }

        const cancelBtn = document.getElementById('cancel-waiting');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.showGenderSelection());
        }

        // Video controls
        this.bindVideoControls();

        // Modal controls
        this.bindModalControls();

        // Stats and safety buttons
        const statsBtn = document.getElementById('stats-btn');
        if (statsBtn) {
            statsBtn.addEventListener('click', () => this.showStatsModal());
        }

        const safetyBtn = document.getElementById('safety-btn');
        if (safetyBtn) {
            safetyBtn.addEventListener('click', () => this.showSafetyModal());
        }

        // Permission modal
        const grantPermissionBtn = document.getElementById('grant-permission');
        if (grantPermissionBtn) {
            grantPermissionBtn.addEventListener('click', () => this.requestPermissions());
        }
    }

    bindVideoControls() {
        const micBtn = document.getElementById('toggle-mic');
        if (micBtn) {
            micBtn.addEventListener('click', () => this.toggleMicrophone());
        }

        const cameraBtn = document.getElementById('toggle-camera');
        if (cameraBtn) {
            cameraBtn.addEventListener('click', () => this.toggleCamera());
        }

        const nextBtn = document.getElementById('next-stranger');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.findNextUser());
        }

        const disconnectBtn = document.getElementById('disconnect-chat');
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', () => this.endChat());
        }

        const reportBtn = document.getElementById('report-user');
        if (reportBtn) {
            reportBtn.addEventListener('click', () => this.showReportModal());
        }
    }

    bindModalControls() {
        // Close modal buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close')) {
                this.closeModal(e.target.closest('.modal'));
            }
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Report options
        document.querySelectorAll('.report-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const reason = e.target.dataset.reason;
                this.submitReport(reason);
            });
        });
    }

    // Screen Management
    showLoadingScreen() {
        document.getElementById('loading-screen').style.display = 'flex';
    }

    hideLoadingScreen() {
        document.getElementById('loading-screen').style.display = 'none';
    }

    showHeroSection() {
        this.switchScreen('hero-section');
        this.currentScreen = 'hero';
    }

    showGenderSelection() {
        this.switchScreen('gender-selection');
        this.currentScreen = 'gender-selection';
    }

    showWaitingScreen() {
        this.switchScreen('waiting-screen');
        this.currentScreen = 'waiting';
    }

    startVideoChat() {
        this.switchScreen('video-chat');
        this.currentScreen = 'video-chat';
        this.startChatTimer();
        
        // Initialize media and start call
        this.webrtc.answerCall();
    }

    switchScreen(targetScreen) {
        // Hide all screens
        document.querySelectorAll('.screen, .hero-section').forEach(screen => {
            screen.style.display = 'none';
            screen.classList.remove('active');
        });

        // Show target screen
        const screen = document.getElementById(targetScreen);
        if (screen) {
            screen.style.display = 'flex';
            setTimeout(() => screen.classList.add('active'), 50);
        }
    }

    // User Interactions
    selectGender(btn) {
        // Update UI
        document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        // Get preferences
        this.preferences.gender = btn.dataset.gender || 'both';
        this.preferences.preference = btn.dataset.preference || 'both';

        console.log('Gender preferences set:', this.preferences);

        // Auto-advance after selection
        setTimeout(() => {
            this.startMatching();
        }, 1000);
    }

    async startMatching() {
        console.log('🔍 Starting matching process...');
        
        // Request media permissions first
        try {
            await this.webrtc.initializeMedia();
        } catch (error) {
            console.error('Media permission error:', error);
            this.showPermissionModal();
            return;
        }

        // Send preferences to server
        this.socket.emit('set-preferences', this.preferences);
        
        // Show waiting screen
        this.showWaitingScreen();
    }

    toggleMicrophone() {
        if (this.webrtc) {
            const enabled = this.webrtc.toggleMicrophone();
            this.updateControlButton('toggle-mic', enabled, '🎤', 'Mic', 'Muted');
        }
    }

    toggleCamera() {
        if (this.webrtc) {
            const enabled = this.webrtc.toggleCamera();
            this.updateControlButton('toggle-camera', enabled, '📹', 'Camera', 'Off');
        }
    }

    findNextUser() {
        console.log('🔄 Finding next user...');
        this.endChat();
        this.socket.emit('next-user');
        this.showWaitingScreen();
    }

    endChat() {
        console.log('📞 Ending chat...');
        
        if (this.webrtc) {
            this.webrtc.endCall();
        }

        if (this.chatTimer) {
            clearInterval(this.chatTimer);
            this.chatTimer = null;
        }

        this.resetVideoElements();
        this.showGenderSelection();
    }

    // UI Updates
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        const statusDot = statusElement.querySelector('.status-dot');
        const statusText = statusElement.querySelector('.status-text');

        if (connected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'Connecting...';
        }
    }

    updateConnectionIndicator(state) {
        const indicator = document.getElementById('connection-indicator');
        if (indicator) {
            switch (state) {
                case 'connected':
                    indicator.textContent = '🟢 Connected';
                    indicator.className = 'connection-indicator connected';
                    break;
                case 'connecting':
                    indicator.textContent = '🟡 Connecting...';
                    indicator.className = 'connection-indicator connecting';
                    break;
                case 'disconnected':
                    indicator.textContent = '🔴 Disconnected';
                    indicator.className = 'connection-indicator disconnected';
                    break;
            }
        }
    }

    updateControlButton(buttonId, enabled, icon, enabledText, disabledText) {
        const button = document.getElementById(buttonId);
        if (button) {
            const iconSpan = button.querySelector('.btn-icon');
            const labelSpan = button.querySelector('.btn-label');
            
            if (enabled) {
                button.classList.add('active');
                labelSpan.textContent = enabledText;
            } else {
                button.classList.remove('active');
                labelSpan.textContent = disabledText;
            }
            
            iconSpan.textContent = icon;
        }
    }

    displayUserCountry(country) {
        const userLocation = document.getElementById('user-location');
        const userFlag = document.getElementById('user-flag');
        const userCountryName = document.getElementById('user-country');
        const localFlag = document.getElementById('local-flag');
        const localCountryName = document.getElementById('local-country-name');

        if (userFlag) userFlag.textContent = country.flag;
        if (userCountryName) userCountryName.textContent = country.name;
        if (localFlag) localFlag.textContent = country.flag;
        if (localCountryName) localCountryName.textContent = country.name;

        if (userLocation) {
            userLocation.style.display = 'block';
        }
    }

    hideVideoPlaceholder(type) {
        const placeholder = document.getElementById(`${type}-placeholder`);
        if (placeholder) {
            placeholder.style.display = 'none';
        }
    }

    resetVideoElements() {
        const placeholders = ['local-placeholder', 'remote-placeholder'];
        placeholders.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'flex';
        });

        const videos = ['localVideo', 'remoteVideo'];
        videos.forEach(id => {
            const video = document.getElementById(id);
            if (video) video.srcObject = null;
        });
    }

    startChatTimer() {
        this.chatStartTime = Date.now();
        this.chatTimer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.chatStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const seconds = (elapsed % 60).toString().padStart(2, '0');
            
            const timerElement = document.getElementById('chat-timer');
            if (timerElement) {
                timerElement.textContent = `${minutes}:${seconds}`;
            }
        }, 1000);
    }

    // Modal Management
    showStatsModal() {
        this.loadStats();
        document.getElementById('stats-modal').style.display = 'flex';
    }

    showSafetyModal() {
        document.getElementById('safety-modal').style.display = 'flex';
    }

    showReportModal() {
        document.getElementById('report-modal').style.display = 'flex';
    }

    showPermissionModal() {
        document.getElementById('permission-modal').style.display = 'flex';
    }

    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // API Calls
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatsDisplay(stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        const elements = {
            'stat-active-users': stats.activeUsers,
            'stat-total-connections': stats.totalConnections,
            'stat-active-rooms': stats.activeRooms,
            'stat-waiting-users': stats.waitingUsers,
            'user-count': stats.activeUsers
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value.toLocaleString();
            }
        });
    }

    async requestPermissions() {
        try {
            await this.webrtc.initializeMedia();
            this.closeModal(document.getElementById('permission-modal'));
            this.showNotification('Permissions granted successfully', 'success');
        } catch (error) {
            this.showNotification('Please allow camera and microphone access', 'error');
        }
    }

    submitReport(reason) {
        if (this.webrtc && this.webrtc.currentRoomId) {
            this.socket.emit('report-user', {
                roomId: this.webrtc.currentRoomId,
                reason: reason
            });
        }
    }

    // Event Handlers
    handlePartnerLeft(reason) {
        let message = 'Your partner has left the chat';
        
        switch (reason) {
            case 'next':
                message = 'Your partner found a new chat';
                break;
            case 'disconnect':
                message = 'Your partner disconnected';
                break;
            case 'report':
                message = 'Chat ended due to report';
                break;
        }

        this.showNotification(message, 'info');
        this.endChat();
    }

    // Utility Methods
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    showError(message) {
        this.showNotification(message, 'error');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌍 Starting StrangerFriends...');
    window.strangerFriends = new StrangerFriendsApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.strangerFriends && window.strangerFriends.webrtc) {
        if (document.hidden) {
            console.log('📱 Page hidden');
        } else {
            console.log('📱 Page visible');
        }
    }
});

// Handle errors
window.addEventListener('error', (e) => {
    console.error('🚨 Global error:', e.error);
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (e) => {
    console.error('🚨 Unhandled promise rejection:', e.reason);
});'''

# Save main app file
with open('public/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js_real_content)

print("✅ Created public/app.js (Real-world main application)")
print(f"📄 File size: {len(app_js_real_content)} characters")