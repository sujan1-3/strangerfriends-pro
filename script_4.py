# Create the WebRTC implementation file
webrtc_js_content = '''// StrangerFriends - Real WebRTC Implementation
class WebRTCManager {
    constructor() {
        this.localStream = null;
        this.remoteStream = null;
        this.peerConnection = null;
        this.socket = null;
        this.currentRoomId = null;
        this.isInitiator = false;
        this.iceServers = [];
        
        // Media constraints
        this.mediaConstraints = {
            video: {
                width: { min: 320, ideal: 1280, max: 1920 },
                height: { min: 240, ideal: 720, max: 1080 },
                frameRate: { min: 15, ideal: 30, max: 30 },
                facingMode: 'user'
            },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 44100
            }
        };

        // WebRTC configuration
        this.rtcConfiguration = {
            iceServers: [],
            iceCandidatePoolSize: 10,
            bundlePolicy: 'max-bundle',
            rtcpMuxPolicy: 'require'
        };

        this.eventHandlers = {};
        this.connectionState = 'new';
        this.dataChannel = null;
        
        this.bindEvents();
    }

    bindEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handlePageHidden();
            } else {
                this.handlePageVisible();
            }
        });

        // Handle beforeunload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }

    setSocket(socket) {
        this.socket = socket;
        this.setupSocketHandlers();
    }

    setupSocketHandlers() {
        if (!this.socket) return;

        this.socket.on('ice-servers', (data) => {
            this.iceServers = data.iceServers || [];
            this.rtcConfiguration.iceServers = this.iceServers;
            console.log('Received ICE servers:', this.iceServers);
            this.emit('country-detected', data.country);
        });

        this.socket.on('match-found', (data) => {
            this.currentRoomId = data.roomId;
            this.emit('match-found', data);
        });

        this.socket.on('offer', async (data) => {
            console.log('Received offer from:', data.from);
            await this.handleOffer(data.offer);
        });

        this.socket.on('answer', async (data) => {
            console.log('Received answer from:', data.from);
            await this.handleAnswer(data.answer);
        });

        this.socket.on('ice-candidate', async (data) => {
            console.log('Received ICE candidate from:', data.from);
            await this.handleIceCandidate(data.candidate);
        });

        this.socket.on('partner-left', (data) => {
            console.log('Partner left:', data.reason);
            this.emit('partner-left', data);
            this.cleanup();
        });
    }

    async initializeMedia() {
        try {
            console.log('Requesting media permissions...');
            this.localStream = await navigator.mediaDevices.getUserMedia(this.mediaConstraints);
            
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = this.localStream;
                localVideo.play().catch(e => console.log('Local video play failed:', e));
            }

            console.log('Media initialized successfully');
            this.emit('media-initialized', this.localStream);
            return true;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            this.emit('media-error', error);
            return false;
        }
    }

    async createPeerConnection() {
        try {
            this.peerConnection = new RTCPeerConnection(this.rtcConfiguration);
            
            // Add local stream tracks
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => {
                    this.peerConnection.addTrack(track, this.localStream);
                });
            }

            // Handle remote stream
            this.peerConnection.ontrack = (event) => {
                console.log('Received remote track:', event);
                this.remoteStream = event.streams[0];
                
                const remoteVideo = document.getElementById('remoteVideo');
                if (remoteVideo) {
                    remoteVideo.srcObject = this.remoteStream;
                    remoteVideo.play().catch(e => console.log('Remote video play failed:', e));
                }

                this.emit('remote-stream', this.remoteStream);
            };

            // Handle ICE candidates
            this.peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    console.log('Sending ICE candidate');
                    this.socket.emit('ice-candidate', {
                        candidate: event.candidate,
                        roomId: this.currentRoomId
                    });
                }
            };

            // Handle connection state changes
            this.peerConnection.onconnectionstatechange = () => {
                const state = this.peerConnection.connectionState;
                console.log('Connection state changed:', state);
                this.connectionState = state;
                this.emit('connection-state-change', state);

                if (state === 'connected') {
                    this.emit('peer-connected');
                } else if (state === 'disconnected' || state === 'failed') {
                    this.emit('peer-disconnected');
                }
            };

            // Handle ICE connection state
            this.peerConnection.oniceconnectionstatechange = () => {
                const state = this.peerConnection.iceConnectionState;
                console.log('ICE connection state:', state);
                this.emit('ice-state-change', state);
            };

            // Handle data channel (for future features)
            this.peerConnection.ondatachannel = (event) => {
                const channel = event.channel;
                channel.onopen = () => console.log('Data channel opened');
                channel.onmessage = (event) => {
                    console.log('Data channel message:', event.data);
                    this.emit('data-message', event.data);
                };
            };

            console.log('Peer connection created successfully');
            return this.peerConnection;
        } catch (error) {
            console.error('Error creating peer connection:', error);
            this.emit('peer-connection-error', error);
            throw error;
        }
    }

    async createOffer() {
        try {
            if (!this.peerConnection) {
                await this.createPeerConnection();
            }

            console.log('Creating offer...');
            const offer = await this.peerConnection.createOffer({
                offerToReceiveAudio: true,
                offerToReceiveVideo: true
            });

            await this.peerConnection.setLocalDescription(offer);
            
            this.socket.emit('offer', {
                offer: offer,
                roomId: this.currentRoomId
            });

            console.log('Offer created and sent');
            this.isInitiator = true;
        } catch (error) {
            console.error('Error creating offer:', error);
            this.emit('offer-error', error);
        }
    }

    async handleOffer(offer) {
        try {
            if (!this.peerConnection) {
                await this.createPeerConnection();
            }

            console.log('Setting remote description (offer)...');
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(offer));

            console.log('Creating answer...');
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);

            this.socket.emit('answer', {
                answer: answer,
                roomId: this.currentRoomId
            });

            console.log('Answer created and sent');
        } catch (error) {
            console.error('Error handling offer:', error);
            this.emit('answer-error', error);
        }
    }

    async handleAnswer(answer) {
        try {
            console.log('Setting remote description (answer)...');
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
            console.log('Answer handled successfully');
        } catch (error) {
            console.error('Error handling answer:', error);
            this.emit('handle-answer-error', error);
        }
    }

    async handleIceCandidate(candidate) {
        try {
            if (this.peerConnection && this.peerConnection.remoteDescription) {
                await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
                console.log('ICE candidate added successfully');
            } else {
                console.log('Queuing ICE candidate for later');
                // Queue the candidate for later if remote description isn't set yet
                if (!this.queuedIceCandidates) {
                    this.queuedIceCandidates = [];
                }
                this.queuedIceCandidates.push(candidate);
            }
        } catch (error) {
            console.error('Error handling ICE candidate:', error);
        }
    }

    async startCall() {
        try {
            console.log('Starting call...');
            
            // Initialize media first
            const mediaInitialized = await this.initializeMedia();
            if (!mediaInitialized) {
                throw new Error('Failed to initialize media');
            }

            // Create peer connection
            await this.createPeerConnection();

            // Create and send offer
            await this.createOffer();

            this.emit('call-started');
        } catch (error) {
            console.error('Error starting call:', error);
            this.emit('call-error', error);
        }
    }

    async answerCall() {
        try {
            console.log('Answering call...');
            
            // Initialize media first
            const mediaInitialized = await this.initializeMedia();
            if (!mediaInitialized) {
                throw new Error('Failed to initialize media');
            }

            this.emit('call-answered');
        } catch (error) {
            console.error('Error answering call:', error);
            this.emit('call-error', error);
        }
    }

    toggleMicrophone() {
        if (this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                console.log('Microphone:', audioTrack.enabled ? 'enabled' : 'disabled');
                this.emit('microphone-toggle', audioTrack.enabled);
                return audioTrack.enabled;
            }
        }
        return false;
    }

    toggleCamera() {
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                console.log('Camera:', videoTrack.enabled ? 'enabled' : 'disabled');
                this.emit('camera-toggle', videoTrack.enabled);
                return videoTrack.enabled;
            }
        }
        return false;
    }

    async switchCamera() {
        try {
            const videoTrack = this.localStream.getVideoTracks()[0];
            const currentFacingMode = videoTrack.getSettings().facingMode;
            const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';

            const newConstraints = {
                ...this.mediaConstraints,
                video: {
                    ...this.mediaConstraints.video,
                    facingMode: newFacingMode
                }
            };

            const newStream = await navigator.mediaDevices.getUserMedia(newConstraints);
            
            // Replace video track in peer connection
            if (this.peerConnection) {
                const sender = this.peerConnection.getSenders().find(s => 
                    s.track && s.track.kind === 'video'
                );
                if (sender) {
                    await sender.replaceTrack(newStream.getVideoTracks()[0]);
                }
            }

            // Replace in local video element
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = newStream;
            }

            // Stop old track and update stream
            videoTrack.stop();
            this.localStream = newStream;

            this.emit('camera-switched', newFacingMode);
        } catch (error) {
            console.error('Error switching camera:', error);
            this.emit('camera-switch-error', error);
        }
    }

    getStats() {
        if (this.peerConnection) {
            return this.peerConnection.getStats();
        }
        return null;
    }

    handlePageHidden() {
        // Reduce video quality when page is hidden
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = false;
            }
        }
    }

    handlePageVisible() {
        // Restore video when page is visible
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = true;
            }
        }
    }

    endCall() {
        console.log('Ending call...');
        this.cleanup();
        this.emit('call-ended');
    }

    cleanup() {
        console.log('Cleaning up WebRTC resources...');

        // Close peer connection
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }

        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => {
                track.stop();
            });
            this.localStream = null;
        }

        // Clear video elements
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        
        if (localVideo) {
            localVideo.srcObject = null;
        }
        if (remoteVideo) {
            remoteVideo.srcObject = null;
        }

        // Reset state
        this.remoteStream = null;
        this.currentRoomId = null;
        this.isInitiator = false;
        this.connectionState = 'new';
        this.queuedIceCandidates = null;

        this.emit('cleanup-complete');
    }

    // Utility methods
    async checkMediaSupport() {
        const support = {
            getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            webRTC: !!(window.RTCPeerConnection),
            webSockets: !!(window.WebSocket)
        };

        console.log('Media support check:', support);
        return support;
    }

    async getAvailableDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            return {
                cameras: devices.filter(device => device.kind === 'videoinput'),
                microphones: devices.filter(device => device.kind === 'audioinput'),
                speakers: devices.filter(device => device.kind === 'audiooutput')
            };
        } catch (error) {
            console.error('Error getting available devices:', error);
            return { cameras: [], microphones: [], speakers: [] };
        }
    }
}

// Export for use in other files
window.WebRTCManager = WebRTCManager;'''

# Save WebRTC implementation
with open('public/webrtc.js', 'w', encoding='utf-8') as f:
    f.write(webrtc_js_content)

print("✅ Created public/webrtc.js (Real WebRTC implementation)")
print(f"📄 File size: {len(webrtc_js_content)} characters")