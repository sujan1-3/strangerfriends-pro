// Core server initialization
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
require('dotenv').config();

// Security & Performance Middleware
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const compression = require('compression');
const morgan = require('morgan');

// Data & Utilities
const geoip = require('geoip-lite');
const { getName } = require('country-list');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: process.env.FRONTEND_URL || "*",
        methods: ["GET", "POST"],
        credentials: true
    }
});

const PORT = process.env.PORT || 3000;

// Security Middleware Stack
app.use(helmet());
app.use(compression());
app.use(cors({ origin: process.env.CORS_ORIGIN || "*" }));
app.use(morgan('dev'));

// Rate Limiting for API endpoints
const limiter = rateLimit({
	windowMs: 15 * 60 * 1000, // 15 minutes
	max: 1000, // Limit each IP to 1000 requests per window
	standardHeaders: true,
	legacyHeaders: false,
});
app.use('/api/', limiter);

// Static File Serving for frontend
app.use(express.static(path.join(__dirname, 'public')));

// In-memory storage for users and rooms
const connectedUsers = new Map();
const activeRooms = new Map();
const waitingUsers = new Map([['male', []], ['female', []], ['both', []]]);
const userStats = {
    totalConnections: 0,
    activeUsers: 0,
    totalRooms: 0
};

// --- Helper Functions from Documentation ---

// IP Address Extraction
function getClientIP(socket) {
    return socket.handshake.headers['x-forwarded-for'] || socket.conn.remoteAddress;
}

// Country Detection
function detectCountry(ip) {
    if (ip === '127.0.0.1' || ip === '::1') {
        return { code: 'US', name: 'United States', flag: '🇺🇸' };
    }
    try {
        const geo = geoip.lookup(ip);
        if (geo && geo.country) {
            return { code: geo.country, name: getName(geo.country) || 'Unknown', flag: '🌍' };
        }
    } catch (error) {
        console.error('Country detection error:', error);
    }
    return { code: 'XX', name: 'Unknown', flag: '🌍' };
}

// User Matching System
function findMatchingUser(currentUser) {
    const { preference } = currentUser;
    let potentialPartners = [];

    if (preference === 'both') {
        potentialPartners = [...(waitingUsers.get('male') || []), ...(waitingUsers.get('female') || [])];
    } else {
        potentialPartners = waitingUsers.get(preference) || [];
    }
    
    for (let i = 0; i < potentialPartners.length; i++) {
        const partner = potentialPartners[i];
        if (partner.preference === 'both' || partner.preference === currentUser.gender) {
            // Found a match, remove from waiting list
            waitingUsers.set(partner.gender, waitingUsers.get(partner.gender).filter(u => u.socketId !== partner.socketId));
            return partner;
        }
    }
    return null;
}

// --- API Endpoints ---

// Health Check Endpoint
app.get('/api/health', (req, res) => {
    res.status(200).json({
        status: "healthy",
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        stats: {
            activeUsers: connectedUsers.size,
            activeRooms: activeRooms.size
        }
    });
});

// Stats Endpoint
app.get('/api/stats', (req, res) => {
    res.status(200).json({
        activeUsers: connectedUsers.size,
        activeRooms: activeRooms.size,
        waitingUsers: waitingUsers.get('male').length + waitingUsers.get('female').length + waitingUsers.get('both').length
    });
});

// --- Socket.IO Real-time Communication ---

io.on('connection', (socket) => {
    console.log(`User connected: ${socket.id}`);
    userStats.totalConnections++;
    userStats.activeUsers = connectedUsers.size + 1;

    const userCountry = detectCountry(getClientIP(socket));

    // Send initial connection info
    socket.emit('connection-success', {
        socketId: socket.id,
        country: userCountry
    });

    // Handle user setting preferences and wanting to match
    socket.on('set-preferences', (preferences) => {
        const currentUser = {
            socketId: socket.id,
            gender: preferences.gender,
            preference: preferences.preference,
        };
        connectedUsers.set(socket.id, currentUser);

        const match = findMatchingUser(currentUser);
        if (match) {
            const roomId = uuidv4();
            activeRooms.set(roomId, [currentUser.socketId, match.socketId]);
            
            // Join both users to the room and notify them
            io.to(currentUser.socketId).emit('match-found', { roomId, partnerId: match.socketId });
            io.to(match.socketId).emit('match-found', { roomId, partnerId: currentUser.socketId });

        } else {
            waitingUsers.get(currentUser.gender).push(currentUser);
            socket.emit('waiting-for-match');
        }
    });

    // Handle WebRTC Signaling Events
    socket.on('offer', (data) => {
        io.to(data.partnerId).emit('offer', { offer: data.offer, senderId: socket.id });
    });

    socket.on('answer', (data) => {
        io.to(data.partnerId).emit('answer', { answer: data.answer, senderId: socket.id });
    });

    socket.on('ice-candidate', (data) => {
        io.to(data.partnerId).emit('ice-candidate', { candidate: data.candidate, senderId: socket.id });
    });
    
    // Handle user disconnect
    socket.on('disconnect', () => {
        console.log(`User disconnected: ${socket.id}`);
        connectedUsers.delete(socket.id);
        userStats.activeUsers = connectedUsers.size;
        // Clean up user from waiting lists
        for(const gender of ['male', 'female', 'both']) {
            waitingUsers.set(gender, waitingUsers.get(gender).filter(u => u.socketId !== socket.id));
        }
        // A full implementation would notify a connected partner that the other user left.
    });
});


server.listen(PORT, () => {
    console.log(`StrangerFriends server is running on http://localhost:${PORT}`);
});
