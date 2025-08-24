# Create .gitignore file
gitignore_content = '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env.test

# parcel-bundler cache
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Editor directories and files
.vscode/
.idea/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.dockerignore

# SSL certificates
*.pem
*.crt
*.key
certificates/

# Backup files
*.backup
*.bak
*.old

# Database files
*.sqlite
*.sqlite3
*.db

# Production builds
build/
dist/

# PM2
.pm2

# Docker volumes
docker-data/

# Test files
test-results/
coverage/

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Local development
.local/
dev-data/

# Application specific
uploads/
media/
static/uploads/

# Monitoring and metrics
metrics/
monitoring/

# Cache files
.cache/
*.cache

# Lock files (keep package-lock.json for production consistency)
# Uncomment the next line if you prefer not to commit lock files
# package-lock.json
'''

with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write(gitignore_content)

# Create deployment script
deploy_script = '''#!/bin/bash
# StrangerFriends Deployment Script
# Usage: ./deploy.sh [development|production]

set -e

ENV=${1:-production}
echo "🚀 Starting StrangerFriends deployment for $ENV environment..."

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

print_status "Node.js version: $(node -v) ✓"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_status "npm version: $(npm -v) ✓"

# Install dependencies
print_status "Installing dependencies..."
if [ "$ENV" = "production" ]; then
    npm ci --production --silent
else
    npm ci --silent
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before running the server."
    else
        print_error ".env.example file not found. Cannot create .env file."
        exit 1
    fi
fi

# Validate environment file
print_status "Validating environment configuration..."
if ! grep -q "NODE_ENV" .env; then
    echo "NODE_ENV=$ENV" >> .env
fi

if ! grep -q "PORT" .env; then
    echo "PORT=3000" >> .env
fi

if ! grep -q "HOST" .env; then
    echo "HOST=0.0.0.0" >> .env
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs

# Create public directory if it doesn't exist
mkdir -p public

# Set proper permissions
print_status "Setting file permissions..."
chmod +x server.js 2>/dev/null || true
chmod -R 755 public/ 2>/dev/null || true
chmod -R 755 logs/ 2>/dev/null || true

# Health check
print_status "Running health checks..."

# Check if port is available
PORT=$(grep "^PORT=" .env | cut -d'=' -f2 | tr -d ' ')
if [ -z "$PORT" ]; then
    PORT=3000
fi

if command -v lsof &> /dev/null; then
    if lsof -i :$PORT >/dev/null 2>&1; then
        print_warning "Port $PORT is already in use. You may need to stop the existing process."
    fi
fi

# Test Node.js syntax
print_status "Testing server syntax..."
if ! node -c server.js; then
    print_error "Server.js has syntax errors. Please fix before deployment."
    exit 1
fi

print_status "✅ Deployment preparation completed successfully!"

if [ "$ENV" = "production" ]; then
    print_status "🚀 Starting production server..."
    
    # Install PM2 if not present
    if ! command -v pm2 &> /dev/null; then
        print_status "Installing PM2 process manager..."
        npm install -g pm2
    fi
    
    # Stop existing process
    pm2 stop strangerfriends 2>/dev/null || true
    pm2 delete strangerfriends 2>/dev/null || true
    
    # Start with PM2
    pm2 start server.js --name strangerfriends --env production
    pm2 save
    
    print_status "✅ Production server started with PM2!"
    print_status "Use 'pm2 logs strangerfriends' to view logs"
    print_status "Use 'pm2 status' to check status"
    
else
    print_status "🔧 Development environment ready!"
    print_status "Run 'npm run dev' to start development server"
    print_status "Run 'npm start' to start production server"
fi

print_status "📊 Server will be available at:"
if [ "$ENV" = "production" ]; then
    FRONTEND_URL=$(grep "^FRONTEND_URL=" .env | cut -d'=' -f2 | tr -d ' ')
    if [ -n "$FRONTEND_URL" ]; then
        print_status "🌍 $FRONTEND_URL"
    else
        print_status "🌍 http://localhost:$PORT"
    fi
else
    print_status "🌍 http://localhost:$PORT"
fi

print_status ""
print_status "🎉 StrangerFriends deployment completed!"
print_status "📖 Check README.md for additional configuration options"

if [ "$ENV" = "production" ]; then
    print_warning "⚠️  Make sure to:"
    print_warning "   1. Configure HTTPS certificate"
    print_warning "   2. Set up TURN servers for production"
    print_warning "   3. Configure firewall rules"
    print_warning "   4. Set up monitoring and backups"
fi
'''

with open('deploy.sh', 'w', encoding='utf-8') as f:
    f.write(deploy_script)

# Make script executable
import os
try:
    os.chmod('deploy.sh', 0o755)
except:
    pass

print("✅ Created .gitignore (Version control exclusions)")
print("✅ Created deploy.sh (Automated deployment script)")
print(f"📄 .gitignore size: {len(gitignore_content)} characters")
print(f"📄 deploy.sh size: {len(deploy_script)} characters")