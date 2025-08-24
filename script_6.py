# Copy the existing CSS to public folder and add additional styles for the real app
css_real_content = '''/* StrangerFriends - Real-world Video Chat Platform Styles */

:root {
  /* Color System */
  --primary-purple: #8B5CF6;
  --primary-cyan: #06B6D4;
  --accent-purple: #A855F7;
  --accent-cyan: #22D3EE;
  --background-dark: #0F172A;
  --background-darker: #020617;
  --surface-dark: #1E293B;
  --surface-light: #334155;
  --text-primary: #FFFFFF;
  --text-secondary: #E2E8F0;
  --text-muted: #94A3B8;
  
  /* Status Colors */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
  
  /* Gradients */
  --gradient-primary: linear-gradient(135deg, var(--primary-purple), var(--primary-cyan));
  --gradient-accent: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
  --gradient-bg: linear-gradient(135deg, var(--background-dark), var(--background-darker));
  
  /* Shadows */
  --shadow-glow: 0 0 20px rgba(139, 92, 246, 0.3);
  --shadow-neon: 0 0 30px rgba(34, 211, 238, 0.4);
  --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.3);
  
  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.5s ease;
}

/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--gradient-bg);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Loading Screen */
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--background-darker);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
}

.loading-logo {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: pulse 2s ease-in-out infinite;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(139, 92, 246, 0.3);
  border-top: 3px solid var(--primary-purple);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 1rem auto;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
}

/* Navigation */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background var(--transition-normal);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
}

.logo-globe {
  font-size: 1.5rem;
  animation: rotateGlobe 10s linear infinite;
}

.logo-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

@keyframes rotateGlobe {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Connection Status */
.connection-status {
  position: fixed;
  top: 80px;
  right: 2rem;
  z-index: 999;
  background: rgba(0, 0, 0, 0.8);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  backdrop-filter: blur(10px);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--error);
  animation: blink 2s infinite;
}

.status-dot.connected {
  background: var(--success);
  animation: none;
}

.status-dot.disconnected {
  background: var(--error);
  animation: blink 2s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.5; }
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  font-size: 1rem;
  position: relative;
  overflow: hidden;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow-glow);
}

.btn--primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.5);
}

.btn--secondary {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn--secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.btn--lg {
  padding: 1rem 2rem;
  font-size: 1.125rem;
  border-radius: 16px;
}

.btn--sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

/* Hero Section */
.hero-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 6rem 2rem 2rem;
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.floating-element {
  position: absolute;
  width: 60px;
  height: 60px;
  background: var(--gradient-accent);
  border-radius: 50%;
  opacity: 0.1;
  animation: float 8s ease-in-out infinite;
}

.floating-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.floating-2 {
  top: 60%;
  right: 15%;
  animation-delay: -2s;
  width: 40px;
  height: 40px;
}

.floating-3 {
  bottom: 20%;
  left: 20%;
  animation-delay: -4s;
  width: 80px;
  height: 80px;
}

.floating-country-flags {
  position: absolute;
  width: 100%;
  height: 100%;
}

.floating-flag {
  position: absolute;
  font-size: 2rem;
  animation: floatFlag 12s ease-in-out infinite;
  opacity: 0.6;
}

.floating-flag:nth-child(1) { top: 15%; left: 5%; animation-delay: 0s; }
.floating-flag:nth-child(2) { top: 25%; right: 10%; animation-delay: -2s; }
.floating-flag:nth-child(3) { top: 45%; left: 15%; animation-delay: -4s; }
.floating-flag:nth-child(4) { top: 65%; right: 20%; animation-delay: -6s; }
.floating-flag:nth-child(5) { bottom: 15%; left: 25%; animation-delay: -8s; }
.floating-flag:nth-child(6) { bottom: 25%; right: 5%; animation-delay: -10s; }
.floating-flag:nth-child(7) { top: 35%; left: 5%; animation-delay: -12s; }
.floating-flag:nth-child(8) { bottom: 35%; right: 15%; animation-delay: -14s; }

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

@keyframes floatFlag {
  0%, 100% { transform: translateY(0px) scale(1); }
  50% { transform: translateY(-30px) scale(1.1); }
}

.hero-content {
  text-align: center;
  z-index: 2;
  max-width: 600px;
}

.hero-logo {
  margin-bottom: 2rem;
}

.logo-globe-main {
  font-size: 4rem;
  animation: pulse 2s ease-in-out infinite;
  display: inline-block;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-tagline {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.hero-features {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.feature-pill {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  font-size: 0.875rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
  transition: all var(--transition-normal);
}

.feature-pill:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.user-location {
  margin: 2rem 0;
  opacity: 0;
  animation: slideUp 0.5s ease-out forwards;
}

.location-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1rem 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: inline-flex;
  align-items: center;
  gap: 1rem;
}

.location-flag {
  font-size: 1.5rem;
}

.cta-button {
  transform: scale(1);
  animation: ctaPulse 3s ease-in-out infinite;
}

@keyframes ctaPulse {
  0%, 100% { box-shadow: var(--shadow-glow); }
  50% { box-shadow: 0 0 40px rgba(139, 92, 246, 0.6); }
}

.user-counter {
  margin-top: 2rem;
  font-size: 1rem;
  color: var(--text-muted);
}

.user-count {
  font-weight: 700;
  color: var(--accent-cyan);
  font-size: 1.125rem;
}

/* Screen Transitions */
.screen {
  min-height: 100vh;
  padding: 6rem 2rem 2rem;
  opacity: 0;
  transform: translateY(20px);
  transition: all var(--transition-slow);
  display: none;
}

.screen.active {
  opacity: 1;
  transform: translateY(0);
}

.screen-container {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.screen-header h2 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.screen-header p {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: 3rem;
}

/* Gender Selection */
.gender-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.gender-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem 1rem;
  cursor: pointer;
  transition: all var(--transition-normal);
  backdrop-filter: blur(10px);
  color: var(--text-primary);
}

.gender-btn:hover {
  border-color: var(--primary-cyan);
  background: rgba(6, 182, 212, 0.1);
  transform: translateY(-5px);
  box-shadow: var(--shadow-neon);
}

.gender-btn.selected {
  border-color: var(--primary-purple);
  background: rgba(139, 92, 246, 0.2);
  box-shadow: var(--shadow-glow);
}

.gender-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.gender-label {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.gender-description {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Waiting Screen */
.waiting-screen {
  display: flex;
  align-items: center;
  justify-content: center;
}

.waiting-animation {
  position: relative;
  margin-bottom: 2rem;
}

.globe-spinner {
  font-size: 4rem;
  animation: spin 2s linear infinite;
  position: relative;
  z-index: 2;
}

.connection-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.ring {
  position: absolute;
  border: 2px solid var(--primary-cyan);
  border-radius: 50%;
  opacity: 0.6;
  animation: ringExpand 2s linear infinite;
}

.ring-1 {
  width: 80px;
  height: 80px;
  margin: -40px 0 0 -40px;
  animation-delay: 0s;
}

.ring-2 {
  width: 120px;
  height: 120px;
  margin: -60px 0 0 -60px;
  animation-delay: -0.7s;
}

.ring-3 {
  width: 160px;
  height: 160px;
  margin: -80px 0 0 -80px;
  animation-delay: -1.4s;
}

@keyframes ringExpand {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}

.waiting-status h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.waiting-info {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.waiting-info p {
  margin: 0.5rem 0;
}

/* Video Chat Screen */
.video-chat-screen {
  padding: 1rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.video-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 80px;
}

.video-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 1rem;
  min-height: 0;
}

.video-frame {
  background: var(--surface-dark);
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.1);
  min-height: 300px;
}

.remote-video {
  grid-column: 1;
}

.local-video {
  grid-column: 2;
  aspect-ratio: 4/3;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: var(--surface-dark);
}

.video-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(45deg, #1E293B, #334155);
  color: var(--text-muted);
  pointer-events: none;
}

.avatar-placeholder {
  font-size: 4rem;
  opacity: 0.5;
  margin-bottom: 1rem;
}

.local .avatar-placeholder {
  font-size: 2rem;
}

.connecting-text {
  font-size: 1rem;
  opacity: 0.8;
}

.video-overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 10;
}

.connection-indicator {
  background: rgba(0, 0, 0, 0.7);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.75rem;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.connection-indicator.connected {
  color: var(--success);
  border-color: var(--success);
}

.connection-indicator.connecting {
  color: var(--warning);
  border-color: var(--warning);
}

.connection-indicator.disconnected {
  color: var(--error);
  border-color: var(--error);
}

.local-indicator {
  background: rgba(139, 92, 246, 0.8);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.75rem;
  backdrop-filter: blur(5px);
}

.country-overlay {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.8);
  padding: 0.75rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.country-overlay .country-flag {
  font-size: 1.5rem;
}

.country-overlay .country-name {
  font-weight: 600;
  color: var(--text-primary);
}

.connection-info {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  margin: 1rem 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.fun-fact {
  font-size: 1rem;
  color: var(--accent-cyan);
  margin-bottom: 0.5rem;
}

.chat-duration {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.video-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.control-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 1rem;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  min-width: 80px;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.control-btn.active {
  border-color: var(--primary-cyan);
  background: rgba(6, 182, 212, 0.2);
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
}

.disconnect-btn {
  border-color: var(--error);
}

.disconnect-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: var(--error);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
}

.report-btn {
  border-color: var(--warning);
}

.report-btn:hover {
  background: rgba(245, 158, 11, 0.2);
  border-color: var(--warning);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
}

.btn-icon {
  font-size: 1.5rem;
}

.btn-label {
  font-size: 0.75rem;
  font-weight: 600;
}

/* Modal Styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: var(--surface-dark);
  border-radius: 20px;
  max-width: 500px;
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  box-shadow: var(--shadow-card);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 1.25rem;
  margin: 0;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 8px;
  transition: background var(--transition-normal);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 1.5rem;
  color: var(--text-secondary);
}

.modal-body p {
  margin-bottom: 1rem;
}

/* Stats Modal */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-cyan);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Safety Modal */
.safety-rules {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.rule-icon {
  font-size: 1.5rem;
  min-width: 40px;
  text-align: center;
}

.rule-text {
  color: var(--text-primary);
  font-weight: 500;
}

.safety-note {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(139, 92, 246, 0.3);
  font-size: 0.875rem;
}

/* Report Modal */
.report-options {
  display: grid;
  gap: 0.5rem;
  margin-top: 1rem;
}

.report-option {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-align: left;
}

.report-option:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: var(--error);
  transform: translateX(4px);
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: right;
}

/* Notifications */
.notification-container {
  position: fixed;
  top: 100px;
  right: 2rem;
  z-index: 10001;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  pointer-events: none;
}

.notification {
  background: var(--surface-dark);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-card);
  animation: notificationSlideIn 0.3s ease-out;
  pointer-events: auto;
  min-width: 300px;
}

.notification--success {
  border-color: var(--success);
  background: rgba(16, 185, 129, 0.1);
}

.notification--error {
  border-color: var(--error);
  background: rgba(239, 68, 68, 0.1);
}

.notification--warning {
  border-color: var(--warning);
  background: rgba(245, 158, 11, 0.1);
}

.notification--info {
  border-color: var(--info);
  background: rgba(59, 130, 246, 0.1);
}

@keyframes notificationSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.notification-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.notification-message {
  color: var(--text-primary);
  font-weight: 500;
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all var(--transition-fast);
}

.notification-close:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.1);
}

/* Animations */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .nav-container {
    padding: 1rem;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-tagline {
    font-size: 1rem;
  }
  
  .hero-features {
    gap: 0.5rem;
  }
  
  .feature-pill {
    font-size: 0.75rem;
    padding: 0.375rem 0.75rem;
  }
  
  .gender-options {
    grid-template-columns: 1fr;
  }
  
  .video-layout {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
  }
  
  .local-video {
    grid-column: 1;
    grid-row: 2;
    aspect-ratio: 16/9;
  }
  
  .video-controls {
    gap: 0.5rem;
    padding: 0.75rem;
    flex-wrap: wrap;
  }
  
  .control-btn {
    min-width: 60px;
    padding: 0.75rem 0.5rem;
  }
  
  .btn-icon {
    font-size: 1.25rem;
  }
  
  .btn-label {
    font-size: 0.6rem;
  }
  
  .screen {
    padding: 4rem 1rem 1rem;
  }
  
  .floating-flag {
    font-size: 1.5rem;
  }
  
  .connection-status {
    right: 1rem;
    font-size: 0.8rem;
  }
  
  .notification-container {
    right: 1rem;
    left: 1rem;
  }
  
  .notification {
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .logo-globe-main {
    font-size: 3rem;
  }
  
  .gender-btn {
    padding: 1.5rem 1rem;
  }
  
  .gender-icon {
    font-size: 2.5rem;
  }
  
  .modal {
    padding: 1rem;
  }
  
  .video-controls {
    gap: 0.25rem;
  }
  
  .control-btn {
    min-width: 50px;
    padding: 0.5rem 0.25rem;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--background-dark);
}

::-webkit-scrollbar-thumb {
  background: var(--surface-light);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-purple);
}

/* Focus styles for accessibility */
.btn:focus-visible,
.control-btn:focus-visible,
.gender-btn:focus-visible {
  outline: 2px solid var(--primary-cyan);
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  :root {
    --shadow-glow: 0 0 20px rgba(255, 255, 255, 0.8);
    --shadow-neon: 0 0 30px rgba(255, 255, 255, 0.9);
  }
  
  .btn--primary {
    border: 2px solid white;
  }
  
  .feature-pill,
  .gender-btn {
    border-width: 2px;
  }
}'''

# Save the CSS file
with open('public/style.css', 'w', encoding='utf-8') as f:
    f.write(css_real_content)

print("✅ Created public/style.css (Complete real-world styles)")
print(f"📄 File size: {len(css_real_content)} characters")