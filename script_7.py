# Create environment configuration file
env_content = '''# StrangerFriends Environment Configuration

# Server Configuration
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# Frontend URL (update with your domain)
FRONTEND_URL=https://yourdomain.com

# TURN/STUN Server Configuration (Optional - for better connectivity)
# You can get free TURN servers from:
# - Xirsys.com (free tier available)
# - Twilio (free credits)
# - WebRTC Ventures
TURN_SERVER=turn:your-turn-server.com:3478
TURN_USERNAME=your-turn-username
TURN_PASSWORD=your-turn-password

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=1000

# Session Configuration
SESSION_SECRET=your-super-secret-key-change-this-in-production

# Logging
LOG_LEVEL=info

# Security
HELMET_CSP_ENABLED=true
CORS_ORIGIN=https://yourdomain.com

# Database Configuration (Optional - for future features)
# DATABASE_URL=mongodb://localhost:27017/strangerfriends
# REDIS_URL=redis://localhost:6379

# Analytics (Optional)
# GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X

# CDN Configuration (Optional)
# CDN_URL=https://cdn.yourdomain.com

# SSL Configuration
# SSL_CERT_PATH=/path/to/certificate.crt
# SSL_KEY_PATH=/path/to/private.key

# Performance
# CLUSTER_WORKERS=4
# ENABLE_COMPRESSION=true

# Monitoring
# HEALTH_CHECK_ENABLED=true
# METRICS_ENABLED=true
'''

with open('.env.example', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✅ Created .env.example (Environment configuration template)")
print(f"📄 File size: {len(env_content)} characters")