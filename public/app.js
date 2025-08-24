const backendUrl = "https://strangerfriends-pro.onrender.com"; // 👈 IMPORTANT: Use your real Render URL

class StrangerFriendsApp {
    constructor() {
        this.socket = null;
        this.webrtc = null;
        this.partnerCountry = null;
        this.init();
    }

    async init() {
        try {
            await this.initializeSocket();
            this.initializeWebRTC();
            this.bindUIEvents();
        } catch (error) {
            console.error('Initialization error:', error);
            alert('Failed to initialize application. Please refresh the page.');
        }
    }

    async initializeSocket() {
        return new Promise((resolve, reject) => {
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
        this.socket.on('waiting-for-match', () => {
            console.log('⏳ Waiting for match...');
        });

        this.socket.on('match-found', (data) => {
            console.log('🎯 Match found!', data);
            this.partnerCountry = data.partner.country;
            // Additional logic to display partner country if needed
            this.webrtc.setRoomId(data.roomId);
            this.webrtc.setPartnerId(data.partner.socketId);
            this.webrtc.startCall();
        });
    }

    initializeWebRTC() {
        this.webrtc = new WebRTCManager();
        this.webrtc.setSocket(this.socket);
    }
    
    bindUIEvents() {
        const startBtn = document.getElementById('start-chatting-btn'); // Example button ID
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startMatching());
        }
    }
    
    async startMatching() {
        // Example matching logic
        console.log('🔍 Starting matching process...');
        const preferences = { gender: 'both', preference: 'both' }; // Example preferences
        this.socket.emit('set-preferences', preferences);
    }
}

