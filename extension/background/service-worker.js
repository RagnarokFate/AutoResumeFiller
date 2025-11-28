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
