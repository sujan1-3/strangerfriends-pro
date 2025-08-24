// IMPORTANT: Replace this URL with your actual public Render URL
// -----------------------------------------------------------------
const backendUrl = "https://strangerfriends-pro.onrender.com";

class ConnectSphereApp {
    constructor() {
        this.socket = null;
        this.webrtc = null;
        this.init();
    }

    async init() {
        this.showScreen('landing-screen');
        try {
            await this.initializeSocket();
            this.webrtc = new WebRTCManager();
            this.webrtc.setSocket(this.socket);
            this.bindUIEvents();
        } catch (error) {
            console.error('Initialization error:', error);
            alert('Could not connect to the server. Please try refreshing the page.');
        }
    }

    async initializeSocket() {
        return new Promise((resolve, reject) => {
            // Use the backendUrl variable to connect to the correct server
            this.socket = io(backendUrl, { transports: ['websocket'] });

            this.socket.on('connect', () => {
                console.log('✅ Connected to server');
                resolve();
            });
            this.socket.on('connect_error', (error) => reject(error));
            this.setupSocketEvents();
        });
    }

    setupSocketEvents() {
        this.socket.on('waiting', () => {
            this.showScreen('waiting-screen');
        });

        this.socket.on('partner', (data) => {
            this.showScreen('video-screen');
            this.webrtc.setPartnerId(data.partnerId);
            this.webrtc.startCall();
        });

        this.socket.on('partner-left', () => {
            this.webrtc.closeConnection();
            this.showScreen('landing-screen');
            alert("Your partner has disconnected.");
        });
    }

    bindUIEvents() {
        document.getElementById('start-btn').addEventListener('click', () => this.startMatching());
        document.getElementById('cancel-search-btn').addEventListener('click', () => this.stopMatching());
        document.getElementById('next-btn').addEventListener('click', () => this.startMatching());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopMatching());
    }

    async startMatching() {
        this.showScreen('waiting-screen');
        try {
            await this.webrtc.initializeMedia();
            this.socket.emit('request-match');
        } catch (error) {
            this.showScreen('landing-screen');
        }
    }

    stopMatching() {
        this.socket.emit('cancel-match');
        this.webrtc.closeConnection();
        if (this.webrtc.localStream) {
            this.webrtc.localStream.getTracks().forEach(track => track.stop());
            this.webrtc.localStream = null;
            document.getElementById('localVideo').srcObject = null;
        }
        this.showScreen('landing-screen');
    }

    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        document.getElementById(screenId).classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ConnectSphereApp();
});
