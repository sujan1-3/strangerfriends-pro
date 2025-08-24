# Create the main server.js file with complete WebRTC signaling implementation
server_js_content = '''// StrangerFriends - Real-time Video Chat Server
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const geoip = require('geoip-lite');
const countryList = require('country-list');
require('dotenv').config();

// Initialize Express app
const app = express();
const server = http.createServer(app);

// Initialize Socket.IO with CORS
const io = socketIo(server, {
    cors: {
        origin: process.env.FRONTEND_URL || "*",
        methods: ["GET", "POST"],
        credentials: true
    },
    transports: ['websocket', 'polling']
});

// Middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            scriptSrc: ["'self'", "'unsafe-inline'"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "ws:", "wss:"],
            mediaSrc: ["'self'"],
            fontSrc: ["'self'"]
        }
    }
}));

app.use(compression());
app.use(morgan('combined'));
app.use(cors({
    origin: process.env.FRONTEND_URL || "*",
    credentials: true
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 1000, // Limit each IP to 1000 requests per windowMs
    message: 'Too many requests from this IP, please try again later.',
    standardHeaders: true,
    legacyHeaders: false
});
app.use('/api', limiter);

// Serve static files from public directory
app.use(express.static(path.join(__dirname, '../public')));

// In-memory data stores (use Redis in production)
const connectedUsers = new Map(); // socketId -> user data
const activeRooms = new Map(); // roomId -> room data
const waitingUsers = new Map(); // gender -> array of waiting users
const userStats = {
    totalConnections: 0,
    activeUsers: 0,
    totalRooms: 0
};

// Country detection and flag mapping
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

// Utility functions
function getClientIP(socket) {
    return socket.handshake.headers['x-forwarded-for'] || 
           socket.handshake.headers['x-real-ip'] || 
           socket.conn.remoteAddress || 
           socket.handshake.address;
}

function detectCountry(ip) {
    try {
        // Handle localhost/development
        if (ip === '127.0.0.1' || ip === '::1' || ip.includes('localhost')) {
            return {
                code: 'US',
                name: 'United States',
                flag: '🇺🇸',
                timezone: 'GMT-5'
            };
        }

        const geo = geoip.lookup(ip);
        if (geo && geo.country) {
            const countryCode = geo.country;
            const countryName = countryList.getName(countryCode) || 'Unknown';
            const flag = countryFlags[countryCode] || '🏳️';
            
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
    
    // Fallback
    return {
        code: 'XX',
        name: 'Unknown',
        flag: '🌍',
        timezone: 'GMT+0'
    };
}

function generateRoomId() {
    return uuidv4().substring(0, 8);
}

function findMatchingUser(currentUser) {
    const { gender, preference } = currentUser;
    
    // Get appropriate waiting list based on preference
    let waitingList = [];
    
    if (preference === 'both') {
        // Get all waiting users
        waitingList = [
            ...(waitingUsers.get('male') || []),
            ...(waitingUsers.get('female') || [])
        ];
    } else {
        waitingList = waitingUsers.get(preference) || [];
    }
    
    // Find compatible user
    for (let i = 0; i < waitingList.length; i++) {
        const waitingUser = waitingList[i];
        
        // Check if the waiting user accepts current user's gender
        if (waitingUser.preference === 'both' || waitingUser.preference === gender) {
            // Remove from waiting list
            const waitingGender = waitingUser.gender;
            const genderList = waitingUsers.get(waitingGender) || [];
            const index = genderList.findIndex(u => u.socketId === waitingUser.socketId);
            if (index > -1) {
                genderList.splice(index, 1);
                if (genderList.length === 0) {
                    waitingUsers.delete(waitingGender);
                } else {
                    waitingUsers.set(waitingGender, genderList);
                }
            }
            
            return waitingUser;
        }
    }
    
    return null;
}

function addToWaitingList(user) {
    const { gender } = user;
    if (!waitingUsers.has(gender)) {
        waitingUsers.set(gender, []);
    }
    waitingUsers.get(gender).push(user);
}

function removeFromWaitingList(socketId) {
    for (const [gender, users] of waitingUsers.entries()) {
        const index = users.findIndex(u => u.socketId === socketId);
        if (index > -1) {
            users.splice(index, 1);
            if (users.length === 0) {
                waitingUsers.delete(gender);
            }
            break;
        }
    }
}

// API Routes
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        stats: userStats
    });
});

app.get('/api/stats', (req, res) => {
    res.json({
        activeUsers: userStats.activeUsers,
        totalConnections: userStats.totalConnections,
        activeRooms: userStats.totalRooms,
        waitingUsers: Array.from(waitingUsers.values()).flat().length
    });
});

app.get('/api/country/:ip?', (req, res) => {
    const ip = req.params.ip || req.ip || getClientIP(req);
    const country = detectCountry(ip);
    res.json(country);
});

// STUN/TURN server configuration
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

// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log(`User connected: ${socket.id}`);
    userStats.totalConnections++;
    userStats.activeUsers++;
    
    // Get user's country information
    const clientIP = getClientIP(socket);
    const userCountry = detectCountry(clientIP);
    
    console.log(`User from ${userCountry.name} (${userCountry.code}) connected`);
    
    // Send ICE servers and country info to client
    socket.emit('ice-servers', { iceServers, country: userCountry });
    
    // Handle user preferences and start matching
    socket.on('set-preferences', (preferences) => {
        console.log(`User ${socket.id} set preferences:`, preferences);
        
        const user = {
            socketId: socket.id,
            gender: preferences.gender || 'both',
            preference: preferences.preference || 'both',
            country: userCountry,
            joinedAt: new Date()
        };
        
        connectedUsers.set(socket.id, user);
        
        // Try to find a match immediately
        const match = findMatchingUser(user);
        
        if (match) {
            // Create room and connect both users
            const roomId = generateRoomId();
            const room = {
                id: roomId,
                users: [user, match],
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
                
                // Notify both users of successful match
                socket.emit('match-found', {
                    roomId,
                    partner: {
                        country: match.country,
                        joinedAt: match.joinedAt
                    }
                });
                
                matchSocket.emit('match-found', {
                    roomId,
                    partner: {
                        country: user.country,
                        joinedAt: user.joinedAt
                    }
                });
                
                console.log(`Match created: ${socket.id} <-> ${match.socketId} in room ${roomId}`);
            }
        } else {
            // Add to waiting list
            addToWaitingList(user);
            socket.emit('waiting-for-match');
            console.log(`User ${socket.id} added to waiting list`);
        }
    });
    
    // WebRTC signaling events
    socket.on('offer', (data) => {
        console.log(`Offer from ${socket.id} to room ${data.roomId}`);
        socket.to(data.roomId).emit('offer', {
            offer: data.offer,
            from: socket.id
        });
    });
    
    socket.on('answer', (data) => {
        console.log(`Answer from ${socket.id} to room ${data.roomId}`);
        socket.to(data.roomId).emit('answer', {
            answer: data.answer,
            from: socket.id
        });
    });
    
    socket.on('ice-candidate', (data) => {
        console.log(`ICE candidate from ${socket.id}`);
        socket.to(data.roomId).emit('ice-candidate', {
            candidate: data.candidate,
            from: socket.id
        });
    });
    
    // Handle user actions
    socket.on('next-user', () => {
        console.log(`User ${socket.id} requested next user`);
        handleUserLeave(socket.id, 'next');
        
        // Try to find new match
        const user = connectedUsers.get(socket.id);
        if (user) {
            const match = findMatchingUser(user);
            if (match) {
                // Create new room
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
                        partner: { country: match.country }
                    });
                    
                    matchSocket.emit('match-found', {
                        roomId,
                        partner: { country: user.country }
                    });
                }
            } else {
                addToWaitingList(user);
                socket.emit('waiting-for-match');
            }
        }
    });
    
    socket.on('report-user', (data) => {
        console.log(`User ${socket.id} reported user in room ${data.roomId} for: ${data.reason}`);
        // In production, save to database and implement moderation
        socket.emit('report-submitted');
    });
    
    socket.on('disconnect', () => {
        console.log(`User disconnected: ${socket.id}`);
        handleUserLeave(socket.id, 'disconnect');
        userStats.activeUsers = Math.max(0, userStats.activeUsers - 1);
    });
    
    // Handle connection errors
    socket.on('error', (error) => {
        console.error(`Socket error for ${socket.id}:`, error);
    });
});

function handleUserLeave(socketId, reason) {
    // Remove from connected users
    const user = connectedUsers.get(socketId);
    if (!user) return;
    
    connectedUsers.delete(socketId);
    removeFromWaitingList(socketId);
    
    // Find and handle active room
    for (const [roomId, room] of activeRooms.entries()) {
        const userIndex = room.users.findIndex(u => u.socketId === socketId);
        if (userIndex > -1) {
            // Notify other user in room
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
                                    partner: { country: match.country }
                                });
                                
                                matchSocket.emit('match-found', {
                                    roomId: newRoomId,
                                    partner: { country: otherUser.country }
                                });
                            }
                        } else {
                            addToWaitingList(otherUser);
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

// Serve frontend files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Handle 404
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Not found' });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

server.listen(PORT, HOST, () => {
    console.log(`🚀 StrangerFriends server running on http://${HOST}:${PORT}`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🔧 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
});

// Graceful shutdown
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

module.exports = { app, server, io };'''

# Save server.js
with open('server.js', 'w', encoding='utf-8') as f:
    f.write(server_js_content)

print("✅ Created server.js (Main WebRTC signaling server)")
print(f"📄 File size: {len(server_js_content)} characters")