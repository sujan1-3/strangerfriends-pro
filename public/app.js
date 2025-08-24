// Simple working StrangerFriends App
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
        
        this.init();
    }

    async init() {
        console.log('🚀 Initializing StrangerFriends App...');
        try {
            await this.initializeSocket();
            this.bindUIEvents();
            this.showHeroSection();
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError('Failed to initialize application. Please refresh the page.');
        }
    }

    async initializeSocket() {
        return new Promise((resolve, reject) => {
            console.log('🔌 Connecting to server...');
            this.socket = io(window.location.origin);

            this.socket.on('connect', () => {
                console.log('✅ Connected to server');
                this.updateConnectionStatus(true);
                resolve();
            });

            this.socket.on('connect_error', (error) => {
                console.error('❌ Connection error:', error);
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
            console.log('📞 Received offer');
            await this.handleOffer(data.offer);
        });

        this.socket.on('answer', async (data) => {
            console.log('✅ Received answer');
            await this.handleAnswer(data.answer);
        });

        this.socket.on('ice-candidate', async (data) => {
            console.log('🧊 Received ICE candidate');
            await this.handleIceCandidate(data.candidate);
        });

        this.socket.on('partner-left', () => {
            console.log('👋 Partner left');
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

        // Gender selection
        document.querySelectorAll('.gender-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectGender(e.target.closest('.gender-btn')));
        });

        // Back to home
        const backBtn = document.getElementById('back-to-home');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showHeroSection());
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
        this.initializeWebRTC();
    }

    switchScreen(targetScreen) {
        document.querySelectorAll('.screen, .hero-section').forEach(screen => {
            screen.style.display = 'none';
        });

        const screen = document.getElementById(targetScreen);
        if (screen) {
            screen.style.display = 'flex';
        }
    }

    selectGender(btn) {
        document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        const preferences = {
            gender: btn.dataset.gender || 'both',
            preference: btn.dataset.preference || 'both'
        };

        console.log('👤 Selected preferences:', preferences);
        setTimeout(() => {
            this.socket.emit('set-preferences', preferences);
        }, 1000);
    }

    async initializeWebRTC() {
        try {
            console.log('🎥 Initializing WebRTC...');
            
            // Get user media
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            // Display local video
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = this.localStream;
            }

            // Create peer connection
            this.peerConnection = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' },
                    { urls: 'stun:stun1.l.google.com:19302' }
                ]
            });

            // Add local stream
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
                }
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

            // Create and send offer
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            this.socket.emit('offer', { roomId: this.roomId, offer });

        } catch (error) {
            console.error('❌ WebRTC initialization error:', error);
            this.showError('Unable to access camera/microphone. Please allow permissions.');
        }
    }

    async handleOffer(offer) {
        if (!this.peerConnection) {
            await this.initializeWebRTC();
        }
        
        await this.peerConnection.setRemoteDescription(offer);
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);
        this.socket.emit('answer', { roomId: this.roomId, answer });
    }

    async handleAnswer(answer) {
        await this.peerConnection.setRemoteDescription(answer);
    }

    async handleIceCandidate(candidate) {
        await this.peerConnection.addIceCandidate(candidate);
    }

    toggleMicrophone() {
        if (this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                console.log('🎤 Microphone:', audioTrack.enabled ? 'enabled' : 'disabled');
            }
        }
    }

    toggleCamera() {
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                console.log('📹 Camera:', videoTrack.enabled ? 'enabled' : 'disabled');
            }
        }
    }

    findNextUser() {
        this.endCall();
        this.showGenderSelection();
    }

    endCall() {
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        this.showGenderSelection();
    }

    updateConnectionStatus(connected) {
        // Update UI connection status if elements exist
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? 'Connected' : 'Connecting...';
            statusElement.className = connected ? 'connected' : 'disconnected';
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

    showNotification(message, type = 'info') {
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        // Could implement toast notifications here
    }

    showError(message) {
        console.error('🚨 Error:', message);
        alert(message); // Simple error display
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌍 Starting StrangerFriends...');
    window.strangerFriends = new StrangerFriendsApp();
});
