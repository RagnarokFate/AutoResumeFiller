# Epic Technical Specification: Form Detection & Field Analysis

Date: 2025-11-28
Author: Ragnar
Epic ID: 4
Status: Draft

---

## Overview

Epic 4 implements the Form Detection & Field Analysis engine in the Chrome extension, enabling AutoResumeFiller to intelligently identify job application pages, discover all form fields, classify field purposes, detect multi-stage applications, and optimize detection for major ATS platforms (WorkDay, Greenhouse, Lever). The detection engine uses pattern matching, heuristics, and DOM analysis to achieve 95%+ accuracy on supported platforms.

This epic delivers the intelligence layer that bridges the extension content scripts with the backend AI system. Field classification determines whether data should be extracted directly from the user profile or requires AI generation, significantly reducing API costs and improving response times.

This epic enables 16 functional requirements (FR24-FR39) and provides the foundation for form filling automation (Epic 5).

## Objectives and Scope

**In Scope:**
- Job application page detection (WorkDay, Greenhouse, Lever, LinkedIn, generic forms)
- Comprehensive field discovery (text, textarea, select, radio, checkbox, file uploads)
- Label extraction with multiple fallback strategies (label element, aria-label, aria-labelledby, placeholder, heuristics)
- Field purpose classification using pattern matching (95%+ accuracy for common fields)
- Field visibility detection (exclude hidden/disabled fields)
- Multi-stage application detection (progress bars, step indicators, pagination)
- Navigation button detection (Next, Previous, Submit)
- Platform-specific adapters for major ATS systems
- XPath and CSS selector generation for reliable element re-selection
- DOM mutation observer for dynamic forms

**Out of Scope:**
- Actual form filling (Epic 5)
- AI-powered field classification (uses pattern matching for performance)
- Captcha detection/solving (deferred)
- PDF form detection (only HTML forms)
- Non-job-application forms (LinkedIn profiles, settings pages)

**Success Criteria:**
- 95%+ detection accuracy on WorkDay, Greenhouse, Lever
- <500ms initial field discovery time
- 90%+ field label extraction accuracy
- Multi-stage applications detected with <5% false positives
- Zero false positives for non-application pages

## System Architecture Alignment

Epic 4 implements the **Form Detection Layer** in the Chrome extension:

**Component Architecture:**
```
extension/content/
├── page-detector.js         # Identify job application pages
├── form-detector.js         # Discover all form fields
├── field-classifier.js      # Classify field purposes
├── stage-detector.js        # Multi-stage application detection
└── adapters/
    ├── workday-adapter.js   # WorkDay-specific logic
    ├── greenhouse-adapter.js
    └── lever-adapter.js
```

**Detection Flow:**
```
1. Page Load → PageDetector.detectApplicationPage()
   ↓
2. If job application detected:
   ↓
3. FormDetector.discoverAllFields()
   - Find all input, textarea, select elements
   - Extract labels, names, IDs, placeholders
   - Generate XPath and CSS selectors
   - Check visibility
   ↓
4. FieldClassifier.classifyAllFields(fields)
   - Pattern match labels against known purposes
   - Assign data paths (e.g., "personal_info.email")
   - Determine if extraction or generation needed
   ↓
5. StageDetector.detectStages()
   - Find progress indicators
   - Detect navigation buttons
   - Determine current stage number
   ↓
6. Send field metadata to backend
   ↓
7. Backend returns response strategy for each field
   ↓
8. Form Filler (Epic 5) executes filling
```

**Integration Points:**
- Backend API: `POST /api/analyze-form` (send field metadata)
- Background Service Worker: Message passing for state management
- Content Script: DOM manipulation, mutation observers
- User Data: Classification determines extraction path

## Detailed Design

### Services and Modules

| Module | Responsibility | Key Interfaces | Owner |
|--------|---------------|----------------|-------|
| **extension/content/page-detector.js** | Identify job application pages vs non-applications | `detectApplicationPage()`, `getPlatform()`, `getJobContext()` | Extension |
| **extension/content/form-detector.js** | Discover all form fields on page | `discoverAllFields()`, `createFieldDescriptor()`, `findLabel()`, `getXPath()` | Extension |
| **extension/content/field-classifier.js** | Classify field purposes using pattern matching | `classifyField()`, `classifyAllFields()`, `CLASSIFICATION_PATTERNS` | Extension |
| **extension/content/stage-detector.js** | Detect multi-stage applications | `detectStages()`, `detectNavigationButtons()`, `isFinalStage()` | Extension |
| **extension/content/adapters/workday-adapter.js** | WorkDay-specific detection optimizations | `detectFields()`, `detectSection()`, `detectFileUploads()` | Extension |
| **extension/content/adapters/greenhouse-adapter.js** | Greenhouse-specific optimizations | `detectFields()`, `extractFieldMetadata()` | Extension |
| **extension/content/adapters/lever-adapter.js** | Lever-specific optimizations | `detectFields()`, `handleCustomComponents()` | Extension |

### Data Models and Contracts

**Field Descriptor Schema:**
```javascript
{
  id: "field_email_123",              // Unique identifier (generated if no ID)
  type: "text",                       // text, textarea, select, radio, checkbox, file
  name: "email",                      // Field name attribute
  label: "Email Address",             // Extracted label text
  placeholder: "you@example.com",     // Placeholder text
  required: true,                     // Required field flag
  value: "",                          // Current value (empty before filling)
  visible: true,                      // Visibility status
  readonly: false,                    // Read-only flag
  disabled: false,                    // Disabled flag
  pattern: "^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$",  // Validation pattern (if any)
  maxLength: 100,                     // Max length (null if not specified)
  xpath: "/html/body/form/div[2]/input[1]",  // XPath for re-selection
  selector: "input#email.form-control",      // CSS selector
  classification: {                   // Classification result
    purpose: "email",
    dataPath: "personal_info.email",
    confidence: 0.98,
    requiresGeneration: false
  },
  options: [                          // For select/radio fields
    { value: "option1", text: "Option 1" },
    { value: "option2", text: "Option 2" }
  ],
  section: "Personal Information",    // Section/group name (if detected)
  platform: "workday"                 // Detected platform
}
```

**Page Detection Result:**
```javascript
{
  isApplicationPage: true,
  platform: "workday",                // workday, greenhouse, lever, linkedin, generic
  confidence: 0.95,
  jobContext: {
    jobTitle: "Software Engineer",
    company: "Google",
    jobDescription: "...",            // Extracted from page (optional)
    applicationUrl: "https://..."
  },
  detectionMethod: "domain_pattern"   // domain_pattern, page_content, form_structure
}
```

**Stage Detection Result:**
```javascript
{
  isMultiStage: true,
  currentStage: 2,
  totalStages: 5,
  method: "aria_attributes",          // aria_attributes, text_pattern, step_elements
  stageTitles: ["Personal Info", "Work Experience", "Education", "Questions", "Review"],
  navigationButtons: {
    nextButton: <button element>,
    prevButton: <button element>,
    submitButton: null
  },
  isFinalStage: false
}
```

### APIs and Interfaces

**Page Detection API:**
```javascript
class PageDetector {
  static DOMAIN_PATTERNS = {
    workday: /\.myworkdayjobs\.com/,
    greenhouse: /boards\.greenhouse\.io/,
    lever: /jobs\.lever\.co/,
    linkedin: /linkedin\.com\/jobs\/apply/
  };
  
  static PAGE_CONTENT_PATTERNS = {
    application: [
      /application/i,
      /apply.*for.*position/i,
      /submit.*resume/i,
      /job.*application/i
    ],
    profile: [
      /edit.*profile/i,
      /account.*settings/i
    ]
  };
  
  detectApplicationPage() {
    // Check domain first (fastest)
    const hostname = window.location.hostname;
    for (const [platform, pattern] of Object.entries(this.DOMAIN_PATTERNS)) {
      if (pattern.test(hostname)) {
        return {
          isApplicationPage: true,
          platform: platform,
          confidence: 0.98,
          detectionMethod: 'domain_pattern'
        };
      }
    }
    
    // Check page content
    const pageText = document.body.textContent.toLowerCase();
    const title = document.title.toLowerCase();
    
    for (const pattern of this.PAGE_CONTENT_PATTERNS.application) {
      if (pattern.test(pageText) || pattern.test(title)) {
        return {
          isApplicationPage: true,
          platform: 'generic',
          confidence: 0.85,
          detectionMethod: 'page_content'
        };
      }
    }
    
    // Check for form with job-related fields
    if (this.hasJobApplicationFormStructure()) {
      return {
        isApplicationPage: true,
        platform: 'generic',
        confidence: 0.75,
        detectionMethod: 'form_structure'
      };
    }
    
    return { isApplicationPage: false };
  }
  
  hasJobApplicationFormStructure() {
    // Look for forms with typical job application fields
    const forms = document.querySelectorAll('form');
    for (const form of forms) {
      const formText = form.textContent.toLowerCase();
      const hasResumeField = /resume|cv/i.test(formText);
      const hasCoverLetterField = /cover.*letter/i.test(formText);
      const hasWorkExperienceField = /work.*experience|employment.*history/i.test(formText);
      
      if ((hasResumeField || hasCoverLetterField) && hasWorkExperienceField) {
        return true;
      }
    }
    return false;
  }
  
  getJobContext() {
    // Extract job details from page
    const jobTitle = this.extractJobTitle();
    const company = this.extractCompany();
    const jobDescription = this.extractJobDescription();
    
    return {
      jobTitle,
      company,
      jobDescription: jobDescription ? jobDescription.slice(0, 1000) : null,
      applicationUrl: window.location.href
    };
  }
}
```

**Field Discovery API:**
```javascript
class FormDetector {
  discoverAllFields() {
    const fields = [];
    
    // Text inputs
    this.discoverTextFields(fields);
    
    // Textareas
    this.discoverTextareas(fields);
    
    // Select dropdowns
    this.discoverSelectFields(fields);
    
    // Radio buttons (grouped)
    this.discoverRadioFields(fields);
    
    // Checkboxes
    this.discoverCheckboxes(fields);
    
    // File uploads
    this.discoverFileFields(fields);
    
    // Filter out hidden/disabled fields
    return fields.filter(field => field.visible && !field.disabled);
  }
  
  createFieldDescriptor(element, type, extraData = {}) {
    return {
      id: element.id || this.generateFieldId(element),
      type: type,
      name: element.name || '',
      label: this.findLabel(element),
      placeholder: element.placeholder || '',
      required: element.required || element.hasAttribute('aria-required'),
      value: element.value || '',
      visible: this.isVisible(element),
      readonly: element.readOnly,
      disabled: element.disabled,
      pattern: element.pattern || null,
      maxLength: element.maxLength > 0 ? element.maxLength : null,
      xpath: this.getXPath(element),
      selector: this.getUniqueSelector(element),
      ...extraData
    };
  }
  
  findLabel(element) {
    // Strategy 1: Label element
    if (element.labels && element.labels.length > 0) {
      return element.labels[0].textContent.trim();
    }
    
    // Strategy 2: aria-label
    const ariaLabel = element.getAttribute('aria-label');
    if (ariaLabel) return ariaLabel.trim();
    
    // Strategy 3: aria-labelledby
    const labelledBy = element.getAttribute('aria-labelledby');
    if (labelledBy) {
      const labelEl = document.getElementById(labelledBy);
      if (labelEl) return labelEl.textContent.trim();
    }
    
    // Strategy 4: Placeholder
    if (element.placeholder) return element.placeholder.trim();
    
    // Strategy 5: Previous sibling text
    const prevSibling = element.previousElementSibling;
    if (prevSibling && prevSibling.textContent) {
      return prevSibling.textContent.trim();
    }
    
    // Strategy 6: Parent element text
    const parent = element.parentElement;
    if (parent) {
      // Get text nodes only (exclude nested inputs)
      const textNodes = [];
      for (const node of parent.childNodes) {
        if (node.nodeType === Node.TEXT_NODE) {
          textNodes.push(node.textContent.trim());
        }
      }
      if (textNodes.length > 0) {
        return textNodes.join(' ').trim();
      }
    }
    
    // Fallback: Use name or ID
    return element.name || element.id || 'Unknown Field';
  }
  
  getXPath(element) {
    if (element.id) {
      return `//*[@id="${element.id}"]`;
    }
    
    const parts = [];
    while (element && element.nodeType === Node.ELEMENT_NODE) {
      let index = 0;
      let sibling = element.previousSibling;
      
      while (sibling) {
        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === element.tagName) {
          index++;
        }
        sibling = sibling.previousSibling;
      }
      
      const tagName = element.tagName.toLowerCase();
      const pathIndex = index > 0 ? `[${index + 1}]` : '';
      parts.unshift(`${tagName}${pathIndex}`);
      
      element = element.parentNode;
    }
    
    return '/' + parts.join('/');
  }
}
```

**Field Classification API:**
```javascript
class FieldClassifier {
  CLASSIFICATION_PATTERNS = {
    // Personal Information
    first_name: {
      patterns: [/first.*name/i, /given.*name/i, /fname/i],
      dataPath: 'personal_info.first_name',
      confidence: 0.95,
      requiresGeneration: false
    },
    email: {
      patterns: [/e-?mail/i, /contact.*email/i],
      dataPath: 'personal_info.email',
      confidence: 0.98,
      requiresGeneration: false
    },
    // Creative fields
    why_interested: {
      patterns: [/why.*interested/i, /why.*apply/i, /why.*company/i],
      dataPath: null,
      confidence: 0.9,
      requiresGeneration: true
    }
    // ... 50+ more patterns
  };
  
  classifyField(field) {
    const searchText = `${field.label} ${field.name} ${field.id} ${field.placeholder}`.toLowerCase();
    
    let bestMatch = null;
    let highestScore = 0;
    
    for (const [purpose, config] of Object.entries(this.CLASSIFICATION_PATTERNS)) {
      for (const pattern of config.patterns) {
        if (pattern.test(searchText)) {
          let score = config.confidence;
          
          // Type hint bonus
          if (config.type_hint && field.type === config.type_hint) {
            score = Math.min(score + 0.05, 1.0);
          }
          
          if (score > highestScore) {
            highestScore = score;
            bestMatch = {
              purpose: purpose,
              dataPath: config.dataPath,
              confidence: score,
              requiresGeneration: config.requiresGeneration || false
            };
          }
        }
      }
    }
    
    // Default to unknown
    if (highestScore < 0.5) {
      return {
        purpose: 'unknown',
        dataPath: null,
        confidence: 0.0,
        requiresGeneration: true
      };
    }
    
    return bestMatch;
  }
}
```

### Workflows and Sequencing

**Complete Detection Workflow:**
1. User navigates to job application page
2. Content script loads → PageDetector.detectApplicationPage()
3. If not application page → exit, no action
4. If application page → Continue
5. Determine platform (WorkDay, Greenhouse, Lever, generic)
6. Load platform-specific adapter if available
7. FormDetector.discoverAllFields() or Adapter.detectFields()
8. Extract labels for each field (fallback strategies)
9. Generate XPath and CSS selector for each field
10. FieldClassifier.classifyAllFields(fields)
11. StageDetector.detectStages()
12. Compile field metadata payload
13. Send to background service worker
14. Background worker calls `POST /api/analyze-form` to backend
15. Backend validates field data, prepares response strategies
16. Response sent back to content script
17. Content script ready for filling (Epic 5)

**Platform-Specific Adapter Workflow (WorkDay):**
1. PageDetector detects WorkDay domain
2. Load WorkDayAdapter
3. WorkDayAdapter.detectFields() uses data-automation-id attributes
4. Extract section names from WorkDay's section structure
5. WorkDay-specific file upload detection
6. Return fields with enhanced metadata
7. Merge with generic field detector results
8. Continue to classification

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page detection | <50ms | Time from page load to detection complete |
| Field discovery (50 fields) | <500ms | Time to discover and describe all fields |
| Field classification (50 fields) | <100ms | Pattern matching all fields |
| Stage detection | <50ms | Progress indicator analysis |
| DOM mutation handling | <100ms | Re-discovery on dynamic content |

**Rationale:** Fast detection ensures extension doesn't slow down page load or user interaction.

### Accuracy

| Metric | Target | Measurement |
|--------|--------|-------------|
| Application page detection | 99%+ (no false positives) | Manual testing on 100 sites |
| Field discovery completeness | 95%+ (all visible fields found) | Automated field counting vs manual |
| Label extraction accuracy | 90%+ (correct label text) | Manual review of 500 fields |
| Field classification accuracy | 95%+ (correct purpose assigned) | WorkDay, Greenhouse, Lever test suite |
| Multi-stage detection | 95%+ (correct stage identification) | Test on known multi-stage applications |

**False Positives:** Zero tolerance for detecting non-application pages as applications (would annoy users).

### Reliability

| Requirement | Implementation |
|-------------|----------------|
| Graceful degradation | If platform adapter fails, fall back to generic detector |
| DOM mutation resilience | MutationObserver re-runs discovery on content changes |
| XPath fallback | If element removed, use CSS selector; if both fail, skip field |
| Classification fallback | Unknown fields marked for manual review, not auto-filled |

## Dependencies and Integrations

### Chrome Extension APIs

```javascript
// Permissions in manifest.json
{
  "permissions": [
    "activeTab",           // Access current tab
    "storage"              // chrome.storage.local for session state
  ],
  "host_permissions": [
    "http://localhost:8765/*"  // Backend API access
  ]
}
```

### Integration Points

| Epic | Integration | Data Flow |
|------|------------|-----------|
| Epic 1 | Extension manifest, content scripts | Manifest V3 structure |
| Epic 3 | Backend receives field metadata | `POST /api/analyze-form` |
| Epic 5 | Form filler uses field descriptors | Field metadata → Filling logic |

## Acceptance Criteria (Authoritative)

### AC1: Application Page Detection Accurate
**Given** various web pages  
**When** PageDetector.detectApplicationPage() runs  
**Then** WorkDay application pages detected with 98%+ confidence  
**And** Greenhouse application pages detected with 98%+ confidence  
**And** Lever application pages detected with 98%+ confidence  
**And** LinkedIn Easy Apply detected with 95%+ confidence  
**And** Generic job applications detected with 75%+ confidence  
**And** Non-application pages return isApplicationPage: false  
**And** Zero false positives (LinkedIn profile pages, settings pages not detected as applications)

### AC2: All Visible Fields Discovered
**Given** job application form with 50 fields  
**When** FormDetector.discoverAllFields() runs  
**Then** all 50 fields returned in result array  
**And** field types correctly identified (text, textarea, select, radio, checkbox, file)  
**And** hidden fields excluded (display:none, visibility:hidden)  
**And** disabled fields excluded  
**And** readonly fields included but flagged

### AC3: Labels Extracted Correctly
**Given** fields with various label strategies  
**When** FormDetector.findLabel(element) runs  
**Then** <label> element text extracted (Strategy 1)  
**And** aria-label attribute used if no <label> (Strategy 2)  
**And** aria-labelledby reference resolved (Strategy 3)  
**And** Placeholder used if no aria labels (Strategy 4)  
**And** Previous sibling text used as fallback (Strategy 5)  
**And** 90%+ accuracy on real application forms

### AC4: Field Classification Accurate
**Given** discovered fields with labels  
**When** FieldClassifier.classifyField(field) runs  
**Then** email fields classified as "email" with 98%+ confidence  
**And** phone fields classified as "phone" with 95%+ confidence  
**And** name fields classified correctly (first_name, last_name, full_name)  
**And** work experience fields classified with 85%+ confidence  
**And** creative fields (why_interested, tell_about_yourself) marked requiresGeneration: true  
**And** factual fields marked requiresGeneration: false  
**And** unknown fields (confidence <0.5) marked for manual review

### AC5: Multi-Stage Applications Detected
**Given** WorkDay multi-stage application (5 stages)  
**When** StageDetector.detectStages() runs  
**Then** returns isMultiStage: true  
**And** currentStage correct (e.g., 2)  
**And** totalStages correct (e.g., 5)  
**And** stageTitles extracted if available  
**And** navigation buttons detected (Next, Previous, Submit)  
**And** isFinalStage() returns true on last stage  
**And** isFinalStage() returns false on earlier stages

### AC6: Platform Adapters Work
**Given** WorkDay application page  
**When** WorkDayAdapter.detectFields() runs  
**Then** uses data-automation-id attributes for reliable field identification  
**And** section names extracted (e.g., "Personal Information", "Work Experience")  
**And** file upload components detected correctly  
**And** 98%+ field discovery accuracy on WorkDay

**Given** Greenhouse application page  
**When** GreenhouseAdapter.detectFields() runs  
**Then** Greenhouse-specific field naming conventions handled  
**And** 95%+ accuracy on Greenhouse

**Given** Lever application page  
**When** LeverAdapter.detectFields() runs  
**Then** Lever custom components handled  
**And** 95%+ accuracy on Lever

### AC7: XPath and Selectors Generated
**Given** discovered field  
**When** FormDetector.getXPath(element) runs  
**Then** returns valid XPath string  
**And** XPath can re-select element via document.evaluate()  
**When** FormDetector.getUniqueSelector(element) runs  
**Then** returns valid CSS selector  
**And** selector can re-select element via document.querySelector()

### AC8: DOM Mutations Handled
**Given** single-page application with dynamic forms  
**When** new form fields added to DOM  
**Then** MutationObserver triggers re-discovery  
**And** new fields discovered within 100ms  
**And** existing fields not duplicated  
**And** field IDs remain stable across mutations

## Traceability Mapping

| Acceptance Criteria | Spec Section(s) | Component(s) | Test Idea |
|---------------------|----------------|--------------|-----------|
| AC1: Page Detection | APIs → Page Detection | page-detector.js | `test_detect_workday_application()` |
| AC2: Fields Discovered | APIs → Field Discovery | form-detector.js | `test_discover_all_visible_fields()` |
| AC3: Labels Extracted | APIs → Field Discovery | form-detector.js | `test_find_label_strategies()` |
| AC4: Classification | APIs → Field Classification | field-classifier.js | `test_classify_email_field()` |
| AC5: Multi-Stage | Data Models → Stage Detection | stage-detector.js | `test_detect_multistage_workday()` |
| AC6: Platform Adapters | Detailed Design → Modules | adapters/*.js | `test_workday_adapter()` |
| AC7: Selectors | APIs → Field Discovery | form-detector.js | `test_xpath_generation()` |
| AC8: DOM Mutations | NFR → Reliability | form-detector.js | `test_mutation_observer()` |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **R1: Platform UI changes break adapters** | High | Maintain generic fallback; monitor platform changelogs; versioned adapters |
| **R2: False positives annoy users** | High | Conservative detection thresholds; user feedback mechanism; "Not an application?" button |
| **R3: SPA frameworks break DOM selectors** | Medium | Use stable attributes (data-*, aria-*); XPath + CSS selector redundancy; re-discovery on mutations |
| **R4: Label extraction fails on custom components** | Medium | Multiple fallback strategies; heuristic text search; manual classification UI |

### Assumptions

| Assumption | Validation | Impact if Wrong |
|------------|-----------|-----------------|
| **A1: Job applications use standard HTML forms** | Test on 50+ real sites | If React/Angular custom components dominate, need deeper inspection |
| **A2: WorkDay/Greenhouse/Lever maintain consistent DOM structure** | Monitor for breaking changes | Adapter updates required; versioned adapter system |
| **A3: 95% accuracy sufficient for MVP** | User feedback | If users report too many misclassifications, add ML-based classification |

### Open Questions

| Question | Owner | Resolution Target |
|----------|-------|------------------|
| **Q1: Should we add ML-based classification?** | Architect | Deferred to Epic 7; pattern matching sufficient for MVP |
| **Q2: How to handle captchas?** | PM | Out of scope for MVP; document limitation |
| **Q3: Support for PDF application forms?** | PM | Deferred; HTML forms only for MVP |

## Test Strategy Summary

### Test Levels

**Unit Tests (85%+ coverage):**
- PageDetector: Domain patterns, page content patterns, form structure detection
- FormDetector: Field discovery, label extraction, XPath/selector generation
- FieldClassifier: Pattern matching, confidence scoring
- StageDetector: Progress bar parsing, button detection
- Adapters: Platform-specific detection logic

**Integration Tests:**
- Complete detection workflow (page load → fields discovered → classified → sent to backend)
- Platform adapter integration (WorkDay adapter → generic detector fallback)
- DOM mutation handling (field added → re-discovery → classification)

**End-to-End Tests:**
- Real WorkDay application (puppeteer test)
- Real Greenhouse application (puppeteer test)
- Real Lever application (puppeteer test)

### Test Data

**Test Sites:**
- WorkDay demo applications (public demos)
- Greenhouse public job boards
- Lever public job boards
- LinkedIn Easy Apply (real jobs)
- Generic HTML forms (custom test pages)

### Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| page-detector.js | 90% |
| form-detector.js | 85% |
| field-classifier.js | 90% |
| stage-detector.js | 85% |
| Adapters | 80% |

---

## Summary

Epic 4 delivers intelligent form detection with:
- ✅ 99%+ application page detection accuracy
- ✅ 95%+ field discovery completeness
- ✅ 90%+ label extraction accuracy
- ✅ 95%+ field classification accuracy (WorkDay, Greenhouse, Lever)
- ✅ Multi-stage application detection
- ✅ Platform-specific adapters for major ATS systems
- ✅ Robust DOM mutation handling
- ✅ XPath/CSS selector generation for reliable element re-selection

**Next Epic:** Epic 5 (Form Filling Automation) uses the detected field metadata to execute intelligent form filling with user confirmation.

**Status:** Ready for implementation. All acceptance criteria are testable, dependencies are specified, and integration points are clearly defined.
