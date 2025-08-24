// Core server initialization
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

// Security Middleware to allow Socket.IO CDN
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        ...helmet.contentSecurityPolicy.getDefaultDirectives(),
        "script-src": ["'self'", "https://cdn.socket.io"],
        "script-src-attr": ["'self'", "'unsafe-inline'"],
      },
    },
  })
);

app.use(cors({ origin: process.env.CORS_ORIGIN || "*" }));

// Serve the static frontend files
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

// Socket.IO Logic
io.on('connection', (socket) => {
    const userCountry = detectCountry(getClientIP(socket));
    
    socket.on('set-preferences', (preferences) => {
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
            io.to(currentUser.socketId).emit('match-found', { roomId, partner: match });
            io.to(match.socketId).emit('match-found', { roomId, partner: currentUser });
        } else {
            waitingUsers.get(currentUser.gender).push(currentUser);
            socket.emit('waiting-for-match');
        }
    });

    socket.on('offer', (data) => { io.to(data.partnerId).emit('offer', { offer: data.offer, senderId: socket.id }); });
    socket.on('answer', (data) => { io.to(data.partnerId).emit('answer', { answer: data.answer, senderId: socket.id }); });
    socket.on('ice-candidate', (data) => { io.to(data.partnerId).emit('ice-candidate', { candidate: data.candidate, senderId: socket.id }); });

    socket.on('disconnect', () => {
        connectedUsers.delete(socket.id);
        for(const gender of ['male', 'female', 'both']) {
            waitingUsers.set(gender, waitingUsers.get(gender).filter(u => u.socketId !== socket.id));
        }
    });
});

server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
