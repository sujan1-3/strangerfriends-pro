# Create complete backend package.json with all dependencies
package_json_content = '''{
  "name": "strangerfriends-backend",
  "version": "1.0.0",
  "description": "Real-time video chat application with country detection - Backend Server",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "build": "npm install --production",
    "test": "jest",
    "docker:build": "docker build -t strangerfriends .",
    "docker:run": "docker run -p 3000:3000 strangerfriends"
  },
  "keywords": [
    "webrtc",
    "video-chat",
    "socket.io",
    "nodejs",
    "real-time",
    "country-detection"
  ],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "socket.io": "^4.7.5",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "dotenv": "^16.3.1",
    "axios": "^1.6.0",
    "uuid": "^9.0.1",
    "express-rate-limit": "^7.1.5",
    "compression": "^1.7.4",
    "morgan": "^1.10.0",
    "node-cron": "^3.0.3",
    "geoip-lite": "^1.4.9",
    "country-list": "^2.3.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.2",
    "jest": "^29.7.0",
    "supertest": "^6.3.3",
    "@types/node": "^20.10.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/strangerfriends-backend.git"
  },
  "bugs": {
    "url": "https://github.com/yourusername/strangerfriends-backend/issues"
  },
  "homepage": "https://github.com/yourusername/strangerfriends-backend#readme"
}'''

# Save package.json
with open('package.json', 'w', encoding='utf-8') as f:
    f.write(package_json_content)

print("✅ Created package.json for backend")
print(f"📄 File size: {len(package_json_content)} characters")