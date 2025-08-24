# StrangerFriends - Production Docker Image

# STAGE 1: Install dependencies
FROM node:18-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

# STAGE 2: Build the application (copying in source code)
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# STAGE 3: Final production image
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Create a non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Copy only the necessary files from previous stages
COPY --from=builder /app/server.js ./
COPY --from=builder /app/public ./public
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Create the logs directory
RUN mkdir -p logs

# Change ownership of ALL application files to the nodejs user
RUN chown -R nodejs:nodejs .

# Set the user to run the application
USER nodejs

# Command to start the server
CMD ["node", "server.js"]
