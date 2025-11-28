# Story 1.3 Technical Context: Chrome Extension Manifest & Basic Structure

**Story ID:** 1.3  
**Context Created:** 2025-11-28  
**Author:** SM Agent (Ragnar)  
**Context Type:** Just-In-Time Technical Guidance  
**Status:** Ready for Implementation

---

## Purpose

This document provides implementation-specific technical context for Story 1.3, offering complete code templates for Chrome Extension Manifest V3, step-by-step implementation guides, and verification checklists. It bridges the story acceptance criteria with actual implementation details.

**When to use this document:**
- During DEV agent implementation (`*dev-story` workflow)
- When unclear about Manifest V3 schema or service worker patterns
- When debugging extension loading issues or CORS problems
- When testing content script injection on job application sites

---

## Quick Reference

### Current Project State

**Existing Files (from Story 1.1):**
```
AutoResumeFiller/
├── extension/
│   ├── background/
│   │   └── .gitkeep              # ✅ Empty directory
│   ├── content/
│   │   └── .gitkeep              # ✅ Empty directory
│   ├── popup/
│   │   └── .gitkeep              # ✅ Empty directory
│   ├── lib/
│   │   └── .gitkeep              # ✅ Empty directory
│   └── icons/
│       └── .gitkeep              # ✅ Empty directory
├── backend/
│   └── main.py                   # ✅ FastAPI app with /api/status endpoint
├── .gitignore                    # ✅ Includes *.crx, *.pem (extension files)
└── README.md                     # ✅ Project documentation (UPDATE in this story)
```

**Story 1.3 Will Create:**
```
AutoResumeFiller/
├── extension/
│   ├── manifest.json             # NEW - Manifest V3 configuration
│   ├── background/
│   │   └── service-worker.js     # NEW - Background service worker
│   ├── content/
│   │   └── content-script.js     # NEW - Content script for job sites
│   ├── popup/
│   │   ├── popup.html            # NEW - Popup interface HTML
│   │   ├── popup.css             # NEW - Popup styling
│   │   └── popup.js              # NEW - Popup backend communication
│   └── icons/
│       ├── icon16.png            # NEW - 16x16 toolbar icon
│       ├── icon48.png            # NEW - 48x48 management icon
│       └── icon128.png           # NEW - 128x128 store icon
└── README.md                     # MODIFY - Add extension installation section
```

---

## Implementation Steps

### Step 1: Create extension/manifest.json

**Complete Manifest V3 Configuration:**

```json
{
  "manifest_version": 3,
  "name": "AutoResumeFiller",
  "version": "1.0.0",
  "description": "Intelligent job application form auto-filling with AI assistance",
  
  "permissions": [
    "storage",
    "activeTab"
  ],
  
  "host_permissions": [
    "http://localhost:8765/*"
  ],
  
  "content_scripts": [
    {
      "matches": [
        "*://*.greenhouse.io/*",
        "*://*.workday.com/*",
        "*://*.lever.co/*",
        "*://www.linkedin.com/jobs/*"
      ],
      "js": ["content/content-script.js"],
      "run_at": "document_idle"
    }
  ],
  
  "background": {
    "service_worker": "background/service-worker.js"
  },
  
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

**Key Configuration Points:**

1. **manifest_version: 3** - Uses Manifest V3 (V2 deprecated by Chrome)
2. **permissions: ["storage", "activeTab"]**
   - `storage`: Access to chrome.storage.local API for extension settings
   - `activeTab`: Access to current tab when user clicks extension icon
3. **host_permissions: ["http://localhost:8765/*"]**
   - Allows fetch() requests to backend API
   - Restricted to localhost only (security-first)
4. **content_scripts.run_at: "document_idle"**
   - Waits for DOM to load before injecting script
   - Ensures form fields are present before detection logic
5. **background.service_worker**
   - Ephemeral service worker (not persistent background page)
   - Wakes on events, sleeps when idle

**Verification:**
```powershell
# Validate JSON syntax
Get-Content extension/manifest.json | ConvertFrom-Json | Out-Null
# If no error, JSON is valid

# Or use Node.js
node -e "JSON.parse(require('fs').readFileSync('extension/manifest.json', 'utf8'))"
```

---

### Step 2: Implement extension/background/service-worker.js

**Complete Background Service Worker:**

```javascript
// extension/background/service-worker.js
/**
 * AutoResumeFiller Background Service Worker
 * 
 * Manages extension lifecycle, handles messages from content scripts,
 * and communicates with backend API on localhost:8765.
 * 
 * Key Features:
 * - Lifecycle event logging (onInstalled, onStartup)
 * - Message routing between content scripts and backend
 * - Backend health check utility
 */

console.log('[AutoResumeFiller] Service worker loaded');

// Extension lifecycle: Installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[AutoResumeFiller] Extension installed:', details.reason);
  
  if (details.reason === 'install') {
    const manifest = chrome.runtime.getManifest();
    console.log('[AutoResumeFiller] First installation - version', manifest.version);
    
    // Initialize default settings
    chrome.storage.local.set({
      extensionEnabled: true,
      backendUrl: 'http://localhost:8765',
      lastHealthCheck: null
    }, () => {
      console.log('[AutoResumeFiller] Default settings initialized');
    });
    
  } else if (details.reason === 'update') {
    console.log('[AutoResumeFiller] Updated from', details.previousVersion, 
                'to', chrome.runtime.getManifest().version);
  }
});

// Extension lifecycle: Browser startup
chrome.runtime.onStartup.addListener(() => {
  console.log('[AutoResumeFiller] Browser started, extension active');
  
  // Perform initial backend health check
  checkBackendHealth()
    .then(isHealthy => {
      console.log('[AutoResumeFiller] Backend health on startup:', isHealthy ? 'healthy' : 'unhealthy');
      chrome.storage.local.set({ lastHealthCheck: Date.now(), backendHealthy: isHealthy });
    })
    .catch(error => {
      console.error('[AutoResumeFiller] Backend health check failed:', error.message);
    });
});

// Message handling from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[AutoResumeFiller] Message received:', {
    type: message.type,
    from: sender.tab ? `tab ${sender.tab.id}` : 'popup'
  });
  
  // Handle different message types
  switch (message.type) {
    case 'FORM_DETECTED':
      handleFormDetected(message, sender, sendResponse);
      return false; // Synchronous response
      
    case 'PING_BACKEND':
      handlePingBackend(message, sender, sendResponse);
      return true; // Keep channel open for async response
      
    case 'GET_SETTINGS':
      handleGetSettings(message, sender, sendResponse);
      return true; // Async response
      
    default:
      console.warn('[AutoResumeFiller] Unknown message type:', message.type);
      sendResponse({ error: 'Unknown message type' });
      return false;
  }
});

/**
 * Handle FORM_DETECTED message from content script
 */
function handleFormDetected(message, sender, sendResponse) {
  const { url, formFields } = message.payload || {};
  console.log('[AutoResumeFiller] Form detected on:', url || sender.tab?.url);
  console.log('[AutoResumeFiller] Form fields count:', formFields?.length || 'unknown');
  
  // Store form detection event (future: send to backend for analysis)
  chrome.storage.local.get(['formDetectionCount'], (result) => {
    const count = (result.formDetectionCount || 0) + 1;
    chrome.storage.local.set({ formDetectionCount: count });
    console.log('[AutoResumeFiller] Total forms detected:', count);
  });
  
  sendResponse({ 
    received: true, 
    timestamp: Date.now(),
    message: 'Form detection logged'
  });
}

/**
 * Handle PING_BACKEND message (check backend health)
 */
async function handlePingBackend(message, sender, sendResponse) {
  try {
    const isHealthy = await checkBackendHealth();
    const response = {
      healthy: isHealthy,
      timestamp: Date.now(),
      url: 'http://localhost:8765/api/status'
    };
    
    // Update stored health status
    chrome.storage.local.set({ 
      lastHealthCheck: Date.now(), 
      backendHealthy: isHealthy 
    });
    
    sendResponse(response);
  } catch (error) {
    console.error('[AutoResumeFiller] Backend ping failed:', error.message);
    sendResponse({ 
      healthy: false, 
      error: error.message,
      timestamp: Date.now()
    });
  }
}

/**
 * Handle GET_SETTINGS message
 */
function handleGetSettings(message, sender, sendResponse) {
  chrome.storage.local.get(null, (settings) => {
    console.log('[AutoResumeFiller] Settings retrieved:', Object.keys(settings));
    sendResponse({ settings });
  });
}

/**
 * Utility: Check backend health
 * 
 * @returns {Promise<boolean>} True if backend is healthy, false otherwise
 */
async function checkBackendHealth() {
  try {
    const response = await fetch('http://localhost:8765/api/status', {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('[AutoResumeFiller] Backend response:', data);
    
    // Verify response structure
    if (data.status !== 'healthy') {
      throw new Error(`Backend returned unhealthy status: ${data.status}`);
    }
    
    return true;
    
  } catch (error) {
    console.error('[AutoResumeFiller] Backend unreachable:', error.message);
    return false;
  }
}

/**
 * Utility: Log error with context
 */
function logError(context, error) {
  console.error(`[AutoResumeFiller] Error in ${context}:`, {
    message: error.message,
    stack: error.stack
  });
}
```

**Key Implementation Points:**

1. **Service Worker Lifecycle:**
   - Logs installation reason (install/update)
   - Initializes default settings in chrome.storage.local
   - Performs health check on browser startup

2. **Message Handling:**
   - FORM_DETECTED: Logs form discovery, increments counter
   - PING_BACKEND: Checks backend health via fetch()
   - GET_SETTINGS: Retrieves all extension settings

3. **Backend Health Check:**
   - Fetches GET /api/status endpoint
   - Validates response.status === 'healthy'
   - Returns boolean (true/false)

**Verification:**
```powershell
# Check JavaScript syntax
node --check extension/background/service-worker.js
# If no output, syntax is valid

# Load extension and check service worker console
# chrome://extensions/ -> Extension -> "Inspect views: service worker"
# Should see: "[AutoResumeFiller] Service worker loaded"
```

---

### Step 3: Implement extension/content/content-script.js

**Complete Content Script:**

```javascript
// extension/content/content-script.js
/**
 * AutoResumeFiller Content Script
 * 
 * Injected into job application pages to detect forms and interact with DOM.
 * Runs on: Greenhouse, Workday, Lever, LinkedIn
 * 
 * Current Implementation (Story 1.3):
 * - Placeholder form detection (logs URL)
 * - Message passing to background worker
 * - Page readiness verification
 * 
 * Future Implementation (Epic 4):
 * - Actual form field detection
 * - Field classification (name, email, experience, etc.)
 * - DOM manipulation for auto-fill
 */

console.log('[AutoResumeFiller] Content script loaded on:', window.location.href);

/**
 * Detect if current page is a job application form
 * 
 * @returns {boolean} True if job site detected
 */
function detectJobApplicationForm() {
  const url = window.location.href;
  
  // Check URL patterns for known job sites
  const jobSitePatterns = [
    'greenhouse.io',
    'workday.com',
    'lever.co',
    'linkedin.com/jobs'
  ];
  
  const isJobSite = jobSitePatterns.some(pattern => url.includes(pattern));
  
  if (isJobSite) {
    console.log('[AutoResumeFiller] Job site detected:', url);
    console.log('[AutoResumeFiller] Site type:', identifySiteType(url));
  } else {
    console.log('[AutoResumeFiller] Not a known job site');
  }
  
  return isJobSite;
}

/**
 * Identify specific job site platform
 * 
 * @param {string} url - Current page URL
 * @returns {string} Platform name
 */
function identifySiteType(url) {
  if (url.includes('greenhouse.io')) return 'Greenhouse';
  if (url.includes('workday.com')) return 'Workday';
  if (url.includes('lever.co')) return 'Lever';
  if (url.includes('linkedin.com/jobs')) return 'LinkedIn';
  return 'Unknown';
}

/**
 * Placeholder: Count form fields on page (future implementation)
 * 
 * @returns {number} Number of form fields found
 */
function countFormFields() {
  // Future implementation: Detect input, select, textarea elements
  const inputs = document.querySelectorAll('input, select, textarea');
  console.log('[AutoResumeFiller] Form fields found:', inputs.length);
  return inputs.length;
}

/**
 * Send message to background worker
 * Notifies extension that a job application form was detected
 */
function notifyBackgroundWorker() {
  if (!detectJobApplicationForm()) {
    console.log('[AutoResumeFiller] Skipping notification - not a job site');
    return;
  }
  
  const payload = {
    url: window.location.href,
    timestamp: Date.now(),
    pageTitle: document.title,
    formFields: countFormFields()
  };
  
  console.log('[AutoResumeFiller] Sending FORM_DETECTED message:', payload);
  
  chrome.runtime.sendMessage(
    { 
      type: 'FORM_DETECTED', 
      payload: payload
    },
    (response) => {
      if (chrome.runtime.lastError) {
        console.error('[AutoResumeFiller] Message send failed:', chrome.runtime.lastError.message);
        return;
      }
      
      console.log('[AutoResumeFiller] Background worker response:', response);
    }
  );
}

/**
 * Initialize content script on page load
 */
function initialize() {
  console.log('[AutoResumeFiller] Initializing content script');
  console.log('[AutoResumeFiller] Document ready state:', document.readyState);
  console.log('[AutoResumeFiller] Page URL:', window.location.href);
  console.log('[AutoResumeFiller] Page title:', document.title);
  
  // Notify background worker if job site detected
  notifyBackgroundWorker();
  
  // Future: Set up DOM observers for dynamic forms
  // Future: Add event listeners for form submission
}

// Run initialization based on document ready state
if (document.readyState === 'loading') {
  console.log('[AutoResumeFiller] Waiting for DOMContentLoaded');
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  console.log('[AutoResumeFiller] Document already loaded, initializing immediately');
  initialize();
}
```

**Key Implementation Points:**

1. **Job Site Detection:**
   - Checks URL for known patterns (greenhouse.io, workday.com, etc.)
   - Logs site type for debugging
   - Returns boolean for conditional logic

2. **Form Field Counting:**
   - Placeholder: counts all input/select/textarea elements
   - Future: will classify fields by purpose (name, email, etc.)

3. **Message Passing:**
   - Sends FORM_DETECTED to background worker
   - Includes URL, timestamp, title, field count
   - Handles chrome.runtime.lastError

4. **Initialization:**
   - Checks document.readyState
   - Waits for DOMContentLoaded if loading
   - Runs immediately if already loaded

**Verification:**
```powershell
# Check JavaScript syntax
node --check extension/content/content-script.js

# Test on Greenhouse demo job board
# Navigate to: https://boards.greenhouse.io/embed/job_board
# Open DevTools (F12) -> Console
# Should see: "[AutoResumeFiller] Content script loaded on: ..."
# Should see: "[AutoResumeFiller] Job site detected: true"
```

---

### Step 4: Create extension/popup/popup.html

**Complete Popup HTML:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutoResumeFiller</title>
  <link rel="stylesheet" href="popup.css">
</head>
<body>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <h1>AutoResumeFiller</h1>
      <p class="tagline">Intelligent Form Auto-Fill</p>
    </div>
    
    <!-- Backend Status Section -->
    <div class="status-section">
      <div class="status-row">
        <span class="status-label">Backend:</span>
        <span id="backend-status" class="status-value disconnected">Checking...</span>
      </div>
      <div class="status-row">
        <span class="status-label">Version:</span>
        <span id="backend-version" class="status-value">—</span>
      </div>
    </div>
    
    <!-- Actions -->
    <div class="actions">
      <button id="open-dashboard" class="btn btn-primary" disabled>
        <span class="btn-icon">🖥️</span>
        Open Dashboard
      </button>
      <button id="reload-status" class="btn btn-secondary">
        <span class="btn-icon">🔄</span>
        Reload Status
      </button>
    </div>
    
    <!-- Quick Stats (Placeholder for future) -->
    <div class="stats">
      <div class="stat-item">
        <span class="stat-label">Forms Detected:</span>
        <span id="forms-detected" class="stat-value">0</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Auto-Fills:</span>
        <span id="autofills-count" class="stat-value">0</span>
      </div>
    </div>
    
    <!-- Footer -->
    <div class="footer">
      <p class="version">Extension v<span id="extension-version">1.0.0</span></p>
      <p class="help-text">Need help? Check <a href="#" id="help-link">docs</a></p>
    </div>
  </div>
  
  <script src="popup.js"></script>
</body>
</html>
```

**Key HTML Elements:**

1. **Status Section:**
   - `#backend-status`: Shows "Connected" (green) or "Disconnected" (red)
   - `#backend-version`: Displays backend version from health check

2. **Action Buttons:**
   - `#open-dashboard`: Launches GUI (disabled until Story 1.4)
   - `#reload-status`: Manual backend health check

3. **Quick Stats:**
   - `#forms-detected`: Count from chrome.storage.local
   - `#autofills-count`: Placeholder for Epic 5

4. **Footer:**
   - Extension version from manifest
   - Help link (placeholder)

---

### Step 5: Create extension/popup/popup.css

**Complete Popup Styling:**

```css
/* extension/popup/popup.css */
/**
 * AutoResumeFiller Popup Styles
 * 
 * Design: Clean, modern, professional
 * Color scheme: Blue (#007bff) for primary, gray for neutral
 * Responsive: Adapts to popup size constraints
 */

/* Reset & Base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  width: 360px;
  min-height: 400px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: #333;
  background: #f5f7fa;
}

.container {
  background: white;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

/* Header */
.header {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 20px;
  text-align: center;
}

.header h1 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.header .tagline {
  font-size: 12px;
  opacity: 0.9;
}

/* Status Section */
.status-section {
  padding: 16px 20px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.status-row:last-child {
  margin-bottom: 0;
}

.status-label {
  font-weight: 500;
  color: #6b7280;
  font-size: 13px;
}

.status-value {
  font-weight: 600;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-value.connected {
  background: #d4edda;
  color: #155724;
}

.status-value.disconnected {
  background: #f8d7da;
  color: #721c24;
}

.status-value.checking {
  background: #fff3cd;
  color: #856404;
}

/* Actions */
.actions {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(108, 117, 125, 0.3);
}

.btn-icon {
  font-size: 16px;
}

/* Quick Stats */
.stats {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  background: #fafbfc;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

.stat-value {
  font-weight: 600;
  font-size: 16px;
  color: #007bff;
}

/* Footer */
.footer {
  margin-top: auto;
  padding: 12px 20px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  text-align: center;
}

.footer .version {
  font-size: 11px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.footer .help-text {
  font-size: 11px;
  color: #6b7280;
}

.footer .help-text a {
  color: #007bff;
  text-decoration: none;
}

.footer .help-text a:hover {
  text-decoration: underline;
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-value.checking {
  animation: pulse 1.5s ease-in-out infinite;
}

/* Loading Spinner (optional) */
.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

**Key Styling Features:**

1. **Color Scheme:**
   - Primary: #007bff (blue) for branding
   - Success: #d4edda (light green) for connected
   - Error: #f8d7da (light red) for disconnected
   - Neutral: Gray tones for text and backgrounds

2. **Layout:**
   - Fixed width: 360px (comfortable popup size)
   - Min height: 400px
   - Flexbox for responsive sections

3. **Animations:**
   - Button hover: translateY + box-shadow
   - Checking state: pulse animation
   - Smooth transitions: 0.2-0.3s ease

4. **Typography:**
   - System font stack for native feel
   - Font sizes: 11-20px for hierarchy
   - Font weights: 500-600 for emphasis

---

### Step 6: Create extension/popup/popup.js

**Complete Popup JavaScript:**

```javascript
// extension/popup/popup.js
/**
 * AutoResumeFiller Popup Logic
 * 
 * Handles:
 * - Backend health check on popup open
 * - Manual status reload
 * - Dashboard launch (placeholder)
 * - Extension statistics display
 */

console.log('[AutoResumeFiller] Popup script loaded');

// DOM element references
const statusElement = document.getElementById('backend-status');
const versionElement = document.getElementById('backend-version');
const extensionVersionElement = document.getElementById('extension-version');
const formsDetectedElement = document.getElementById('forms-detected');
const autofillsCountElement = document.getElementById('autofills-count');
const openDashboardBtn = document.getElementById('open-dashboard');
const reloadStatusBtn = document.getElementById('reload-status');
const helpLink = document.getElementById('help-link');

/**
 * Check backend health and update UI
 */
async function checkBackendHealth() {
  console.log('[AutoResumeFiller] Checking backend health...');
  
  // Update UI to checking state
  statusElement.textContent = 'Checking...';
  statusElement.className = 'status-value checking';
  versionElement.textContent = '—';
  
  try {
    const response = await fetch('http://localhost:8765/api/status', {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('[AutoResumeFiller] Backend response:', data);
    
    // Validate response structure
    if (data.status === 'healthy') {
      statusElement.textContent = 'Connected';
      statusElement.className = 'status-value connected';
      versionElement.textContent = data.version || '1.0.0';
      
      // Enable dashboard button (future - Story 1.4)
      // openDashboardBtn.disabled = false;
      
      console.log('[AutoResumeFiller] Backend healthy');
      return true;
    } else {
      throw new Error(`Unhealthy status: ${data.status}`);
    }
    
  } catch (error) {
    console.error('[AutoResumeFiller] Backend check failed:', error.message);
    
    statusElement.textContent = 'Disconnected';
    statusElement.className = 'status-value disconnected';
    versionElement.textContent = 'N/A';
    
    // Disable dashboard button
    openDashboardBtn.disabled = true;
    
    return false;
  }
}

/**
 * Load and display extension statistics
 */
function loadStatistics() {
  chrome.storage.local.get(['formDetectionCount', 'autofillCount'], (result) => {
    console.log('[AutoResumeFiller] Statistics loaded:', result);
    
    formsDetectedElement.textContent = result.formDetectionCount || 0;
    autofillsCountElement.textContent = result.autofillCount || 0;
  });
}

/**
 * Open GUI dashboard (placeholder for Story 1.4)
 */
function openDashboard() {
  console.log('[AutoResumeFiller] Open dashboard clicked');
  
  // Placeholder alert
  alert('GUI Dashboard opening feature coming in Story 1.4!\n\n' +
        'The PyQt5 desktop application will provide:\n' +
        '• Real-time monitoring of form auto-fill events\n' +
        '• User data management interface\n' +
        '• Configuration settings\n' +
        '• Conversational data updates chatbot');
  
  // Future implementation (Story 1.4):
  // - Send message to backend to launch GUI
  // - Or use native messaging to launch Python script
  // - Or open localhost URL if GUI has web interface
}

/**
 * Reload backend status manually
 */
async function reloadStatus() {
  console.log('[AutoResumeFiller] Manual status reload');
  reloadStatusBtn.disabled = true;
  reloadStatusBtn.textContent = '🔄 Reloading...';
  
  await checkBackendHealth();
  
  reloadStatusBtn.disabled = false;
  reloadStatusBtn.innerHTML = '<span class="btn-icon">🔄</span> Reload Status';
}

/**
 * Show help documentation
 */
function showHelp(event) {
  event.preventDefault();
  console.log('[AutoResumeFiller] Help link clicked');
  
  // Placeholder: Open README or documentation
  alert('Help Documentation\n\n' +
        'Repository: github.com/yourusername/autoresumefiller\n' +
        'README: docs/README.md\n' +
        'Issues: github.com/yourusername/autoresumefiller/issues');
  
  // Future: Open actual documentation link
  // chrome.tabs.create({ url: 'https://github.com/...' });
}

/**
 * Initialize popup
 */
function initialize() {
  console.log('[AutoResumeFiller] Initializing popup');
  
  // Set extension version from manifest
  const manifest = chrome.runtime.getManifest();
  extensionVersionElement.textContent = manifest.version;
  console.log('[AutoResumeFiller] Extension version:', manifest.version);
  
  // Check backend health immediately
  checkBackendHealth();
  
  // Load statistics
  loadStatistics();
  
  // Set up event listeners
  openDashboardBtn.addEventListener('click', openDashboard);
  reloadStatusBtn.addEventListener('click', reloadStatus);
  helpLink.addEventListener('click', showHelp);
  
  console.log('[AutoResumeFiller] Popup initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}
```

**Key JavaScript Features:**

1. **Backend Health Check:**
   - Fetches GET /api/status on popup open
   - Updates UI based on response (connected/disconnected)
   - Validates response.status === 'healthy'

2. **Statistics Display:**
   - Loads formDetectionCount from chrome.storage.local
   - Displays counts in stats section
   - Updates on each popup open

3. **User Actions:**
   - Open Dashboard: Placeholder alert (Story 1.4)
   - Reload Status: Manual health check
   - Help Link: Placeholder alert with documentation info

4. **Error Handling:**
   - Try/catch for fetch errors
   - Logs all operations to console
   - Graceful degradation on failure

**Verification:**
```powershell
# Check JavaScript syntax
node --check extension/popup/popup.js

# Test popup
# 1. Start backend: uvicorn backend.main:app --host 127.0.0.1 --port 8765
# 2. Click extension icon in Chrome toolbar
# 3. Popup should show "Backend: Connected" (green)
# 4. Stop backend, click "Reload Status"
# 5. Popup should show "Backend: Disconnected" (red)
```

---

### Step 7: Create Extension Icons

**Icon Generation Options:**

**Option 1: Simple Placeholder Icons (PowerShell + ImageMagick)**

If you have ImageMagick installed:

```powershell
# Create 16x16 icon
magick -size 16x16 xc:#007bff -pointsize 8 -font Arial -fill white -gravity center -annotate +0+0 "ARF" extension/icons/icon16.png

# Create 48x48 icon
magick -size 48x48 xc:#007bff -pointsize 24 -font Arial-Bold -fill white -gravity center -annotate +0+0 "ARF" extension/icons/icon48.png

# Create 128x128 icon
magick -size 128x128 xc:#007bff -pointsize 64 -font Arial-Bold -fill white -gravity center -annotate +0+0 "ARF" extension/icons/icon128.png
```

**Option 2: Python Script (Cross-Platform)**

Create a Python script to generate icons:

```python
# scripts/generate_icons.py
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text, output_path):
    """Create a simple icon with text on blue background"""
    # Create blue background
    img = Image.new('RGB', (size, size), color='#007bff')
    draw = ImageDraw.Draw(img)
    
    # Calculate font size (roughly 1/3 of icon size)
    font_size = size // 3
    
    try:
        # Try to use a better font
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - font_size // 6
    
    # Draw text
    draw.text((x, y), text, font=font, fill='white')
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f'Created: {output_path}')

# Generate all icon sizes
create_icon(16, 'ARF', 'extension/icons/icon16.png')
create_icon(48, 'ARF', 'extension/icons/icon48.png')
create_icon(128, 'ARF', 'extension/icons/icon128.png')

print('All icons generated successfully!')
```

Install Pillow and run script:

```powershell
pip install Pillow
python scripts/generate_icons.py
```

**Option 3: Manual Creation (Simplest)**

Use any image editor (Paint, GIMP, Photoshop):

1. Create 16x16 PNG with blue background (#007bff)
2. Add white text "ARF" centered
3. Save as `extension/icons/icon16.png`
4. Repeat for 48x48 and 128x128

**Icon Requirements:**

- Format: PNG with transparency support
- Background: Solid color (#007bff recommended)
- Text: High contrast (white on blue)
- Sizes: Exactly 16x16, 48x48, 128x128 pixels
- File names: icon16.png, icon48.png, icon128.png

**Verification:**
```powershell
# Check files exist
Test-Path extension/icons/icon16.png
Test-Path extension/icons/icon48.png
Test-Path extension/icons/icon128.png

# Check dimensions (requires ImageMagick)
identify extension/icons/icon16.png  # Should show: icon16.png PNG 16x16
identify extension/icons/icon48.png  # Should show: icon48.png PNG 48x48
identify extension/icons/icon128.png # Should show: icon128.png PNG 128x128
```

---

### Step 8: Update README.md

**Add Extension Installation Section:**

Find the "Quick Start" section in README.md and add after Step 7 (Run Backend Tests):

```markdown
**8. Run GUI (Development)**
```bash
# In a new terminal
python gui/main.py
```

**9. Load Chrome Extension (Development)**
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `extension/` directory from the project
5. Extension should load with green checkmark

**Verify Extension:**
- Backend responds at `http://localhost:8765/api/status`
- Extension icon appears in Chrome toolbar
- Click extension icon → popup shows "Backend: Connected"
- Navigate to `https://boards.greenhouse.io/embed/job_board`
- Open DevTools (F12) → Console should show content script logs

**Supported Job Sites:**
- **Greenhouse:** `*.greenhouse.io/*`
- **Workday:** `*.workday.com/*`
- **Lever:** `*.lever.co/*`
- **LinkedIn:** `www.linkedin.com/jobs/*`

**Troubleshooting Extension:**

| Issue | Solution |
|-------|----------|
| Extension won't load | Verify `manifest.json` is valid JSON (use jsonlint.com) |
| Service worker inactive | Check JavaScript syntax: `node --check extension/background/service-worker.js` |
| Content script not injecting | Verify URL matches patterns in manifest.json |
| Popup shows "Disconnected" | Ensure backend is running and CORS configured for `chrome-extension://*` |
| Icon not displaying | Verify icon files exist: `extension/icons/icon16.png`, etc. |
```

**Also update the "Installation" section header to clarify:**

```markdown
## Installation (Developer Setup)

### Prerequisites
- **Python 3.9+** (download from [python.org](https://www.python.org/downloads/))
- **Node.js 16+** (optional, for extension linting tools)
- **Google Chrome 88+** or **Microsoft Edge 88+** (Chromium-based browser)
- **Git** (for cloning repository)
```

---

## Verification Checklist

### Pre-Implementation Checks

- [ ] Story 1.1 completed (extension/ directory structure exists)
- [ ] Story 1.2 completed (backend running on localhost:8765)
- [ ] Backend health check endpoint responds: `curl http://localhost:8765/api/status`
- [ ] Backend CORS configured for `chrome-extension://*` in backend/main.py
- [ ] Chrome Developer Mode can be enabled

### Post-Implementation Checks

**AC1: Manifest V3 Configuration**
- [ ] extension/manifest.json created with 45 lines
- [ ] manifest_version is 3
- [ ] permissions include "storage" and "activeTab"
- [ ] host_permissions include "http://localhost:8765/*"
- [ ] content_scripts configured for 4 job sites
- [ ] background.service_worker points to correct file
- [ ] action.default_popup points to popup.html
- [ ] icons configured for 3 sizes
- [ ] JSON syntax is valid: `Get-Content extension/manifest.json | ConvertFrom-Json`

**AC2: Background Service Worker**
- [ ] extension/background/service-worker.js created with ~55 lines
- [ ] chrome.runtime.onInstalled listener implemented
- [ ] chrome.runtime.onStartup listener implemented
- [ ] chrome.runtime.onMessage listener with switch/case for message types
- [ ] checkBackendHealth() function fetches /api/status
- [ ] JavaScript syntax valid: `node --check extension/background/service-worker.js`
- [ ] Console logs "[AutoResumeFiller] Service worker loaded" when extension loads

**AC3: Content Script**
- [ ] extension/content/content-script.js created with ~35 lines
- [ ] detectJobApplicationForm() function checks URL patterns
- [ ] notifyBackgroundWorker() sends FORM_DETECTED message
- [ ] initialize() function runs on DOMContentLoaded or immediately
- [ ] JavaScript syntax valid: `node --check extension/content/content-script.js`
- [ ] Console logs "[AutoResumeFiller] Content script loaded" on job sites

**AC4: Popup Interface**
- [ ] extension/popup/popup.html created with ~30 lines
- [ ] Contains header, status section, action buttons, stats, footer
- [ ] All IDs match JavaScript references (backend-status, etc.)
- [ ] extension/popup/popup.css created with ~90 lines
- [ ] Styles for connected (green) and disconnected (red) states
- [ ] extension/popup/popup.js created with ~50 lines
- [ ] checkBackendHealth() fetches /api/status on popup open
- [ ] loadStatistics() retrieves chrome.storage.local data
- [ ] Event listeners for buttons and links

**AC5: Extension Icons**
- [ ] extension/icons/icon16.png exists (16x16 pixels)
- [ ] extension/icons/icon48.png exists (48x48 pixels)
- [ ] extension/icons/icon128.png exists (128x128 pixels)
- [ ] All icons are PNG format
- [ ] Icons are visible and not corrupted

**AC6: Extension Loads Successfully**
- [ ] Extension loads in Chrome without errors at chrome://extensions/
- [ ] Extension card shows name "AutoResumeFiller"
- [ ] Extension icon appears in Chrome toolbar
- [ ] No "Manifest errors" or "Service worker (Inactive)" warnings
- [ ] Click "Inspect views: service worker" → Console shows logs

**AC7: Content Script Injects**
- [ ] Navigate to https://boards.greenhouse.io/embed/job_board
- [ ] DevTools Console shows "[AutoResumeFiller] Content script loaded"
- [ ] Console shows "[AutoResumeFiller] Job site detected: true"
- [ ] Background worker console shows "FORM_DETECTED" message received
- [ ] Test on at least 2 different job sites (Greenhouse, LinkedIn)

**AC8: Backend Communication**
- [ ] Start backend: uvicorn backend.main:app --host 127.0.0.1 --port 8765
- [ ] Click extension icon → Popup opens
- [ ] Popup shows "Backend: Connected" in green
- [ ] Popup shows backend version (e.g., "1.0.0")
- [ ] Stop backend (Ctrl+C)
- [ ] Click "Reload Status" button
- [ ] Popup shows "Backend: Disconnected" in red

### Documentation Checks

- [ ] README.md updated with extension installation instructions
- [ ] README.md lists supported job sites (4 platforms)
- [ ] README.md includes troubleshooting table
- [ ] All JavaScript files have descriptive comments
- [ ] manifest.json has no inline comments (JSON doesn't support //)

### Git Checks

- [ ] All 10 files staged for commit (7 JS/HTML/CSS + 3 PNGs)
- [ ] sprint-status.yaml updated: 1-3-chrome-extension-manifest-basic-structure: in-progress
- [ ] Git commit message describes all changes
- [ ] No .crx or .pem files committed (should be in .gitignore)

---

## Common Issues and Solutions

### Issue 1: "Manifest file is missing or unreadable"

**Symptom:** Chrome shows error when loading extension  
**Cause:** Invalid JSON syntax in manifest.json  
**Solution:**

```powershell
# Validate JSON syntax
Get-Content extension/manifest.json | ConvertFrom-Json

# Or use Node.js
node -e "JSON.parse(require('fs').readFileSync('extension/manifest.json', 'utf8'))"

# Common errors:
# - Trailing commas in JSON objects/arrays
# - Missing quotes around keys/values
# - Unescaped strings
```

### Issue 2: Service Worker Shows "Inactive"

**Symptom:** Background service worker doesn't run, no console logs  
**Cause:** JavaScript syntax error in service-worker.js  
**Solution:**

```powershell
# Check syntax
node --check extension/background/service-worker.js

# View errors in Chrome
# chrome://extensions/ → Extension → Errors button
# Should show line number and error message

# Common errors:
# - Missing semicolons
# - Undefined variables
# - Syntax errors in async/await
```

### Issue 3: Content Script Not Injecting

**Symptom:** No console logs when visiting greenhouse.io  
**Cause:** URL match pattern incorrect or site requires authentication  
**Solution:**

```javascript
// Verify match patterns in manifest.json
"matches": [
  "*://*.greenhouse.io/*",    // Correct: wildcard subdomain
  // NOT: "https://greenhouse.io/*"  // Incorrect: missing subdomain
  "*://*.workday.com/*",
  "*://*.lever.co/*",
  "*://www.linkedin.com/jobs/*"  // Specific subdomain for LinkedIn
]

// Test on public job boards:
// - https://boards.greenhouse.io/embed/job_board
// - https://jobs.lever.co/example
// - https://www.linkedin.com/jobs/
```

### Issue 4: Popup Shows "Disconnected" Despite Backend Running

**Symptom:** Backend responds to curl but popup shows red  
**Cause:** CORS blocking extension → backend requests  
**Solution:**

```python
# Verify backend/main.py has CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],  # MUST include this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check backend console logs:
# Should see: INFO: 127.0.0.1:xxxxx - "GET /api/status HTTP/1.1" 200 OK
# NOT: INFO: 127.0.0.1:xxxxx - "OPTIONS /api/status HTTP/1.1" 403 Forbidden

# Test backend directly:
curl http://localhost:8765/api/status
# Should return: {"status":"healthy","version":"1.0.0","timestamp":"..."}
```

### Issue 5: Icons Not Displaying

**Symptom:** Extension shows generic gray icon  
**Cause:** Icon file paths incorrect or files don't exist  
**Solution:**

```powershell
# Verify files exist
Test-Path extension/icons/icon16.png
Test-Path extension/icons/icon48.png
Test-Path extension/icons/icon128.png

# Check paths in manifest.json (relative to extension/ directory)
"icons": {
  "16": "icons/icon16.png",    // Correct
  "48": "icons/icon48.png",    // Correct
  "128": "icons/icon128.png"   // Correct
  // NOT: "/icons/icon16.png" or "extension/icons/icon16.png"
}

# Reload extension after adding icons
# chrome://extensions/ → Extension → Reload button (circular arrow)
```

### Issue 6: "Cannot read properties of undefined (reading 'sendMessage')"

**Symptom:** Content script error in console  
**Cause:** chrome.runtime undefined (script not running as content script)  
**Solution:**

```javascript
// Verify script is injected via manifest.json, not loaded directly
// Content scripts MUST be declared in manifest.json content_scripts

// Check if running as content script:
if (typeof chrome !== 'undefined' && chrome.runtime) {
  console.log('Running as content script');
  chrome.runtime.sendMessage({ type: 'TEST' });
} else {
  console.error('Not running as content script!');
}

// Ensure content-script.js is listed in manifest.json:
"content_scripts": [
  {
    "matches": ["*://*.greenhouse.io/*"],
    "js": ["content/content-script.js"]  // Path must be correct
  }
]
```

---

## Testing Strategy

### Unit Testing (Future - Story 1.6)

Extension JavaScript is harder to unit test than backend Python. For now, rely on manual testing. Future:

```javascript
// tests/extension/test-service-worker.js (Jest or Mocha)
// Mock chrome.runtime, chrome.storage APIs
// Test message handling logic
// Test backend health check function
```

### Manual Testing Workflow

**Test 1: Extension Loading**
1. Open `chrome://extensions/`
2. Enable Developer Mode
3. Click "Load unpacked"
4. Select `AutoResumeFiller/extension/`
5. ✅ Extension loads without errors
6. ✅ Icon appears in toolbar

**Test 2: Service Worker Lifecycle**
1. Load extension
2. Click "Inspect views: service worker"
3. ✅ Console shows "[AutoResumeFiller] Service worker loaded"
4. ✅ Console shows "[AutoResumeFiller] Extension installed: install"
5. Reload extension
6. ✅ Console shows "[AutoResumeFiller] Extension installed: update"

**Test 3: Content Script Injection**
1. Navigate to https://boards.greenhouse.io/embed/job_board
2. Open DevTools (F12) → Console
3. ✅ Console shows "[AutoResumeFiller] Content script loaded"
4. ✅ Console shows "[AutoResumeFiller] Job site detected: true"
5. Open service worker console
6. ✅ Console shows "[AutoResumeFiller] Message received: FORM_DETECTED"

**Test 4: Popup Backend Communication (Connected)**
1. Start backend: `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765`
2. Wait for "Application startup complete"
3. Click extension icon in toolbar
4. ✅ Popup opens
5. ✅ Shows "Backend: Connected" (green)
6. ✅ Shows backend version "1.0.0"
7. ✅ Stats show "Forms Detected: 0"

**Test 5: Popup Backend Communication (Disconnected)**
1. Stop backend (Ctrl+C in terminal)
2. Click extension icon
3. ✅ Popup shows "Backend: Disconnected" (red)
4. ✅ Version shows "N/A"
5. Click "Reload Status"
6. ✅ Button shows "🔄 Reloading..."
7. ✅ Status remains "Disconnected"

**Test 6: Multi-Site Content Script**
Test on all supported platforms:

| Site | URL | Expected Console Log |
|------|-----|----------------------|
| Greenhouse | https://boards.greenhouse.io/embed/job_board | ✅ "Job site detected: true", "Site type: Greenhouse" |
| LinkedIn | https://www.linkedin.com/jobs/ | ✅ "Job site detected: true", "Site type: LinkedIn" |
| Lever | https://jobs.lever.co/example (if accessible) | ✅ "Job site detected: true", "Site type: Lever" |
| Generic site | https://google.com | ✅ "Not a known job site" |

**Test 7: Chrome Storage**
1. Open service worker console
2. Run: `chrome.storage.local.get(null, (data) => console.log(data))`
3. ✅ Should show: `{extensionEnabled: true, backendUrl: "http://localhost:8765", ...}`
4. Navigate to job site (triggers form detection)
5. Run storage command again
6. ✅ Should show: `{formDetectionCount: 1, ...}`

---

## Tool-Specific Notes

### Chrome Extension Developer Mode

**Enable Developer Mode:**
```
1. Open Chrome
2. Navigate to chrome://extensions/
3. Toggle "Developer mode" switch (top-right corner)
4. Three new buttons appear: "Load unpacked", "Pack extension", "Update"
```

**Load Extension:**
```
5. Click "Load unpacked"
6. Browse to AutoResumeFiller/extension/ directory
7. Click "Select Folder"
8. Extension loads with ID: chrome-extension://<random-id>/
```

**Reload Extension After Changes:**
```
9. chrome://extensions/ → Extension card → Reload button (circular arrow)
10. Or keyboard shortcut: Ctrl+R on extensions page with extension selected
```

### Debugging Extension Components

**Service Worker Console:**
```
chrome://extensions/ → Extension card → "Inspect views: service worker" (blue link)
Opens DevTools for background service worker
Console shows all console.log() from service-worker.js
Network tab shows fetch() requests to backend
```

**Content Script Console:**
```
Navigate to job site (e.g., greenhouse.io)
Open DevTools (F12) → Console tab
Filter logs: Type "[AutoResumeFiller]" in console filter box
Shows content-script.js logs, errors, warnings
```

**Popup Console:**
```
Click extension icon to open popup
Right-click inside popup → "Inspect" or "Inspect Element"
Opens DevTools for popup window
Console shows popup.js logs, fetch() responses
```

**Extension Storage Inspector:**
```
Service worker console → Application tab → Storage → Extension Storage
Shows chrome.storage.local key-value pairs
Can manually edit values for testing
```

### Manifest V3 Schema Validation

**Online Validators:**
- https://json.schemastore.org/chrome-manifest
- https://developer.chrome.com/docs/extensions/mv3/manifest/

**Command-Line Validation (Node.js + AJV):**
```powershell
# Install AJV CLI
npm install -g ajv-cli

# Validate manifest
ajv validate -s https://json.schemastore.org/chrome-manifest.json -d extension/manifest.json

# If valid: "extension/manifest.json valid"
# If invalid: Shows error with line number
```

### JavaScript Linting (Optional)

```powershell
# Install ESLint
npm install -g eslint

# Initialize ESLint config
cd extension
eslint --init

# Lint all JavaScript files
eslint **/*.js

# Auto-fix issues
eslint **/*.js --fix
```

---

## Integration Points

### Story 1.2 (Backend) Integration

**Popup → Backend Communication:**
```javascript
// popup.js calls backend health check
const response = await fetch('http://localhost:8765/api/status');
const data = await response.json();
// data: {status: "healthy", version: "1.0.0", timestamp: "..."}
```

**Backend CORS Configuration:**
```python
# backend/main.py must include:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],  # Required for extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Backend Logs Extension Requests:**
```
INFO:     127.0.0.1:xxxxx - "GET /api/status HTTP/1.1" 200 OK
```

### Story 1.4 (GUI) Integration (Future)

**Popup "Open Dashboard" Button:**
```javascript
// Current: Placeholder alert
openDashboardBtn.addEventListener('click', () => {
  alert('GUI Dashboard coming in Story 1.4!');
});

// Future (Story 1.4): Actual GUI launch
openDashboardBtn.addEventListener('click', async () => {
  const response = await fetch('http://localhost:8765/api/launch-gui', {
    method: 'POST'
  });
  // Backend spawns PyQt5 GUI process
});
```

### Epic 4 (Form Detection) Integration (Future)

**Content Script Form Detection:**
```javascript
// Current (Story 1.3): Placeholder
function detectJobApplicationForm() {
  return url.includes('greenhouse.io'); // Simple URL check
}

// Future (Epic 4): Actual DOM analysis
function detectJobApplicationForm() {
  const forms = document.querySelectorAll('form');
  const inputs = document.querySelectorAll('input, select, textarea');
  
  // Classify fields by purpose (name, email, phone, experience, etc.)
  // Send field metadata to backend for AI analysis
  // Return structured data for auto-fill
}
```

---

## Next Story: 1.4 (PyQt5 GUI Application Shell)

After completing Story 1.3, the next story will create the PyQt5 desktop GUI that:

1. **Displays backend connection status** (same health check as extension popup)
2. **Shows real-time monitoring** in Monitor tab (placeholder)
3. **Provides data management interface** in My Data tab (placeholder)
4. **Includes configuration settings** in Settings tab (placeholder)
5. **Implements system tray icon** (minimize to tray, not taskbar)

**Integration Point:**
Extension popup "Open Dashboard" button will eventually trigger GUI launch via backend endpoint or native messaging.

---

## Estimated Implementation Time

**Story 1.3 Breakdown:**

| Task | Estimated Time | Complexity |
|------|----------------|------------|
| Create manifest.json | 15 minutes | Low |
| Implement service-worker.js | 30 minutes | Medium |
| Implement content-script.js | 20 minutes | Low |
| Create popup.html | 15 minutes | Low |
| Create popup.css | 25 minutes | Medium |
| Implement popup.js | 30 minutes | Medium |
| Generate icons (3 sizes) | 15 minutes | Low |
| Update README.md | 20 minutes | Low |
| Load and test extension | 30 minutes | Low |
| Debug and fix issues | 30 minutes | Medium |
| Git commit and documentation | 10 minutes | Low |

**Total Estimated Time:** 3 hours 20 minutes  
**Story Points:** 3 (matches estimate)  
**Confidence:** High (75%) - Chrome extension basics well-documented, minimal complexity

---

## Final Pre-Implementation Checklist

Before running `*dev-story`, verify:

- [ ] ✅ Story 1.1 completed (extension/ directory exists)
- [ ] ✅ Story 1.2 completed (backend running with /api/status endpoint)
- [ ] ✅ Backend CORS configured for chrome-extension://*
- [ ] ✅ Chrome Developer Mode can be enabled
- [ ] ✅ Node.js installed (for syntax checking)
- [ ] ✅ Python Pillow installed (if generating icons with script)
- [ ] ✅ ImageMagick installed (if generating icons with magick command)
- [ ] ✅ This context document reviewed and understood

**Ready for implementation!** 🚀

Run `*dev-story` to begin DEV agent implementation of Story 1.3.

---

**Document Status:** Complete  
**Last Updated:** 2025-11-28  
**Next Action:** Run `*dev-story` workflow to implement Story 1.3
