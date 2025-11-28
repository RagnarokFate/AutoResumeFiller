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
