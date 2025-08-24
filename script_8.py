# Create Dockerfile for production deployment
dockerfile_content = '''# StrangerFriends - Production Docker Image
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Production image, copy all the files and run the app
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Copy built application
COPY --from=builder /app/server.js ./
COPY --from=builder /app/public ./public
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Create logs directory
RUN mkdir -p logs && chown -R nodejs:nodejs logs

USER nodejs

EXPOSE 3000

ENV PORT 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); })"

CMD ["node", "server.js"]
'''

with open('Dockerfile', 'w', encoding='utf-8') as f:
    f.write(dockerfile_content)

# Create docker-compose file
docker_compose_content = '''version: '3.8'

services:
  strangerfriends:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - HOST=0.0.0.0
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); })"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add Redis for scaling (uncomment if needed)
  # redis:
  #   image: redis:6-alpine
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data
  #   restart: unless-stopped

  # Optional: Add MongoDB for user data (uncomment if needed)
  # mongodb:
  #   image: mongo:5
  #   ports:
  #     - "27017:27017"
  #   volumes:
  #     - mongodb_data:/data/db
  #   environment:
  #     - MONGO_INITDB_ROOT_USERNAME=admin
  #     - MONGO_INITDB_ROOT_PASSWORD=password
  #   restart: unless-stopped

# volumes:
#   redis_data:
#   mongodb_data:

networks:
  default:
    driver: bridge
'''

with open('docker-compose.yml', 'w', encoding='utf-8') as f:
    f.write(docker_compose_content)

print("✅ Created Dockerfile (Production container configuration)")
print("✅ Created docker-compose.yml (Multi-service deployment)")
print(f"📄 Dockerfile size: {len(dockerfile_content)} characters")
print(f"📄 Docker Compose size: {len(docker_compose_content)} characters")