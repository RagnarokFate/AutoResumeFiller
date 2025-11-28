# Epic Technical Specification: Intelligent Form Filling

Date: 2025-11-28
Author: Ragnar
Epic ID: 5
Status: Draft

---

## Overview

Epic 5 implements the Intelligent Form Filling automation engine, enabling AutoResumeFiller to automatically populate detected form fields with user data while maintaining full transparency and user control through a confirmation workflow. The filling engine handles text inputs, dropdowns, radio buttons, checkboxes, file uploads, multi-stage navigation, manual edits, and comprehensive error handling.

The system uses a "generate→preview→approve→fill" workflow, ensuring users review every generated response before submission. Field filling strategies differ based on classification: factual fields are directly extracted from user_profile.json, while creative fields use AI-generated responses from Epic 3.

This epic enables 18 functional requirements (FR56-FR69) and completes the core automation functionality alongside the GUI dashboard (Epic 6).

## Objectives and Scope

**In Scope:**
- Extension-backend API client for form metadata and response generation
- Text input filling with preview and approval
- Dropdown/select field filling with fuzzy matching
- Radio button and checkbox selection
- File upload handling (resume, cover letter)
- Multi-stage navigation with context preservation
- Manual edit detection and preservation
- Error handling with validation feedback
- Field highlighting (preview, success, error states)
- Session state management across stage transitions
- Final submission confirmation modal

**Out of Scope:**
- Captcha solving (deferred)
- Third-party authentication (OAuth, SSO)
- Advanced file types (video portfolios, references)
- Bulk application submission across multiple sites
- A/B testing different response strategies

**Success Criteria:**
- 90%+ successful fill rate for supported field types
- <200ms fill time per field (excluding AI generation)
- Zero unintended form submissions (confirmation required)
- 100% manual edits preserved across navigation
- <5% error rate on dropdown fuzzy matching

## System Architecture Alignment

Epic 5 implements the **Form Filling Layer** in the Chrome extension:

**Filling Flow:**
```
1. User clicks "Start Auto-Fill" in extension popup
   ↓
2. Content script sends field metadata to backend
   POST /api/generate-batch → {fields: [...]}
   ↓
3. Backend processes fields:
   - Factual → Extract from user_profile.json
   - Creative → AI Provider generates response
   ↓
4. Backend returns responses: [{field, value, metadata}]
   ↓
5. Extension displays preview in confirmation panel
   ↓
6. User reviews and approves each field
   ↓
7. FormFiller.fillField(field, value) executes DOM manipulation
   ↓
8. Visual feedback: Field highlighted green (success)
   ↓
9. If multi-stage: Preserve state, navigate to next stage
   ↓
10. Repeat steps 2-9 for each stage
   ↓
11. Final stage: Show submission confirmation modal
   ↓
12. User approves → Extension clicks Submit button
```

**Integration Points:**
- Epic 3: AI provider generates creative responses
- Epic 4: Field metadata (classification, selectors)
- Epic 6: GUI dashboard shows real-time events
- Backend API: Response generation, file serving

## Detailed Design

### Services and Modules

| Module | Responsibility | Key Interfaces |
|--------|---------------|----------------|
| **extension/content/form-filler.js** | Execute DOM manipulation to fill fields | `fillField(field, value)`, `fillTextInput()`, `fillDropdown()`, `fillRadio()`, `fillCheckbox()`, `fillFileInput()` |
| **extension/lib/api-client.js** | Backend HTTP client | `generateResponse(field)`, `generateBatch(fields)`, `getFile(path)` |
| **extension/content/multi-stage-handler.js** | Multi-stage navigation and state | `fillCurrentStage()`, `advanceToNextStage()`, `saveState()`, `restoreState()` |
| **extension/content/manual-edit-handler.js** | Track and preserve manual edits | `observeManualEdits()`, `isManuallyEdited()`, `refillField()` |
| **extension/content/fill-error-handler.js** | Error handling and validation | `handleFillError()`, `showErrorNotification()`, `retryWithBackoff()` |
| **extension/content/confirmation-ui.js** | In-page confirmation panel | `showConfirmationPanel()`, `addFieldPreview()`, `handleApproval()` |

### Key Algorithms

**Dropdown Fuzzy Matching:**
```javascript
function findBestDropdownMatch(targetValue, options) {
  // Strategy 1: Exact match (case-insensitive)
  for (const option of options) {
    if (option.text.toLowerCase() === targetValue.toLowerCase()) {
      return { option, confidence: 1.0, method: 'exact' };
    }
  }
  
  // Strategy 2: Contains match
  for (const option of options) {
    if (option.text.toLowerCase().includes(targetValue.toLowerCase()) ||
        targetValue.toLowerCase().includes(option.text.toLowerCase())) {
      return { option, confidence: 0.8, method: 'contains' };
    }
  }
  
  // Strategy 3: Levenshtein distance (fuzzy)
  let bestMatch = null;
  let lowestDistance = Infinity;
  
  for (const option of options) {
    const distance = levenshteinDistance(
      targetValue.toLowerCase(),
      option.text.toLowerCase()
    );
    
    if (distance < lowestDistance) {
      lowestDistance = distance;
      bestMatch = option;
    }
  }
  
  const confidence = 1 - (lowestDistance / Math.max(targetValue.length, bestMatch.text.length));
  
  if (confidence > 0.6) {
    return { option: bestMatch, confidence, method: 'fuzzy' };
  }
  
  return { option: null, confidence: 0, method: 'no_match' };
}
```

**File Upload Strategy:**
```javascript
async function uploadFile(fileInput, filePath) {
  // Step 1: Request file from backend
  const response = await fetch(`http://localhost:8765/api/files/get?path=${encodeURIComponent(filePath)}`);
  const blob = await response.blob();
  
  // Step 2: Create File object from blob
  const fileName = filePath.split('/').pop();
  const file = new File([blob], fileName, { type: blob.type });
  
  // Step 3: Create DataTransfer to simulate user file selection
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  
  // Step 4: Assign to file input
  fileInput.files = dataTransfer.files;
  
  // Step 5: Trigger change event
  fileInput.dispatchEvent(new Event('change', { bubbles: true }));
  
  return { success: true, fileName };
}
```

### APIs and Interfaces

**Backend Endpoints:**

**1. Generate Single Response:**
```
POST /api/generate-response

Request:
{
  "field": { /* field descriptor from Epic 4 */ },
  "job_context": { "jobTitle": "...", "company": "..." },
  "previous_responses": { "field_id": "value" }
}

Response (200 OK):
{
  "success": true,
  "response": "I'm excited about...",
  "metadata": {
    "provider": "openai",
    "tokens_used": 150,
    "cost_usd": 0.005,
    "cached": false
  }
}
```

**2. Generate Batch:**
```
POST /api/generate-batch

Request:
{
  "fields": [ /* array of field descriptors */ ],
  "job_context": {...},
  "max_parallel": 5
}

Response (200 OK):
{
  "success": true,
  "responses": [
    {
      "field_id": "email_123",
      "value": "john.doe@example.com",
      "source": "extraction",
      "confidence": 1.0
    },
    {
      "field_id": "motivation_456",
      "value": "I'm drawn to this role...",
      "source": "ai_generation",
      "confidence": 0.85,
      "provider": "openai"
    }
  ],
  "summary": {
    "total_fields": 20,
    "extracted": 15,
    "generated": 5,
    "cached": 2,
    "total_cost_usd": 0.045,
    "total_time_ms": 2100
  }
}
```

**3. File Serving:**
```
GET /api/files/get?path={file_path}

Response: Binary file content (application/pdf, etc.)
```

### Workflows and Sequencing

**Complete Filling Workflow:**
1. User opens job application page
2. Extension detects application (Epic 4)
3. User clicks extension icon → "Start Auto-Fill" button
4. Content script discovers all fields (Epic 4)
5. Content script sends `POST /api/generate-batch` with field metadata
6. Backend processes batch:
   - 15 factual fields → extract from user_profile.json (<100ms)
   - 5 creative fields → AI generation (2-3s each, parallelized)
7. Backend returns all 20 responses
8. Content script displays confirmation panel (in-page overlay)
9. For each field:
   - Show field label
   - Show generated value
   - Show "Approve" / "Reject" / "Edit" buttons
10. User reviews and approves fields one-by-one
11. On approval: FormFiller.fillField() executes
12. Field highlighted green with checkmark icon
13. If user clicks "Edit": Switch to manual input mode
14. After all fields filled: Enable "Continue to Next Stage" button
15. User clicks "Continue" → MultiStageHandler.advanceToNextStage()
16. Navigation button clicked programmatically
17. Wait for page update (MutationObserver)
18. Repeat steps 4-17 for next stage
19. On final stage: Show final submission modal
20. User confirms → Click Submit button

## Non-Functional Requirements

### Performance

| Metric | Target |
|--------|--------|
| Text input fill time | <50ms per field |
| Dropdown fill time | <100ms (including fuzzy match) |
| File upload time | <2s (5MB file) |
| Batch filling (20 fields) | <3s (excluding AI generation) |
| State save/restore | <100ms |

### Reliability

| Requirement | Implementation |
|-------------|----------------|
| Zero unintended submissions | Require explicit user confirmation for Submit button |
| Manual edits never overwritten | Track edited fields, skip on re-fill |
| State preserved across navigation | Save to chrome.storage.local after each stage |
| Graceful error recovery | Show error UI, allow manual fill, continue with remaining fields |

### Security

| Requirement | Implementation |
|-------------|----------------|
| No sensitive data in logs | Redact values, log field IDs only |
| CORS validation | Backend enforces chrome-extension://* origin |
| File path validation | Backend restricts to user data directory |

## Acceptance Criteria (Authoritative)

### AC1: Text Input Filling Works
**Given** text field classified as "email"  
**When** FormFiller.fillTextInput(field, "john.doe@example.com")  
**Then** field.element.value set to "john.doe@example.com"  
**And** field highlighted green  
**And** 'input' and 'change' events dispatched  
**And** fill completes in <50ms

### AC2: Dropdown Fuzzy Matching Works
**Given** dropdown with options ["United States", "Canada", "Mexico"]  
**When** target value "USA"  
**Then** "United States" selected (fuzzy match)  
**And** confidence >0.6  
**When** target value "Germany" (not in list)  
**Then** no match, error displayed, user selects manually

### AC3: File Upload Works
**Given** file input for resume  
**When** uploadFile(input, "~/.autoresumefiller/resumes/john_doe_resume.pdf")  
**Then** file fetched from backend  
**And** File object assigned to input.files  
**And** 'change' event fired  
**And** upload completes in <2s

### AC4: Multi-Stage Preserved
**Given** 3-stage application  
**When** filling stage 1 with 10 fields  
**Then** state saved to chrome.storage.local  
**When** advancing to stage 2  
**Then** stage 1 data persists  
**And** can navigate back without re-filling

### AC5: Manual Edits Preserved
**Given** auto-filled field "Why Google?"  
**When** user manually changes text  
**Then** field marked as manually edited  
**And** not overwritten on re-fill  
**And** orange border indicates manual edit

### AC6: Error Handling Works
**Given** dropdown with no matching option  
**When** filling fails  
**Then** field highlighted red  
**And** error tooltip displayed  
**And** user prompted to select manually  
**And** remaining fields continue filling

### AC7: Final Confirmation Required
**Given** final stage of application  
**When** all fields filled  
**Then** "Submit Application" button enabled  
**When** user clicks "Submit Application"  
**Then** modal displayed: "Review and Confirm"  
**And** lists all filled fields  
**And** requires explicit "I confirm" checkbox  
**And** only then clicks Submit button

### AC8: Batch Filling Optimized
**Given** 20 fields (15 factual, 5 creative)  
**When** generating batch responses  
**Then** factual fields extracted immediately (<100ms)  
**And** creative fields generated in parallel (max 5 concurrent)  
**And** total time <5s (including AI calls)

## Traceability Mapping

| Acceptance Criteria | Component(s) | Test Idea |
|---------------------|--------------|-----------|
| AC1: Text Filling | form-filler.js | `test_fill_text_input()` |
| AC2: Dropdown Match | form-filler.js | `test_dropdown_fuzzy_matching()` |
| AC3: File Upload | form-filler.js | `test_file_upload()` |
| AC4: Multi-Stage | multi-stage-handler.js | `test_preserve_state_across_stages()` |
| AC5: Manual Edits | manual-edit-handler.js | `test_manual_edit_detection()` |
| AC6: Error Handling | fill-error-handler.js | `test_handle_fill_error()` |
| AC7: Final Confirmation | multi-stage-handler.js | `test_final_submission_modal()` |
| AC8: Batch Optimization | api-client.js | `test_batch_generate_parallel()` |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| **R1: SPA frameworks break event listeners** | Dispatch all standard events (input, change, blur); test on React/Angular forms |
| **R2: Platform-specific validation fails** | Show validation errors, allow manual correction, don't block submission |
| **R3: File upload rejected by server** | Detect upload failures, retry with different format, fallback to manual |

## Summary

Epic 5 delivers intelligent form filling with:
- ✅ Text, dropdown, radio, checkbox, file upload support
- ✅ Fuzzy matching for dropdown options (90%+ accuracy)
- ✅ Multi-stage navigation with state preservation
- ✅ Manual edit detection and preservation
- ✅ Comprehensive error handling
- ✅ Final submission confirmation (zero unintended submissions)
- ✅ 90%+ successful fill rate

**Next Epic:** Epic 6 (Real-Time Monitoring Dashboard) provides the GUI for monitoring, confirmation, data management, and configuration.

**Status:** Ready for implementation.
