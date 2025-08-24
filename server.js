const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const path = require('path');
const helmet = require('helmet');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const geoip = require('geoip-lite');
const { getName } = require('country-list');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: process.env.CORS_ORIGIN || "*",
        methods: ["GET", "POST"]
    }
});

const PORT = process.env.PORT || 3000;

// Security Middleware - More permissive for Socket.IO
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "https://cdn.socket.io", "'unsafe-inline'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        connectSrc: ["'self'", "wss:", "ws:"],
        imgSrc: ["'self'", "data:", "https:"]
      },
    },
  })
);

app.use(cors({ origin: process.env.CORS_ORIGIN || "*" }));
app.use(express.json());

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// In-memory storage
const connectedUsers = new Map();
const waitingUsers = new Map([['male', []], ['female', []], ['both', []]]);
const activeRooms = new Map();

// Helper Functions
function getClientIP(socket) {
    return socket.handshake.headers['x-forwarded-for'] || socket.conn.remoteAddress;
}

function detectCountry(ip) {
    if (ip === '127.0.0.1' || ip === '::1' || ip === '::ffff:127.0.0.1') {
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
            waitingUsers.set(partner.gender, waitingUsers.get(partner.gender).filter(u => u.socketId !== partner.socketId));
            return partner;
        }
    }
    return null;
}

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        connectedUsers: connectedUsers.size,
        activeRooms: activeRooms.size
    });
});

app.get('/api/stats', (req, res) => {
    res.json({
        connectedUsers: connectedUsers.size,
        activeRooms: activeRooms.size,
        waitingUsers: Array.from(waitingUsers.values()).flat().length
    });
});

// Socket.IO Logic
io.on('connection', (socket) => {
    console.log('User connected:', socket.id);
    const userCountry = detectCountry(getClientIP(socket));
    
    // Send connection info to client
    socket.emit('ice-servers', { 
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
        ], 
        country: userCountry 
    });
    
    socket.on('set-preferences', (preferences) => {
        console.log('User set preferences:', preferences);
        const currentUser = {
            socketId: socket.id,
            gender: preferences.gender,
            preference: preferences.preference,
            country: userCountry
        };
        connectedUsers.set(socket.id, currentUser);

        const match = findMatchingUser(currentUser);
        if (match) {
            const roomId = uuidv4();
            activeRooms.set(roomId, [currentUser.socketId, match.socketId]);
            
            // Join both users to the room
            socket.join(roomId);
            const matchSocket = io.sockets.sockets.get(match.socketId);
            if (matchSocket) {
                matchSocket.join(roomId);
            }
            
            console.log(`Match created: ${socket.id} <-> ${match.socketId}`);
            io.to(currentUser.socketId).emit('match-found', { roomId, partner: match });
            io.to(match.socketId).emit('match-found', { roomId, partner: currentUser });
        } else {
            waitingUsers.get(currentUser.gender).push(currentUser);
            socket.emit('waiting-for-match');
            console.log('User added to waiting list:', socket.id);
        }
    });

    socket.on('offer', (data) => { 
        console.log('Offer from:', socket.id);
        socket.to(data.roomId).emit('offer', { offer: data.offer, from: socket.id }); 
    });
    
    socket.on('answer', (data) => { 
        console.log('Answer from:', socket.id);
        socket.to(data.roomId).emit('answer', { answer: data.answer, from: socket.id }); 
    });
    
    socket.on('ice-candidate', (data) => { 
        socket.to(data.roomId).emit('ice-candidate', { candidate: data.candidate, from: socket.id }); 
    });

    socket.on('disconnect', (reason) => {
        console.log('User disconnected:', socket.id, 'Reason:', reason);
        connectedUsers.delete(socket.id);
        for(const gender of ['male', 'female', 'both']) {
            waitingUsers.set(gender, waitingUsers.get(gender).filter(u => u.socketId !== socket.id));
        }
        
        // Clean up rooms
        for (const [roomId, users] of activeRooms.entries()) {
            if (users.includes(socket.id)) {
                activeRooms.delete(roomId);
                const otherUser = users.find(id => id !== socket.id);
                if (otherUser) {
                    io.to(otherUser).emit('partner-left', { reason });
                }
                break;
            }
        }
    });
});

server.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});
