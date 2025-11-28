# Story 1.3: Chrome Extension Manifest & Basic Structure

**Epic:** Epic 1 - Foundation & Core Infrastructure  
**Story ID:** 1.3  
**Title:** Chrome Extension Manifest & Basic Structure  
**Status:** Drafted  
**Created:** 2025-11-28  
**Story Points:** 3  
**Priority:** High  
**Assigned To:** DEV Agent  

---

## Story Description

### User Story

**As a** developer building AutoResumeFiller  
**I want** a Chrome Extension scaffolded with Manifest V3 structure  
**So that** I can inject content scripts into job application pages, communicate with the backend, and provide a popup interface for status monitoring

### Context

Story 1.2 delivered a functional FastAPI backend running on `localhost:8765` with a health check endpoint. Story 1.3 builds the Chrome Extension that will interact with job application forms in the browser and communicate with the backend server.

This story establishes the Manifest V3 extension architecture:

1. **manifest.json** - Extension configuration with permissions, content script injection rules, background service worker registration
2. **Content Script** - Injected into job application pages (Workday, Greenhouse, Lever, LinkedIn) to detect forms and manipulate DOM
3. **Background Service Worker** - Manages extension lifecycle, handles messages between content scripts and backend
4. **Popup Interface** - Shows backend connection status and provides quick access to the GUI dashboard

While this story doesn't implement actual form detection or auto-filling logic (those come in Epic 4 and Epic 5), it creates the extension shell that future features will build upon. The key integration point is the popup displaying "Backend: Connected" when `http://localhost:8765/api/status` returns successfully.

### Dependencies

- ✅ **Story 1.1:** Project Initialization & Repository Setup (COMPLETED)
  - Requires `extension/` directory structure
  - Requires `.gitignore` to exclude packaged extension files

- ✅ **Story 1.2:** Python Backend Scaffolding (COMPLETED)
  - Backend must be running on `localhost:8765`
  - Health check endpoint (`GET /api/status`) must be operational
  - CORS configured for `chrome-extension://*` origins

- 📦 **External Dependencies:**
  - Google Chrome 88+ or Microsoft Edge 88+ (Chromium-based browser)
  - Chrome Developer Mode enabled for loading unpacked extension

### Technical Approach

**Implementation Strategy:**

1. **Create `extension/manifest.json`** with Manifest V3 schema:
   - Set manifest_version to 3 (V2 deprecated)
   - Configure permissions: `storage`, `activeTab`
   - Configure host_permissions: `http://localhost:8765/*` (backend API access)
   - Define content_scripts with matches for job sites (*.greenhouse.io/*, *.workday.com/*, *.lever.co/*, linkedin.com/jobs/*)
   - Register background service worker (`background/service-worker.js`)
   - Configure action (popup) with HTML, CSS, JS, icons

2. **Implement `extension/background/service-worker.js`**:
   - Add `chrome.runtime.onInstalled` listener logging extension installation
   - Add `chrome.runtime.onStartup` listener logging browser startup
   - Add `chrome.runtime.onMessage` listener for content script communication
   - Create utility function to ping backend health check endpoint

3. **Implement `extension/content/content-script.js`**:
   - Log initialization message to console
   - Create placeholder `detectJobApplicationForm()` function
   - Send test message to background worker on page load

4. **Create `extension/popup/` interface**:
   - `popup.html` - Minimal UI with extension title, backend status indicator, link to GUI
   - `popup.css` - Basic styling (green for connected, red for disconnected)
   - `popup.js` - Fetch backend health check and update status display

5. **Create placeholder icons**:
   - Generate 16x16, 48x48, 128x128 PNG icons (simple colored squares for now)
   - Place in `extension/icons/` directory

**Key Design Decisions:**

- **Manifest V3 over V2:** V2 is deprecated by Google, V3 is the modern standard (service workers, host_permissions, declarative APIs)
- **Ephemeral service worker:** Background script is a service worker (not persistent background page), wakes on events
- **Content script injection on match:** Only inject on known job sites to minimize performance impact
- **localhost communication:** Extension popup pings `http://localhost:8765/api/status` to show connection status
- **chrome.storage.local over sync:** Privacy-first design - no cloud synchronization of extension settings

---

## Acceptance Criteria

### AC1: Manifest V3 Configuration Complete

**Given** the `extension/` directory structure from Story 1.1  
**When** creating `extension/manifest.json`  
**Then** it contains valid Manifest V3 configuration:

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

**Verification:**
```bash
# Validate manifest schema (Node.js + AJV recommended)
npx ajv validate -s manifest-v3-schema.json -d extension/manifest.json

# Or manual check in Chrome
# chrome://extensions/ → Load unpacked → extension/ → Check for errors
```

---

### AC2: Background Service Worker Implemented

**Given** `extension/manifest.json` configured  
**When** implementing `extension/background/service-worker.js`  
**Then** it contains:

**Required Components:**
1. **Installation listener** logging extension version
2. **Startup listener** logging browser launch
3. **Message listener** handling content script messages
4. **Backend health check function** to verify API availability

**Code Template:**
```javascript
// extension/background/service-worker.js

// Extension lifecycle listeners
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[AutoResumeFiller] Extension installed:', details.reason);
  if (details.reason === 'install') {
    console.log('[AutoResumeFiller] First installation - version', chrome.runtime.getManifest().version);
  } else if (details.reason === 'update') {
    console.log('[AutoResumeFiller] Updated from', details.previousVersion, 'to', chrome.runtime.getManifest().version);
  }
});

chrome.runtime.onStartup.addListener(() => {
  console.log('[AutoResumeFiller] Browser started, extension active');
});

// Message handling from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[AutoResumeFiller] Message received:', message.type);
  
  if (message.type === 'FORM_DETECTED') {
    console.log('[AutoResumeFiller] Form detected on:', sender.tab?.url);
    sendResponse({ received: true, timestamp: Date.now() });
  } else if (message.type === 'PING_BACKEND') {
    // Check backend health
    checkBackendHealth()
      .then(isHealthy => sendResponse({ healthy: isHealthy }))
      .catch(err => sendResponse({ healthy: false, error: err.message }));
    return true; // Keep message channel open for async response
  }
  
  return false;
});

// Utility: Check backend health
async function checkBackendHealth() {
  try {
    const response = await fetch('http://localhost:8765/api/status');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    console.log('[AutoResumeFiller] Backend healthy:', data);
    return data.status === 'healthy';
  } catch (error) {
    console.error('[AutoResumeFiller] Backend unreachable:', error.message);
    return false;
  }
}
```

**Verification:**
```bash
# Load extension in Chrome
# Open chrome://extensions/ → Details → Inspect views: service worker
# Should see console logs for onInstalled and onStartup
```

---

### AC3: Content Script Injected on Job Sites

**Given** `extension/manifest.json` with content_scripts configuration  
**When** implementing `extension/content/content-script.js`  
**Then** it contains:

```javascript
// extension/content/content-script.js

console.log('[AutoResumeFiller] Content script loaded on:', window.location.href);

// Placeholder: Detect if current page is a job application form
function detectJobApplicationForm() {
  // Future implementation (Epic 4): Analyze DOM for form fields
  // For now, just log the page URL
  const url = window.location.href;
  const isJobSite = url.includes('greenhouse.io') || 
                    url.includes('workday.com') || 
                    url.includes('lever.co') || 
                    url.includes('linkedin.com/jobs');
  
  console.log('[AutoResumeFiller] Job site detected:', isJobSite);
  return isJobSite;
}

// Placeholder: Send message to background worker
function notifyBackgroundWorker() {
  if (detectJobApplicationForm()) {
    chrome.runtime.sendMessage(
      { type: 'FORM_DETECTED', payload: { url: window.location.href } },
      (response) => {
        console.log('[AutoResumeFiller] Background worker response:', response);
      }
    );
  }
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', notifyBackgroundWorker);
} else {
  notifyBackgroundWorker();
}
```

**Verification:**
```bash
# Navigate to https://boards.greenhouse.io/example/jobs
# Open DevTools → Console
# Should see: "[AutoResumeFiller] Content script loaded on: ..."
# Should see: "[AutoResumeFiller] Job site detected: true"
```

---

### AC4: Extension Popup Interface Created

**Given** `extension/popup/` directory  
**When** creating popup HTML, CSS, and JavaScript  
**Then** the interface displays backend connection status

**popup.html:**
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
    <h1>AutoResumeFiller</h1>
    
    <div class="status-section">
      <div class="status-label">Backend:</div>
      <div id="backend-status" class="status-value disconnected">Checking...</div>
    </div>
    
    <div class="actions">
      <button id="open-dashboard" class="btn-primary">Open Dashboard</button>
      <button id="reload-status" class="btn-secondary">Reload Status</button>
    </div>
    
    <div class="info">
      <p>Version: <span id="version">1.0.0</span></p>
    </div>
  </div>
  
  <script src="popup.js"></script>
</body>
</html>
```

**popup.css:**
```css
body {
  width: 320px;
  min-height: 200px;
  margin: 0;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
  font-size: 14px;
  background: #f5f5f5;
}

.container {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h1 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.status-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 16px;
  background: #f9f9f9;
  border-radius: 6px;
}

.status-label {
  font-weight: 500;
  color: #666;
}

.status-value {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.status-value.connected {
  background: #d4edda;
  color: #155724;
}

.status-value.disconnected {
  background: #f8d7da;
  color: #721c24;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.info {
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
  color: #666;
}
```

**popup.js:**
```javascript
// extension/popup/popup.js

const statusElement = document.getElementById('backend-status');
const versionElement = document.getElementById('version');
const openDashboardBtn = document.getElementById('open-dashboard');
const reloadStatusBtn = document.getElementById('reload-status');

// Check backend health
async function checkBackendHealth() {
  statusElement.textContent = 'Checking...';
  statusElement.className = 'status-value disconnected';
  
  try {
    const response = await fetch('http://localhost:8765/api/status');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    if (data.status === 'healthy') {
      statusElement.textContent = 'Connected';
      statusElement.className = 'status-value connected';
      versionElement.textContent = data.version || '1.0.0';
    } else {
      throw new Error('Unhealthy status');
    }
  } catch (error) {
    console.error('[AutoResumeFiller] Backend check failed:', error);
    statusElement.textContent = 'Disconnected';
    statusElement.className = 'status-value disconnected';
  }
}

// Open GUI dashboard (placeholder - will launch GUI in future story)
function openDashboard() {
  alert('GUI Dashboard opening feature coming in Story 1.4!');
  // Future: Launch PyQt5 GUI via backend endpoint or native messaging
}

// Event listeners
openDashboardBtn.addEventListener('click', openDashboard);
reloadStatusBtn.addEventListener('click', checkBackendHealth);

// Check health on popup open
checkBackendHealth();
```

**Verification:**
```bash
# Start backend: uvicorn backend.main:app --host 127.0.0.1 --port 8765
# Click extension icon in Chrome toolbar
# Popup should show "Backend: Connected" in green
# Click "Reload Status" → Should re-check and update status
```

---

### AC5: Extension Icons Created

**Given** `extension/icons/` directory  
**When** creating placeholder icons  
**Then** 3 PNG files exist with correct dimensions:

**Icon Specifications:**
- **icon16.png** - 16x16 pixels (toolbar icon)
- **icon48.png** - 48x48 pixels (extension management page)
- **icon128.png** - 128x128 pixels (Chrome Web Store)

**Placeholder Icon Design:**
- Solid background color: #007bff (blue)
- White text: "ARF" (AutoResumeFiller abbreviation)
- Simple, recognizable, professional

**Verification:**
```bash
# Check files exist
ls extension/icons/
# Should show: icon16.png, icon48.png, icon128.png

# Check dimensions (using ImageMagick)
identify extension/icons/icon16.png  # Should show: 16x16
identify extension/icons/icon48.png  # Should show: 48x48
identify extension/icons/icon128.png # Should show: 128x128
```

---

### AC6: Extension Loads Without Errors

**Given** all extension files created  
**When** loading extension in Chrome Developer Mode  
**Then** extension loads successfully with no errors

**Loading Steps:**
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" toggle (top-right)
3. Click "Load unpacked" button
4. Select `AutoResumeFiller/extension/` directory
5. Extension should load with green checkmark (no errors)

**Verification Checklist:**
- ✅ Extension appears in extensions list
- ✅ Extension icon visible in Chrome toolbar
- ✅ No errors shown on extension card
- ✅ Click "Details" → "Inspect views: service worker" → Console shows onInstalled log
- ✅ Click extension icon → Popup opens successfully
- ✅ Navigate to greenhouse.io → Console shows content script injection log

**Common Error Checks:**
```bash
# Check for manifest errors
# chrome://extensions/ → Extension card should NOT show "Manifest errors" or "Service worker (Inactive)"

# If errors appear:
# - Verify manifest.json is valid JSON (use jsonlint.com)
# - Check all file paths in manifest exist (icons, scripts)
# - Ensure service-worker.js has no syntax errors
```

---

### AC7: Content Script Injects on Job Sites

**Given** extension loaded in Chrome  
**When** navigating to supported job application sites  
**Then** content script injects and logs initialization

**Test Sites:**
- https://boards.greenhouse.io/embed/job_board (Greenhouse)
- https://myworkday.com/example/jobs (Workday - requires auth, test on public demo)
- https://jobs.lever.co/example (Lever)
- https://www.linkedin.com/jobs/ (LinkedIn)

**Expected Console Output:**
```
[AutoResumeFiller] Content script loaded on: https://boards.greenhouse.io/...
[AutoResumeFiller] Job site detected: true
[AutoResumeFiller] Background worker response: {received: true, timestamp: 1234567890}
```

**Verification:**
```bash
# For each test site:
# 1. Navigate to URL
# 2. Open DevTools (F12) → Console tab
# 3. Verify content script initialization logs appear
# 4. Open chrome://extensions/ → Extension → Background service worker → Console
# 5. Verify message received logs appear
```

---

### AC8: Backend Communication Validated

**Given** backend running on `localhost:8765` and extension loaded  
**When** clicking extension icon to open popup  
**Then** popup successfully communicates with backend and displays status

**Test Scenario 1: Backend Running**
1. Start backend: `uvicorn backend.main:app --host 127.0.0.1 --port 8765`
2. Click extension icon
3. Popup should show: "Backend: Connected" (green background)

**Test Scenario 2: Backend Stopped**
1. Stop backend (Ctrl+C in terminal)
2. Click extension icon
3. Popup should show: "Backend: Disconnected" (red background)

**Test Scenario 3: Backend Health Check Response**
```javascript
// Open extension popup
// Open DevTools on popup (Right-click → Inspect)
// Console should show:
fetch('http://localhost:8765/api/status')
  .then(r => r.json())
  .then(data => console.log(data));
// Output: {status: "healthy", version: "1.0.0", timestamp: "2025-11-28T...Z"}
```

**Verification:**
```bash
# Backend logs should show CORS request from extension
# uvicorn console output:
INFO:     127.0.0.1:xxxxx - "GET /api/status HTTP/1.1" 200 OK
```

---

## Definition of Done

### Code Complete
- ✅ `extension/manifest.json` created with Manifest V3 schema
- ✅ `extension/background/service-worker.js` implemented with lifecycle listeners
- ✅ `extension/content/content-script.js` implemented with placeholder form detection
- ✅ `extension/popup/popup.html` created with backend status display
- ✅ `extension/popup/popup.css` styled with connected/disconnected states
- ✅ `extension/popup/popup.js` implemented with backend health check
- ✅ `extension/icons/` directory with 3 PNG icons (16x16, 48x48, 128x128)

### Quality Gates
- ✅ Extension loads without errors in Chrome Developer Mode
- ✅ Content script injects on job sites (Greenhouse, Workday, Lever, LinkedIn)
- ✅ Background service worker logs lifecycle events (onInstalled, onStartup)
- ✅ Popup displays "Connected" when backend is running
- ✅ Popup displays "Disconnected" when backend is stopped
- ✅ Console logs show message passing between content script and background worker

### Documentation
- ✅ README.md updated with:
  - Extension installation instructions (Load unpacked in Developer Mode)
  - Supported job sites list (Greenhouse, Workday, Lever, LinkedIn)
  - Troubleshooting section for common extension issues
- ✅ Code comments added to all JavaScript files (describe functions and event listeners)

### Testing
- ✅ Manual test: Load extension in Chrome, verify no errors on extensions page
- ✅ Manual test: Navigate to greenhouse.io, verify content script injection in console
- ✅ Manual test: Open popup with backend running, verify "Connected" status
- ✅ Manual test: Stop backend, open popup, verify "Disconnected" status
- ✅ Manual test: Click service worker "Inspect views", verify onInstalled log

### Version Control
- ✅ All changes committed to git with descriptive message:
  ```
  Story 1.3: Implement Chrome Extension Manifest & Basic Structure
  
  - Created extension/manifest.json with Manifest V3 configuration
  - Implemented background/service-worker.js with lifecycle listeners
  - Implemented content/content-script.js with placeholder form detection
  - Created popup interface (HTML, CSS, JS) with backend status display
  - Added placeholder icons (16x16, 48x48, 128x128)
  - Updated README.md with extension installation instructions
  
  Extension loads successfully in Chrome Developer Mode
  Content script injected on supported job sites
  Popup communicates with backend and displays connection status
  
  Story Status: ready-for-dev → in-progress → review
  ```

---

## Technical Implementation Details

### File Changes Summary

**Files Created:**
1. `extension/manifest.json` (45 lines) - Manifest V3 configuration
2. `extension/background/service-worker.js` (55 lines) - Background service worker
3. `extension/content/content-script.js` (35 lines) - Content script for job sites
4. `extension/popup/popup.html` (30 lines) - Popup HTML structure
5. `extension/popup/popup.css` (90 lines) - Popup styling
6. `extension/popup/popup.js` (50 lines) - Popup backend communication
7. `extension/icons/icon16.png` (binary) - 16x16 toolbar icon
8. `extension/icons/icon48.png` (binary) - 48x48 management icon
9. `extension/icons/icon128.png` (binary) - 128x128 store icon

**Files Modified:**
1. `README.md` (30 lines added) - Extension installation section

**Total Changes:** ~335 lines of code + 3 icon files

---

### Extension Permissions Explained

**storage:**
- Purpose: Store extension settings using `chrome.storage.local` API
- Privacy: Data stored locally only (not synced to Google account)
- Usage: Future - save user preferences, form field mappings

**activeTab:**
- Purpose: Access to currently active tab when user clicks extension icon
- Limited scope: Only works when user interacts with extension (not all tabs)
- Usage: Read current page URL, inject scripts on-demand

**host_permissions: http://localhost:8765/*:**
- Purpose: Allow extension to make fetch() requests to backend API
- Security: Only localhost allowed (no external network access)
- Usage: Backend health check, future API calls (form analysis, AI responses)

---

### Content Script Injection Strategy

**Why `run_at: "document_idle"`:**
- Waits for DOM to fully load before injecting script
- Ensures all form fields are present before detection logic runs
- Balances performance (not too early) and functionality (not too late)

**Why specific site matches:**
- Reduces performance impact (only inject on job sites, not every page)
- Security best practice (principle of least privilege)
- Easier to debug (logs only appear on relevant pages)

**Future Expansion (Epic 4):**
- Add more ATS platforms: *://jobs.ashbyhq.com/*, *://recruiting.ultipro.com/*
- Support custom company career pages with generic detection heuristics

---

### Popup Design Decisions

**Why 320px width:**
- Chrome popup standard size (comfortable for reading, not too wide)
- Fits status display + 2 buttons + version info without scrolling

**Why "Open Dashboard" button:**
- Future integration with PyQt5 GUI (Story 1.4)
- User can launch monitoring dashboard directly from extension
- Implementation: Backend endpoint triggers GUI launch (or native messaging)

**Why separate "Reload Status" button:**
- User can manually re-check backend connection without closing/reopening popup
- Useful for troubleshooting (user starts backend after opening popup)

**Why connected/disconnected colors:**
- Green (#d4edda) for connected: Positive reinforcement, system operational
- Red (#f8d7da) for disconnected: Clear warning, action required
- Follows standard UI conventions (traffic light metaphor)

---

### Common Pitfalls and Solutions

**Pitfall 1: Extension fails to load - "Manifest file is missing or unreadable"**
- **Symptom:** Chrome shows error when loading unpacked extension
- **Cause:** Invalid JSON syntax in manifest.json
- **Solution:**
  ```bash
  # Validate JSON syntax
  cat extension/manifest.json | python -m json.tool
  # Or use online validator: jsonlint.com
  # Common errors: trailing commas, missing quotes, unescaped strings
  ```

**Pitfall 2: Service worker shows "Inactive" status**
- **Symptom:** Background service worker doesn't run, no console logs
- **Cause:** Syntax error in service-worker.js or missing file
- **Solution:**
  ```bash
  # Check file exists
  ls extension/background/service-worker.js
  
  # Check for JavaScript syntax errors
  node --check extension/background/service-worker.js
  
  # View service worker errors:
  # chrome://extensions/ → Extension → Errors button → Check for script errors
  ```

**Pitfall 3: Content script not injecting on job sites**
- **Symptom:** No console logs when visiting greenhouse.io or workday.com
- **Cause:** URL match pattern incorrect, or site requires authentication
- **Solution:**
  ```javascript
  // Debug: Add logging to verify script is loaded
  console.log('[AutoResumeFiller] Content script file loaded');
  
  // Check manifest.json matches array:
  "matches": ["*://*.greenhouse.io/*"]  // Correct: wildcard subdomain
  // NOT: ["https://greenhouse.io/*"]   // Incorrect: missing subdomain
  
  // Test on public job boards without authentication:
  // https://boards.greenhouse.io/embed/job_board
  ```

**Pitfall 4: Popup shows "Disconnected" even when backend is running**
- **Symptom:** Backend responds to curl but extension popup shows red
- **Cause:** CORS blocking extension → backend requests
- **Solution:**
  ```python
  # Verify backend/main.py has CORS middleware:
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["chrome-extension://*"],  # Must include this!
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  
  # Check backend logs for CORS errors:
  # Should see: INFO:     127.0.0.1:xxxxx - "GET /api/status HTTP/1.1" 200 OK
  # NOT: INFO:     127.0.0.1:xxxxx - "OPTIONS /api/status HTTP/1.1" 403 Forbidden
  ```

**Pitfall 5: Icon images not displaying in extension**
- **Symptom:** Extension shows generic gray icon instead of custom icon
- **Cause:** Icon file paths incorrect, or files don't exist
- **Solution:**
  ```bash
  # Verify files exist
  ls extension/icons/icon16.png extension/icons/icon48.png extension/icons/icon128.png
  
  # Check file paths in manifest.json match actual files
  # Paths are relative to extension/ directory
  "icons/icon16.png"  # Correct
  # NOT: "/icons/icon16.png" or "extension/icons/icon16.png"
  
  # Reload extension after adding icons:
  # chrome://extensions/ → Extension → Reload button (circular arrow)
  ```

---

### Tool-Specific Notes

**Chrome Extension Developer Mode:**
```bash
# Enable developer mode
# 1. Open chrome://extensions/
# 2. Toggle "Developer mode" in top-right corner
# 3. Three new buttons appear: "Load unpacked", "Pack extension", "Update"

# Load extension
# 4. Click "Load unpacked"
# 5. Navigate to AutoResumeFiller/extension/ directory
# 6. Click "Select Folder"

# Reload after code changes
# 7. Click circular arrow icon on extension card (or Ctrl+R on extensions page)
```

**Debugging Extension Components:**

**Service Worker Console:**
```bash
# chrome://extensions/ → Extension card → "Inspect views: service worker" (blue link)
# Opens DevTools for background service worker
# Console shows onInstalled, onStartup, onMessage logs
```

**Content Script Console:**
```bash
# Navigate to job site (e.g., greenhouse.io)
# Open DevTools (F12) → Console tab
# Filter logs: Type "[AutoResumeFiller]" in console filter box
# Shows content script initialization and message sending
```

**Popup Console:**
```bash
# Click extension icon to open popup
# Right-click inside popup → "Inspect"
# Opens DevTools for popup window
# Console shows fetch() requests to backend, status updates
```

**Manifest Validation:**
```bash
# Online validator
# https://github.com/GoogleChrome/chrome-extensions-samples/blob/main/functional-samples/tutorial.hello-world/manifest.json
# Compare with official examples

# JSON schema validation (requires Node.js)
npx ajv validate -s https://json.schemastore.org/chrome-manifest.json -d extension/manifest.json
```

---

## Traceability

### Links to Requirements
- **PRD Section 3.1 (Chrome Extension):** Browser automation component for form detection and interaction
- **PRD Section 5.2 (User Interface):** Extension popup for quick status and access to dashboard

### Links to Architecture
- **Architecture Section 4.1 (Extension Structure):** Manifest V3 with content scripts, background service worker, popup
- **Architecture Section 5.1 (Extension → Backend Communication):** HTTP REST API via fetch() to localhost:8765
- **Architecture Section 6.2 (CORS Configuration):** chrome-extension://* origins whitelisted in backend CORS middleware

### Links to Epic
- **Epic 1 Tech Spec Section 4.1 (Extension Manifest):** Manifest V3 schema with permissions, content_scripts, background service worker
- **Epic 1 Tech Spec Section 4.2 (Content Script Injection):** Job site URL patterns (greenhouse.io, workday.com, lever.co, linkedin.com)
- **Epic 1 Tech Spec Section 4.3 (Popup Interface):** Backend status display with connected/disconnected states

### Related Stories
- **Story 1.1:** Project Initialization & Repository Setup (PREREQUISITE - provides extension/ directory)
- **Story 1.2:** Python Backend Scaffolding (PREREQUISITE - provides backend API for popup to communicate with)
- **Story 1.4:** PyQt5 GUI Application Shell (NEXT - popup "Open Dashboard" button will launch GUI)
- **Story 4.1:** Page Detection - Job Application Identifier (BUILDS ON - uses content script from this story)
- **Story 5.1:** Extension-Backend Communication Bridge (BUILDS ON - expands message passing from this story)

---

## Estimates

**Story Points:** 3  
**Estimated Time:** 3-4 hours

**Breakdown:**
- Manifest V3 configuration: 30 minutes
- Background service worker implementation: 45 minutes
- Content script placeholder: 30 minutes
- Popup interface (HTML + CSS + JS): 60 minutes
- Icon creation (3 sizes): 20 minutes
- Extension loading and testing: 30 minutes
- Documentation (README update): 20 minutes
- Git commit and code review prep: 15 minutes

**Risk Factors:**
- ⚠️ First time using Manifest V3 (learning curve for service workers vs. persistent background pages)
- ⚠️ CORS configuration between extension and backend (common gotcha)
- ✅ Chrome extension basics well-documented (official docs, samples)
- ✅ Popup UI is simple (minimal JavaScript, no complex interactions)

**Confidence:** High (75%) - Well-defined scope, clear acceptance criteria, minimal complexity

---

## Notes

### Implementation Tips
1. **Start with manifest.json:** Get extension loading first (even with empty scripts), then implement functionality incrementally
2. **Use placeholder icons:** Don't spend time on icon design now - simple colored squares work for development
3. **Test frequently:** Reload extension after each file change (chrome://extensions/ → Reload button)
4. **Check service worker console:** Most debugging happens in service worker DevTools, not page console
5. **Use console.log liberally:** Extension debugging is harder than web debugging - log everything during development

### Future Enhancements (Out of Scope)
- ❌ Actual form detection logic (Epic 4 - Form Detection & Field Analysis)
- ❌ Communication with AI providers (Epic 3 - AI Provider Integration)
- ❌ Auto-fill functionality (Epic 5 - Intelligent Form Filling)
- ❌ Options page for extension settings (Story 6.4 - Configuration Tab)
- ❌ Native messaging to launch GUI (current: alert placeholder)

### Open Questions
- ✅ **Q:** Should we use chrome.storage.sync or chrome.storage.local for extension settings?  
  **A:** Use chrome.storage.local. Privacy-first design means no cloud sync.

- ✅ **Q:** Do we need content_security_policy in manifest?  
  **A:** Not required for now. Default CSP is sufficient. Add later if we load external resources.

- ✅ **Q:** Should popup ping backend on open, or only on button click?  
  **A:** Ping on open (automatic) AND on reload button click (manual). Better UX - immediate feedback.

---

**Story Drafted By:** SM Agent (Scrum Master)  
**Reviewed By:** PM Agent (Product Manager) [Pending]  
**Approved By:** Ragnar [Pending]  
**Ready for Development:** Yes (Stories 1.1 and 1.2 completed)
