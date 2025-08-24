// StrangerFriends - Complete Working App
class StrangerFriendsApp {
    constructor() {
        this.socket = null;
        this.localStream = null;
        this.remoteStream = null;
        this.peerConnection = null;
        this.roomId = null;
        this.currentScreen = 'hero';
        this.userCountry = null;
        this.partnerCountry = null;
        this.chatStartTime = null;
        this.chatTimer = null;
        
        this.init();
    }

    async init() {
        console.log('🚀 Initializing StrangerFriends App...');
        try {
            await this.initializeSocket();
            this.bindUIEvents();
            this.showHeroSection();
            this.loadStats();
        } catch (error) {
            console.error('❌ Initialization error:', error);
            this.showError('Failed to initialize application. Please refresh the page.');
        }
    }

    async initializeSocket() {
        return new Promise((resolve, reject) => {
            console.log('🔌 Connecting to server...');
            
            // Determine server URL based on environment
            let serverUrl;
            if (window.location.hostname === 'localhost') {
                serverUrl = 'http://localhost:3000';
            } else if (window.location.hostname.includes('vercel.app')) {
                // If frontend is on Vercel, connect to Render backend
                serverUrl = 'https://strangerfriends-pro.onrender.com';
            } else {
                // If everything is on same domain (Render), use relative URL
                serverUrl = window.location.origin;
            }
            
            console.log('🔗 Connecting to:', serverUrl);
            
            this.socket = io(serverUrl, {
                transports: ['websocket', 'polling'],
                timeout: 20000,
                forceNew: true
            });

            this.socket.on('connect', () => {
                console.log('✅ Connected to server');
                this.updateConnectionStatus(true);
                resolve();
            });

            this.socket.on('connect_error', (error) => {
                console.error('❌ Connection error:', error);
                this.updateConnectionStatus(false);
                reject(error);
            });

            this.socket.on('disconnect', (reason) => {
                console.log('❌ Disconnected from server:', reason);
                this.updateConnectionStatus(false);
            });

            this.setupSocketEvents();
        });
    }

    setupSocketEvents() {
        this.socket.on('ice-servers', (data) => {
            console.log('🌍 Received country data:', data.country);
            this.userCountry = data.country;
            this.displayUserCountry(data.country);
        });

        this.socket.on('waiting-for-match', () => {
            console.log('⏳ Waiting for match...');
            this.showWaitingScreen();
        });

        this.socket.on('match-found', (data) => {
            console.log('🎯 Match found!', data);
            this.roomId = data.roomId;
            this.partnerCountry = data.partner.country;
            this.startVideoChat();
        });

        this.socket.on('offer', async (data) => {
            console.log('📞 Received offer from:', data.from);
            await this.handleOffer(data.offer);
        });

        this.socket.on('answer', async (data) => {
            console.log('✅ Received answer from:', data.from);
            await this.handleAnswer(data.answer);
        });

        this.socket.on('ice-candidate', async (data) => {
            console.log('🧊 Received ICE candidate from:', data.from);
            await this.handleIceCandidate(data.candidate);
        });

        this.socket.on('partner-left', (data) => {
            console.log('👋 Partner left:', data.reason);
            this.showNotification('Your partner has left the chat', 'info');
            this.endCall();
        });
    }

    bindUIEvents() {
        // Start chatting button
        const startBtn = document.getElementById('start-chatting-btn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.showGenderSelection());
        }

        // Gender selection buttons
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
            disconnectBtn.addEventListener('click', () => this.endCall());
        }

        const reportBtn = document.getElementById('report-user');
        if (reportBtn) {
            reportBtn.addEventListener('click', () => this.showReportModal());
        }

        // Stats button
        const statsBtn = document.getElementById('stats-btn');
        if (statsBtn) {
            statsBtn.addEventListener('click', () => this.showStatsModal());
        }

        // Safety button
        const safetyBtn = document.getElementById('safety-btn');
        if (safetyBtn) {
            safetyBtn.addEventListener('click', () => this.showSafetyModal());
        }

        // Modal close buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close')) {
                this.closeModal(e.target.closest('.modal'));
            }
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });
    }

    // Screen Management
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
        this.initializeWebRTC();
        this.startChatTimer();
        this.displayPartnerCountry();
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

    selectGender(btn) {
        // Remove selection from all buttons
        document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('selected'));
        
        // Add selection to clicked button
        btn.classList.add('selected');

        const preferences = {
            gender: btn.dataset.gender || 'both',
            preference: btn.dataset.preference || 'both'
        };

        console.log('👤 Selected preferences:', preferences);
        
        // Auto-advance after selection
        setTimeout(() => {
            this.socket.emit('set-preferences', preferences);
        }, 1000);
    }

    async initializeWebRTC() {
        try {
            console.log('🎥 Initializing WebRTC...');
            
            // Request media permissions
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { min: 320, ideal: 1280, max: 1920 },
                    height: { min: 240, ideal: 720, max: 1080 },
                    frameRate: { min: 15, ideal: 30, max: 30 }
                },
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            // Display local video
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = this.localStream;
                localVideo.muted = true; // Prevent feedback
                localVideo.play().catch(e => console.log('Local video play failed:', e));
            }

            // Hide local placeholder
            this.hideVideoPlaceholder('local');

            // Create peer connection
            this.peerConnection = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' },
                    { urls: 'stun:stun1.l.google.com:19302' },
                    { urls: 'stun:stun2.l.google.com:19302' }
                ],
                iceCandidatePoolSize: 10
            });

            // Add local stream tracks
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });

            // Handle remote stream
            this.peerConnection.ontrack = (event) => {
                console.log('📺 Received remote stream');
                this.remoteStream = event.streams[0];
                const remoteVideo = document.getElementById('remoteVideo');
                if (remoteVideo) {
                    remoteVideo.srcObject = this.remoteStream;
                    remoteVideo.play().catch(e => console.log('Remote video play failed:', e));
                }
                this.hideVideoPlaceholder('remote');
                this.updateConnectionIndicator('connected');
            };

            // Handle ICE candidates
            this.peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.socket.emit('ice-candidate', {
                        roomId: this.roomId,
                        candidate: event.candidate
                    });
                }
            };

            // Handle connection state changes
            this.peerConnection.onconnectionstatechange = () => {
                const state = this.peerConnection.connectionState;
                console.log('Connection state:', state);
                this.updateConnectionIndicator(state);
            };

            // Create and send offer
            const offer = await this.peerConnection.createOffer({
                offerToReceiveAudio: true,
                offerToReceiveVideo: true
            });
            
            await this.peerConnection.setLocalDescription(offer);
            
            this.socket.emit('offer', { 
                roomId: this.roomId, 
                offer: offer 
            });

            console.log('📞 Offer sent');

        } catch (error) {
            console.error('❌ WebRTC initialization error:', error);
            this.showError('Unable to access camera/microphone. Please allow permissions and refresh.');
        }
    }

    async handleOffer(offer) {
        try {
            if (!this.peerConnection) {
                await this.initializeWebRTC();
            }
            
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            
            this.socket.emit('answer', { 
                roomId: this.roomId, 
                answer: answer 
            });
            
            console.log('✅ Answer sent');
        } catch (error) {
            console.error('❌ Handle offer error:', error);
        }
    }

    async handleAnswer(answer) {
        try {
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
            console.log('✅ Answer handled');
        } catch (error) {
            console.error('❌ Handle answer error:', error);
        }
    }

    async handleIceCandidate(candidate) {
        try {
            if (this.peerConnection && this.peerConnection.remoteDescription) {
                await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
            }
        } catch (error) {
            console.error('❌ ICE candidate error:', error);
        }
    }

    toggleMicrophone() {
        if (this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                const micBtn = document.getElementById('toggle-mic');
                if (micBtn) {
                    if (audioTrack.enabled) {
                        micBtn.classList.add('active');
                        micBtn.querySelector('.btn-label').textContent = 'Mic';
                    } else {
                        micBtn.classList.remove('active');
                        micBtn.querySelector('.btn-label').textContent = 'Muted';
                    }
                }
                console.log('🎤 Microphone:', audioTrack.enabled ? 'enabled' : 'disabled');
            }
        }
    }

    toggleCamera() {
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                const cameraBtn = document.getElementById('toggle-camera');
                if (cameraBtn) {
                    if (videoTrack.enabled) {
                        cameraBtn.classList.add('active');
                        cameraBtn.querySelector('.btn-label').textContent = 'Camera';
                    } else {
                        cameraBtn.classList.remove('active');
                        cameraBtn.querySelector('.btn-label').textContent = 'Off';
                    }
                }
                console.log('📹 Camera:', videoTrack.enabled ? 'enabled' : 'disabled');
            }
        }
    }

    findNextUser() {
        console.log('🔄 Finding next user...');
        this.socket.emit('next-user');
        this.endCall();
    }

    endCall() {
        console.log('📞 Ending call...');
        
        // Close peer connection
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }

        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }

        // Clear video elements
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        
        if (localVideo) localVideo.srcObject = null;
        if (remoteVideo) remoteVideo.srcObject = null;

        // Show placeholders again
        this.showVideoPlaceholder('local');
        this.showVideoPlaceholder('remote');

        // Stop chat timer
        if (this.chatTimer) {
            clearInterval(this.chatTimer);
            this.chatTimer = null;
        }

        // Go back to gender selection
        this.showGenderSelection();
    }

    // UI Updates
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            const statusDot = statusElement.querySelector('.status-dot');
            const statusText = statusElement.querySelector('.status-text');
            
            if (statusDot && statusText) {
                if (connected) {
                    statusDot.className = 'status-dot connected';
                    statusText.textContent = 'Connected';
                } else {
                    statusDot.className = 'status-dot disconnected';
                    statusText.textContent = 'Connecting...';
                }
            }
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
                case 'failed':
                    indicator.textContent = '🔴 Disconnected';
                    indicator.className = 'connection-indicator disconnected';
                    break;
            }
        }
    }

    displayUserCountry(country) {
        const elements = {
            'user-flag': country.flag,
            'user-country': country.name,
            'local-flag': country.flag,
            'local-country-name': country.name
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });

        const userLocation = document.getElementById('user-location');
        if (userLocation) {
            userLocation.style.display = 'block';
        }
    }

    displayPartnerCountry() {
        if (this.partnerCountry) {
            const remoteFlag = document.getElementById('remote-flag');
            const remoteName = document.getElementById('remote-country-name');
            
            if (remoteFlag) remoteFlag.textContent = this.partnerCountry.flag;
            if (remoteName) remoteName.textContent = this.partnerCountry.name;

            // Display fun fact
            this.displayConnectionFact();
        }
    }

    displayConnectionFact() {
        const factElement = document.getElementById('connection-fact');
        if (factElement && this.userCountry && this.partnerCountry) {
            const facts = [
                `🌍 Connecting ${this.userCountry.name} and ${this.partnerCountry.name}!`,
                `🌎 International chat in progress!`,
                `🗺️ Bridging cultures across continents!`,
                `🌐 Making the world smaller, one chat at a time!`
            ];
            const randomFact = facts[Math.floor(Math.random() * facts.length)];
            factElement.textContent = randomFact;
        }
    }

    hideVideoPlaceholder(type) {
        const placeholder = document.getElementById(`${type}-placeholder`);
        if (placeholder) {
            placeholder.style.display = 'none';
        }
    }

    showVideoPlaceholder(type) {
        const placeholder = document.getElementById(`${type}-placeholder`);
        if (placeholder) {
            placeholder.style.display = 'flex';
        }
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

    async loadStats() {
        try {
            const serverUrl = this.socket ? this.socket.io.uri : window.location.origin;
            const response = await fetch(`${serverUrl}/api/stats`);
            if (response.ok) {
                const stats = await response.json();
                this.updateStatsDisplay(stats);
            }
        } catch (error) {
            console.error('❌ Error loading stats:', error);
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
                element.textContent = value ? value.toLocaleString() : '0';
            }
        });
    }

    // Modal Management
    showStatsModal() {
        this.loadStats();
        const modal = document.getElementById('stats-modal');
        if (modal) modal.style.display = 'flex';
    }

    showSafetyModal() {
        const modal = document.getElementById('safety-modal');
        if (modal) modal.style.display = 'flex';
    }

    showReportModal() {
        const modal = document.getElementById('report-modal');
        if (modal) modal.style.display = 'flex';
    }

    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
        }
    }

    showNotification(message, type = 'info') {
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        // You could implement toast notifications here
        if (type === 'error') {
            alert(message);
        }
    }

    showError(message) {
        console.error('🚨 Error:', message);
        alert(message);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌍 Starting StrangerFriends...');
    window.strangerFriends = new StrangerFriendsApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.strangerFriends) {
        console.log(document.hidden ? '📱 Page hidden' : '📱 Page visible');
    }
});

// Global error handling
window.addEventListener('error', (e) => {
    console.error('🚨 Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('🚨 Unhandled promise rejection:', e.reason);
});
