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

// Socket.IO with proper CORS configuration
const io = new Server(server, {
    cors: {
        origin: [
            "https://strangerfriends-pro.vercel.app",
            "https://strangerfriends-pro.onrender.com",
            "http://localhost:3000",
            "*"
        ],
        methods: ["GET", "POST"],
        credentials: true
    },
    allowEIO3: true
});

const PORT = process.env.PORT || 3000;

// Security middleware - relaxed for Socket.IO functionality
app.use(
    helmet({
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                scriptSrc: ["'self'", "https://cdn.socket.io", "'unsafe-inline'", "'unsafe-eval'"],
                styleSrc: ["'self'", "'unsafe-inline'"],
                connectSrc: ["'self'", "wss:", "ws:", "https:", "http:"],
                imgSrc: ["'self'", "data:", "https:", "blob:"],
                mediaSrc: ["'self'", "blob:", "data:"]
            },
        },
    })
);

app.use(cors({
    origin: [
        "https://strangerfriends-pro.vercel.app",
        "https://strangerfriends-pro.onrender.com", 
        "http://localhost:3000",
        "*"
    ],
    credentials: true
}));

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// In-memory storage
const connectedUsers = new Map();
const waitingUsers = new Map([['male', []], ['female', []], ['both', []]]);
const activeRooms = new Map();
const userStats = {
    totalConnections: 0,
    activeUsers: 0,
    totalRooms: 0
};

// Country flags mapping
const countryFlags = {
    'US': '🇺🇸', 'GB': '🇬🇧', 'CA': '🇨🇦', 'AU': '🇦🇺', 'DE': '🇩🇪',
    'FR': '🇫🇷', 'JP': '🇯🇵', 'IN': '🇮🇳', 'BR': '🇧🇷', 'MX': '🇲🇽',
    'IT': '🇮🇹', 'ES': '🇪🇸', 'RU': '🇷🇺', 'CN': '🇨🇳', 'KR': '🇰🇷',
    'NL': '🇳🇱', 'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'FI': '🇫🇮',
    'PL': '🇵🇱', 'PT': '🇵🇹', 'GR': '🇬🇷', 'TR': '🇹🇷', 'ID': '🇮🇩',
    'TH': '🇹🇭', 'SG': '🇸🇬', 'MY': '🇲🇾', 'PH': '🇵🇭', 'VN': '🇻🇳',
    'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 'PE': '🇵🇪', 'ZA': '🇿🇦',
    'EG': '🇪🇬', 'NG': '🇳🇬', 'KE': '🇰🇪', 'IL': '🇮🇱', 'AE': '🇦🇪'
};

// Helper Functions
function getClientIP(socket) {
    return socket.handshake.headers['x-forwarded-for'] || 
           socket.handshake.headers['x-real-ip'] ||
           socket.conn.remoteAddress ||
           socket.request.connection.remoteAddress;
}

function detectCountry(ip) {
    if (ip === '127.0.0.1' || ip === '::1' || ip === '::ffff:127.0.0.1') {
        return { 
            code: 'US', 
            name: 'United States', 
            flag: '🇺🇸', 
            timezone: 'GMT-5',
            city: 'Local',
            region: 'Local'
        };
    }
    
    try {
        const geo = geoip.lookup(ip);
        if (geo && geo.country) {
            const countryCode = geo.country;
            const countryName = getName(geo.country) || 'Unknown';
            const flag = countryFlags[countryCode] || '🌍';
            
            return { 
                code: countryCode, 
                name: countryName, 
                flag: flag,
                timezone: geo.timezone || 'GMT+0',
                city: geo.city || 'Unknown',
                region: geo.region || 'Unknown'
            };
        }
    } catch (error) {
        console.error('Country detection error:', error);
    }
    
    return { 
        code: 'XX', 
        name: 'Unknown', 
        flag: '🌍', 
        timezone: 'GMT+0',
        city: 'Unknown',
        region: 'Unknown'
    };
}

function findMatchingUser(currentUser) {
    const { preference } = currentUser;
    let potentialPartners = [];
    
    if (preference === 'both') {
        potentialPartners = [
            ...(waitingUsers.get('male') || []), 
            ...(waitingUsers.get('female') || [])
        ];
    } else {
        potentialPartners = waitingUsers.get(preference) || [];
    }
    
    for (let i = 0; i < potentialPartners.length; i++) {
        const partner = potentialPartners[i];
        if (partner.preference === 'both' || partner.preference === currentUser.gender) {
            // Remove from waiting list
            const partnerGender = partner.gender;
            waitingUsers.set(partnerGender, 
                waitingUsers.get(partnerGender).filter(u => u.socketId !== partner.socketId)
            );
            return partner;
        }
    }
    return null;
}

function generateRoomId() {
    return uuidv4();
}

// =============================================================================
// API ROUTES
// =============================================================================

// Serve main HTML page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        stats: {
            activeUsers: userStats.activeUsers,
            totalConnections: userStats.totalConnections,
            activeRooms: userStats.totalRooms,
            waitingUsers: Array.from(waitingUsers.values()).flat().length
        },
        environment: {
            nodeVersion: process.version,
            platform: process.platform,
            arch: process.arch
        }
    });
});

// Live statistics endpoint
app.get('/api/stats', (req, res) => {
    res.json({
        activeUsers: userStats.activeUsers,
        totalConnections: userStats.totalConnections,
        activeRooms: userStats.totalRooms,
        waitingUsers: Array.from(waitingUsers.values()).flat().length,
        timestamp: new Date().toISOString()
    });
});

// Country detection endpoint
app.get('/api/country/:ip?', (req, res) => {
    const ip = req.params.ip || 
               req.headers['x-forwarded-for'] || 
               req.headers['x-real-ip'] ||
               req.connection.remoteAddress || 
               req.socket.remoteAddress ||
               req.ip;
    
    const country = detectCountry(ip);
    res.json(country);
});

// Get waiting users count by gender
app.get('/api/waiting', (req, res) => {
    res.json({
        male: waitingUsers.get('male').length,
        female: waitingUsers.get('female').length,
        both: waitingUsers.get('both').length,
        total: Array.from(waitingUsers.values()).flat().length
    });
});

// Get active rooms information
app.get('/api/rooms', (req, res) => {
    const rooms = Array.from(activeRooms.values()).map(room => ({
        id: room.id,
        userCount: room.users.length,
        createdAt: room.createdAt,
        status: room.status
    }));
    
    res.json({
        totalRooms: activeRooms.size,
        rooms: rooms
    });
});

// STUN/TURN servers endpoint
app.get('/api/ice-servers', (req, res) => {
    const iceServers = [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' },
        { urls: 'stun:stun3.l.google.com:19302' },
        { urls: 'stun:stun4.l.google.com:19302' }
    ];

    // Add TURN servers if credentials provided
    if (process.env.TURN_SERVER && process.env.TURN_USERNAME && process.env.TURN_PASSWORD) {
        iceServers.push({
            urls: process.env.TURN_SERVER,
            username: process.env.TURN_USERNAME,
            credential: process.env.TURN_PASSWORD
        });
    }

    res.json({ iceServers });
});

// Server information endpoint
app.get('/api/info', (req, res) => {
    res.json({
        name: 'StrangerFriends',
        version: '2.0.0',
        description: 'Real-time video chat platform with country detection',
        author: 'StrangerFriends Team',
        features: [
            'Real WebRTC video chat',
            'Country detection',
            'Gender preferences',
            'Mobile responsive',
            'No registration required'
        ],
        endpoints: [
            'GET /',
            'GET /api/health',
            'GET /api/stats', 
            'GET /api/country/:ip?',
            'GET /api/waiting',
            'GET /api/rooms',
            'GET /api/ice-servers',
            'GET /api/info'
        ]
    });
});

// =============================================================================
// SOCKET.IO EVENT HANDLING
// =============================================================================

io.on('connection', (socket) => {
    console.log(`🔌 User connected: ${socket.id}`);
    userStats.totalConnections++;
    userStats.activeUsers++;
    
    // Detect user's country
    const clientIP = getClientIP(socket);
    const userCountry = detectCountry(clientIP);
    console.log(`🌍 User from ${userCountry.name} (${userCountry.code}) connected`);
    
    // Send ICE servers and country info
    socket.emit('ice-servers', { 
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' },
            { urls: 'stun:stun2.l.google.com:19302' }
        ], 
        country: userCountry 
    });
    
    socket.on('set-preferences', (preferences) => {
        console.log(`👤 User ${socket.id} set preferences:`, preferences);
        
        const currentUser = {
            socketId: socket.id,
            gender: preferences.gender,
            preference: preferences.preference,
            country: userCountry,
            joinedAt: new Date()
        };
        
        connectedUsers.set(socket.id, currentUser);

        // Try to find a match
        const match = findMatchingUser(currentUser);
        
        if (match) {
            const roomId = generateRoomId();
            const room = {
                id: roomId,
                users: [currentUser, match],
                createdAt: new Date(),
                status: 'active'
            };
            
            activeRooms.set(roomId, room);
            userStats.totalRooms++;
            
            // Join both users to room
            socket.join(roomId);
            const matchSocket = io.sockets.sockets.get(match.socketId);
            if (matchSocket) {
                matchSocket.join(roomId);
            }
            
            console.log(`🎯 Match created: ${socket.id} <-> ${match.socketId} in room ${roomId}`);
            
            // Notify both users
            socket.emit('match-found', { 
                roomId, 
                partner: {
                    socketId: match.socketId,
                    country: match.country,
                    joinedAt: match.joinedAt
                }
            });
            
            if (matchSocket) {
                matchSocket.emit('match-found', { 
                    roomId, 
                    partner: {
                        socketId: currentUser.socketId,
                        country: currentUser.country,
                        joinedAt: currentUser.joinedAt
                    }
                });
            }
        } else {
            // Add to waiting list
            waitingUsers.get(currentUser.gender).push(currentUser);
            socket.emit('waiting-for-match');
            console.log(`⏳ User ${socket.id} added to waiting list`);
        }
    });

    // WebRTC signaling events
    socket.on('offer', (data) => {
        console.log(`📞 Offer from ${socket.id} to room ${data.roomId}`);
        socket.to(data.roomId).emit('offer', {
            offer: data.offer,
            from: socket.id
        });
    });
    
    socket.on('answer', (data) => {
        console.log(`✅ Answer from ${socket.id} to room ${data.roomId}`);
        socket.to(data.roomId).emit('answer', {
            answer: data.answer,
            from: socket.id
        });
    });
    
    socket.on('ice-candidate', (data) => {
        console.log(`🧊 ICE candidate from ${socket.id}`);
        socket.to(data.roomId).emit('ice-candidate', {
            candidate: data.candidate,
            from: socket.id
        });
    });

    socket.on('next-user', () => {
        console.log(`🔄 User ${socket.id} requested next user`);
        handleUserLeave(socket.id, 'next');
        
        // Try to find new match
        const user = connectedUsers.get(socket.id);
        if (user) {
            const match = findMatchingUser(user);
            if (match) {
                // Create new room and match
                const roomId = generateRoomId();
                const room = {
                    id: roomId,
                    users: [user, match],
                    createdAt: new Date(),
                    status: 'active'
                };
                
                activeRooms.set(roomId, room);
                
                socket.join(roomId);
                const matchSocket = io.sockets.sockets.get(match.socketId);
                if (matchSocket) {
                    matchSocket.join(roomId);
                    
                    socket.emit('match-found', { 
                        roomId, 
                        partner: {
                            socketId: match.socketId,
                            country: match.country
                        }
                    });
                    
                    matchSocket.emit('match-found', { 
                        roomId, 
                        partner: {
                            socketId: user.socketId,
                            country: user.country
                        }
                    });
                }
            } else {
                waitingUsers.get(user.gender).push(user);
                socket.emit('waiting-for-match');
            }
        }
    });

    socket.on('report-user', (data) => {
        console.log(`🚨 User ${socket.id} reported user in room ${data.roomId} for: ${data.reason}`);
        // In production, save to database and implement moderation
        socket.emit('report-submitted');
    });

    socket.on('disconnect', (reason) => {
        console.log(`❌ User disconnected: ${socket.id}, reason: ${reason}`);
        handleUserLeave(socket.id, 'disconnect');
        userStats.activeUsers = Math.max(0, userStats.activeUsers - 1);
    });
    
    socket.on('error', (error) => {
        console.error(`🚨 Socket error for ${socket.id}:`, error);
    });
});

function handleUserLeave(socketId, reason) {
    // Remove from connected users
    const user = connectedUsers.get(socketId);
    if (user) {
        connectedUsers.delete(socketId);
    }
    
    // Remove from waiting lists
    for (const gender of ['male', 'female', 'both']) {
        waitingUsers.set(gender, 
            waitingUsers.get(gender).filter(u => u.socketId !== socketId)
        );
    }
    
    // Handle active rooms
    for (const [roomId, room] of activeRooms.entries()) {
        const userIndex = room.users.findIndex(u => u.socketId === socketId);
        if (userIndex > -1) {
            // Notify other user
            const otherUser = room.users.find(u => u.socketId !== socketId);
            if (otherUser) {
                const otherSocket = io.sockets.sockets.get(otherUser.socketId);
                if (otherSocket) {
                    otherSocket.leave(roomId);
                    otherSocket.emit('partner-left', { reason });
                    
                    // Try to find new match for remaining user
                    setTimeout(() => {
                        const match = findMatchingUser(otherUser);
                        if (match) {
                            const newRoomId = generateRoomId();
                            const newRoom = {
                                id: newRoomId,
                                users: [otherUser, match],
                                createdAt: new Date(),
                                status: 'active'
                            };
                            
                            activeRooms.set(newRoomId, newRoom);
                            
                            otherSocket.join(newRoomId);
                            const matchSocket = io.sockets.sockets.get(match.socketId);
                            if (matchSocket) {
                                matchSocket.join(newRoomId);
                                
                                otherSocket.emit('match-found', {
                                    roomId: newRoomId,
                                    partner: { 
                                        socketId: match.socketId,
                                        country: match.country 
                                    }
                                });
                                
                                matchSocket.emit('match-found', {
                                    roomId: newRoomId,
                                    partner: { 
                                        socketId: otherUser.socketId,
                                        country: otherUser.country 
                                    }
                                });
                            }
                        } else {
                            waitingUsers.get(otherUser.gender).push(otherUser);
                            otherSocket.emit('waiting-for-match');
                        }
                    }, 1000);
                }
            }
            
            activeRooms.delete(roomId);
            userStats.totalRooms = Math.max(0, userStats.totalRooms - 1);
            break;
        }
    }
}

// Handle 404 for undefined routes
app.use('*', (req, res) => {
    res.status(404).json({ 
        error: 'Endpoint not found',
        availableEndpoints: [
            'GET /',
            'GET /api/health',
            'GET /api/stats', 
            'GET /api/country/:ip?',
            'GET /api/waiting',
            'GET /api/rooms',
            'GET /api/ice-servers',
            'GET /api/info'
        ]
    });
});

// Global error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// Graceful shutdown handlers
process.on('SIGTERM', () => {
    console.log('SIGTERM received. Shutting down gracefully...');
    server.close(() => {
        console.log('Server closed.');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received. Shutting down gracefully...');
    server.close(() => {
        console.log('Server closed.');
        process.exit(0);
    });
});

// Start server
server.listen(PORT, () => {
    console.log(`🚀 StrangerFriends server running on port ${PORT}`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🔧 API endpoints available at http://localhost:${PORT}/api/`);
});

module.exports = { app, server, io };
