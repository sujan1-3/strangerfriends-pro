# Create comprehensive deployment README
readme_content = '''# 🌍 StrangerFriends - Real-World Video Chat Platform

A complete production-ready video chat application with real WebRTC implementation, country detection, and modern features.

## 🚀 Features

### ✨ Core Features
- **Real WebRTC Video Chat** - Peer-to-peer video and audio communication
- **Country Detection** - Real-time IP geolocation with flag display
- **Gender Filtering** - Match with Male, Female, or Everyone
- **Mobile Responsive** - Works seamlessly on all devices
- **No Registration** - Instant access without signup
- **Real-time Matching** - Advanced user matching algorithm

### 🛡️ Security & Safety
- Built-in reporting system
- User blocking functionality
- Rate limiting and DDoS protection
- HTTPS enforcement
- Content Security Policy (CSP)
- Helmet.js security headers

### 📊 Performance
- WebSocket with Socket.IO for real-time communication
- Optimized WebRTC with STUN/TURN support
- Efficient peer-to-peer connections
- Auto-cleanup of unused resources
- Health monitoring and metrics

## 📋 Requirements

- **Node.js** 18+ 
- **npm** 9+
- **Modern Browser** (Chrome 88+, Firefox 78+, Safari 14+, Edge 88+)
- **HTTPS** (required for WebRTC in production)

## ⚡ Quick Start

### 1. Clone and Install
```bash
git clone <your-repo-url>
cd strangerfriends
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Development Server
```bash
npm run dev
```
Visit `http://localhost:3000`

### 4. Run Production Server
```bash
npm start
```

## 🔧 Configuration

### Environment Variables

#### Required
- `NODE_ENV` - Environment (development/production)
- `PORT` - Server port (default: 3000)
- `HOST` - Server host (default: 0.0.0.0)
- `FRONTEND_URL` - Your domain URL

#### Optional
- `TURN_SERVER` - TURN server URL for NAT traversal
- `TURN_USERNAME` - TURN server username
- `TURN_PASSWORD` - TURN server password
- `SESSION_SECRET` - Session encryption key

### TURN/STUN Servers

For production, configure TURN servers for users behind strict firewalls:

#### Free Options:
- **Xirsys** - Free tier with 500MB/month
- **Twilio** - Free credits for TURN services
- **Metered** - Free STUN/TURN servers

#### Configuration:
```env
TURN_SERVER=turn:your-server.com:3478
TURN_USERNAME=your-username
TURN_PASSWORD=your-password
```

## 🚀 Deployment Options

### Option 1: VPS/Dedicated Server

#### Prerequisites:
- Ubuntu 20.04+ or CentOS 8+
- Node.js 18+
- Nginx (reverse proxy)
- SSL certificate (Let's Encrypt recommended)

#### Steps:
```bash
# 1. Upload files to server
scp -r . user@yourserver:/var/www/strangerfriends/

# 2. Install dependencies
cd /var/www/strangerfriends
npm ci --production

# 3. Configure environment
cp .env.example .env
nano .env

# 4. Start with PM2
npm install -g pm2
pm2 start server.js --name strangerfriends
pm2 startup
pm2 save
```

#### Nginx Configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /socket.io/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: Docker Deployment

```bash
# Build and run with Docker
docker build -t strangerfriends .
docker run -d -p 3000:3000 --env-file .env strangerfriends

# Or use Docker Compose
docker-compose up -d
```

### Option 3: Cloud Platform Deployment

#### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
git push heroku main
heroku config:set NODE_ENV=production
heroku config:set FRONTEND_URL=https://your-app-name.herokuapp.com
```

#### DigitalOcean App Platform
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically

#### AWS/Google Cloud/Azure
Use their container services with the provided Dockerfile.

## 🔍 Testing WebRTC

### Local Testing (Development)
WebRTC requires HTTPS in production but works with localhost in development:
- `http://localhost:3000` ✅
- `http://127.0.0.1:3000` ✅  
- `http://your-local-ip:3000` ❌ (requires HTTPS)

### Production Testing
- Always use HTTPS: `https://yourdomain.com`
- Test on different networks (WiFi, mobile data)
- Test behind corporate firewalls (TURN server needed)

## 📊 Monitoring & Analytics

### Health Check
```bash
curl https://yourdomain.com/api/health
```

### Live Statistics
```bash
curl https://yourdomain.com/api/stats
```

### Application Logs
```bash
# PM2 logs
pm2 logs strangerfriends

# Docker logs  
docker logs container-name

# File logs
tail -f logs/app.log
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. WebRTC Connection Fails
- **Cause**: No HTTPS, blocked ports, or NAT issues
- **Solution**: Use HTTPS and configure TURN servers

#### 2. Users Can't Connect
- **Cause**: Firewall blocking WebRTC ports
- **Solution**: Configure TURN relay servers

#### 3. High CPU Usage
- **Cause**: Too many connections
- **Solution**: Implement horizontal scaling with load balancer

#### 4. Socket.IO Disconnections
- **Cause**: Network instability or server overload
- **Solution**: Increase server resources and implement reconnection logic

### Performance Optimization

#### Server-Side:
- Use clustering for multi-core utilization
- Implement Redis for session storage
- Use CDN for static assets
- Enable gzip compression

#### Client-Side:
- Lazy load video streams
- Implement adaptive bitrate
- Use efficient video codecs (VP8/VP9)
- Optimize for mobile devices

## 🔒 Security Best Practices

### Server Security:
- Keep Node.js updated
- Use HTTPS everywhere  
- Implement rate limiting
- Regular security audits
- Monitor for suspicious activity

### Client Security:
- Content Security Policy (CSP)
- No inline scripts
- CSRF protection
- Input validation
- XSS prevention

## 📈 Scaling

### Horizontal Scaling:
```bash
# Multiple server instances with load balancer
pm2 start server.js -i max
```

### Database Integration:
- MongoDB for user data
- Redis for session storage
- PostgreSQL for analytics

### CDN Integration:
- CloudFlare for static assets
- AWS CloudFront for global distribution

## 🐛 Debugging

### Enable Debug Logging:
```env
LOG_LEVEL=debug
```

### WebRTC Debug:
```javascript
// In browser console
localStorage.debug = '*'
```

### Network Debug:
```bash
# Check port availability
netstat -tulpn | grep 3000

# Test WebSocket connection
wscat -c wss://yourdomain.com/socket.io/?EIO=4&transport=websocket
```

## 📁 Project Structure

```
strangerfriends/
├── server.js              # Main server file
├── package.json           # Dependencies
├── .env.example           # Environment template
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-service deployment
├── public/                # Frontend files
│   ├── index.html        # Main HTML
│   ├── style.css         # Styles
│   ├── app.js            # Main application
│   └── webrtc.js         # WebRTC implementation
├── config/               # Configuration files
├── utils/                # Utility functions
├── routes/               # API routes
└── logs/                 # Application logs
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README first
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@yourdomain.com

## 🎯 Production Checklist

Before going live:

- [ ] HTTPS certificate configured
- [ ] Environment variables set
- [ ] TURN servers configured
- [ ] Rate limiting enabled
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Security headers enabled
- [ ] Performance tested
- [ ] Mobile testing completed
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Health checks working

---

**Made with ❤️ for connecting people worldwide** 🌍
'''

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✅ Created README.md (Comprehensive deployment guide)")
print(f"📄 File size: {len(readme_content)} characters")