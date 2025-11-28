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
