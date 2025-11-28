# AutoResumeFiller - Architecture Document

**Author:** Winston (Architect) with Ragnar
**Date:** 2025-11-28
**Version:** 1.0
**Project:** AutoResumeFiller

---

## Executive Summary

AutoResumeFiller is a **multi-component desktop application** comprising:
1. **Chrome Extension** (content script + background service) - Form detection and interaction
2. **Python Backend** (Flask/FastAPI HTTP server) - AI orchestration and data management  
3. **Desktop GUI** (Tkinter/PyQt5) - Real-time monitoring and configuration
4. **Local Data Store** (JSON/YAML files) - User personal information repository

The architecture prioritizes **local-first privacy**, **low-latency communication**, and **extensibility** while maintaining simplicity for a solo developer project.

---

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                          User's Machine                          │
│                                                                  │
│  ┌─────────────────┐      HTTP REST      ┌─────────────────┐   │
│  │ Chrome Extension│◄────────────────────►│                 │   │
│  │                 │   localhost:8765     │  FastAPI Backend│   │
│  │ • Content Script│                      │                 │   │
│  │ • Background SW │                      │ • AI Providers  │   │
│  └─────────────────┘                      │ • Data Parser   │   │
│         │                                 │ • Form Processor│   │
│         │ Interacts with                  └────────┬────────┘   │
│         │ Job Sites                                │            │
│         ▼                                          │            │
│  ┌─────────────────┐                              │            │
│  │   Web Browser   │                              │            │
│  │   (Job Sites)   │                              │            │
│  └─────────────────┘                              │            │
│                                                    │            │
│  ┌─────────────────┐      HTTP REST               │            │
│  │   PyQt5 GUI     │◄─────────────────────────────┘            │
│  │   Dashboard     │   localhost:8765                          │
│  │                 │                                            │
│  │ • Real-time Mon │                                            │
│  │ • Config Mgmt   │                                            │
│  │ • Chatbot UI    │                                            │
│  └─────────────────┘                                            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Local File System                            │   │
│  │                                                         │   │
│  │  ~/.autoresumefiller/                                   │   │
│  │  ├── data/                                              │   │
│  │  │   ├── user_profile.json                             │   │
│  │  │   ├── education.json                                │   │
│  │  │   ├── work_experience.json                          │   │
│  │  │   └── skills.json                                   │   │
│  │  ├── resumes/                                           │   │
│  │  │   ├── software_engineer.pdf                         │   │
│  │  │   └── fullstack_developer.pdf                       │   │
│  │  ├── cover_letters/                                     │   │
│  │  ├── config.yaml                                        │   │
│  │  └── logs/                                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  External: AI Provider APIs (OpenAI, Anthropic, Google, etc.)   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

**Backend Framework:**
- **FastAPI** (Python 3.9+)
  - Async/await support for parallel AI API calls
  - Auto-generated OpenAPI documentation
  - Pydantic models for request/response validation
  - Built-in dependency injection
  - WebSocket support (future expansion)

**Desktop GUI:**
- **PyQt5**
  - Modern UI with professional appearance
  - System tray integration
  - QNetworkAccessManager for async HTTP
  - Rich widget library for real-time updates
  - Cross-platform (Windows primary, Mac/Linux future)

**Browser Extension:**
- **Chrome Extension (Manifest V3)**
  - Content scripts for DOM manipulation
  - Background service worker for state management
  - Chrome Storage API for extension settings
  - Native fetch() for HTTP communication

**Data Storage:**
- **JSON/YAML files** (local filesystem)
  - Human-readable for debugging
  - Version control friendly
  - Flexible schema evolution
  - No database dependency

### Supporting Libraries

**Python Backend:**
```python
fastapi>=0.104.0
uvicorn>=0.24.0          # ASGI server
pydantic>=2.5.0          # Data validation
httpx>=0.25.0            # Async HTTP client for AI APIs
PyPDF2>=3.0.0            # PDF parsing
python-docx>=1.1.0       # Word document parsing
python-multipart>=0.0.6  # File upload handling
keyring>=24.3.0          # Secure API key storage
cryptography>=41.0.0     # Data encryption (AES-256)
pyyaml>=6.0              # YAML config parsing
```

**Python GUI:**
```python
PyQt5>=5.15.10
PyQt5-Qt5>=5.15.2
requests>=2.31.0         # HTTP client for backend communication
```

**Chrome Extension:**
```javascript
// No external dependencies - vanilla JS
// Modern browser APIs only
```

**Development Tools:**
```python
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Code Quality
black>=23.11.0           # Code formatting
pylint>=3.0.0            # Linting
mypy>=1.7.0              # Type checking

# Build/Distribution
pyinstaller>=6.3.0       # Executable packaging
```

---

## Architectural Decisions

### Decision 1: Extension-Backend Communication - HTTP REST API

**Decision:** Use HTTP REST API on `localhost:8765` for all extension-backend communication.

**Rationale:**
- **Decoupling**: Extension and GUI can both communicate with backend independently
- **Debuggability**: Standard HTTP tools (curl, Postman, browser DevTools)
- **Development workflow**: Components can be developed and tested in isolation
- **Multi-tab support**: Multiple browser tabs can make independent concurrent requests
- **Portfolio value**: Demonstrates RESTful API design skills
- **Future-proofing**: Easy to add web interface or mobile companion later

**Alternatives Considered:**
- ❌ **Native Messaging**: Complex stdio protocol, platform-specific, exclusive extension access
- ❌ **WebSocket**: Overkill for request-response patterns, adds complexity

**Implementation Details:**
- FastAPI server listens on `127.0.0.1:8765`
- CORS enabled for `chrome-extension://*` origins
- JSON request/response payloads
- RESTful endpoints for resources

**API Endpoints:**
```
POST   /api/analyze-form      # Extension sends form structure
POST   /api/generate-response # Get AI response for specific field
GET    /api/user-data         # Fetch user profile data
POST   /api/user-data/update  # Chatbot updates user data
GET    /api/status            # Health check for GUI
POST   /api/config/ai-provider # Update AI provider settings
```

### Decision 2: GUI Framework - PyQt5

**Decision:** Use PyQt5 for desktop GUI dashboard.

**Rationale:**
- **Professional appearance**: Modern widgets and styling (portfolio showcase)
- **Rich feature set**: System tray, notifications, async networking built-in
- **Real-time updates**: Excellent for displaying live form detection events
- **PyInstaller compatibility**: Bundles well into standalone executable
- **Cross-platform**: Works on Windows/Mac/Linux with same codebase
- **HTTP integration**: QNetworkAccessManager handles async requests cleanly

**Alternatives Considered:**
- ❌ **Tkinter**: Limited styling, looks dated, less suitable for portfolio
- ❌ **Electron**: Larger bundle size, web tech overkill for this use case

**Implementation Details:**
- Single-window application with tabs/sections
- System tray icon for minimized operation
- Real-time event log widget for form detection
- Configuration dialogs for AI providers and data management
- Embedded chatbot interface for data updates

### Decision 3: Backend Framework - FastAPI

**Decision:** Use FastAPI as the Python backend framework.

**Rationale:**
- **Async support**: Critical for parallel AI API calls (multiple form fields)
- **Modern Python**: Leverages type hints and async/await patterns
- **Auto documentation**: OpenAPI/Swagger UI generated automatically
- **Validation**: Pydantic models catch errors at API boundary
- **Performance**: ASGI server faster than traditional WSGI
- **Developer experience**: Excellent for rapid iteration

**Alternatives Considered:**
- ❌ **Flask**: Synchronous by default, manual validation, older patterns
- ❌ **Django**: Too heavyweight, unnecessary ORM and admin features

**Implementation Details:**
- Uvicorn ASGI server
- Pydantic models for all request/response schemas
- Dependency injection for AI provider instances
- Background tasks for long-running operations (future)
- Structured logging with correlation IDs

---

## Data Architecture

### User Data Schema

**Storage Format:** JSON files (default) or YAML (user preference)

**Data Organization Options:**

**Option A: Single Master File** (`user_profile.json`)
```json
{
  "version": "1.0",
  "last_updated": "2025-11-28T10:00:00Z",
  "personal": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-0100",
    "location": {
      "city": "San Francisco",
      "state": "CA",
      "zip": "94102",
      "country": "USA"
    }
  },
  "education": [
    {
      "institution": "Stanford University",
      "degree": "BS",
      "field": "Computer Science",
      "gpa": "3.8",
      "start_date": "2018-09",
      "end_date": "2022-06",
      "achievements": ["Dean's List", "Summa Cum Laude"]
    }
  ],
  "work_experience": [
    {
      "company": "Tech Corp",
      "title": "Senior Software Engineer",
      "location": "San Francisco, CA",
      "start_date": "2022-07",
      "end_date": null,
      "current": true,
      "responsibilities": [
        "Led development of microservices architecture",
        "Mentored junior engineers"
      ],
      "technologies": ["Python", "React", "AWS"]
    }
  ],
  "skills": {
    "programming_languages": ["Python", "JavaScript", "TypeScript", "Go"],
    "frameworks": ["React", "FastAPI", "Django", "Node.js"],
    "tools": ["Docker", "Kubernetes", "Git", "CI/CD"],
    "soft_skills": ["Leadership", "Communication", "Problem Solving"]
  },
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "2023-05",
      "credential_id": "ABC123"
    }
  ],
  "projects": [
    {
      "name": "AutoResumeFiller",
      "description": "AI-powered job application automation tool",
      "technologies": ["Python", "Chrome Extension", "FastAPI", "PyQt5"],
      "url": "https://github.com/username/autoresumefiller"
    }
  ]
}
```

**Option B: Multiple Category Files**
```
data/
├── personal_info.json      # Name, contact, location
├── education.json          # Degrees, institutions, GPAs
├── work_experience.json    # Employment history
├── skills.json             # Technical and soft skills
├── certifications.json     # Professional certifications
└── projects.json           # Portfolio projects
```

**Decision:** Support both, let user choose via config. Default to single file for simplicity.

### Configuration File Schema

**File:** `~/.autoresumefiller/config.yaml`

```yaml
version: "1.0"

# Data preferences
data:
  structure: "single_file"  # or "multiple_files"
  format: "json"            # or "yaml"
  location: "~/.autoresumefiller/data/"
  
# AI provider configuration
ai:
  default_provider: "openai"
  providers:
    openai:
      enabled: true
      model: "gpt-4-turbo-preview"
      api_key_keyring_id: "autoresumefiller_openai"
    anthropic:
      enabled: true
      model: "claude-3-sonnet-20240229"
      api_key_keyring_id: "autoresumefiller_anthropic"
    google:
      enabled: false
      model: "gemini-pro"
      api_key_keyring_id: "autoresumefiller_google"

# Backend server
backend:
  host: "127.0.0.1"
  port: 8765
  auto_start: true
  
# GUI preferences
gui:
  theme: "light"  # or "dark"
  always_on_top: false
  minimize_to_tray: true
  
# Resume files
resumes:
  default: "~/.autoresumefiller/resumes/software_engineer.pdf"
  available:
    - name: "Software Engineer"
      path: "~/.autoresumefiller/resumes/software_engineer.pdf"
    - name: "Full Stack Developer"
      path: "~/.autoresumefiller/resumes/fullstack_developer.pdf"
      
# Cover letters
cover_letters:
  default: "~/.autoresumefiller/cover_letters/default.pdf"
  available:
    - name: "General Tech"
      path: "~/.autoresumefiller/cover_letters/general_tech.pdf"
      
# Logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "~/.autoresumefiller/logs/app.log"
  max_size_mb: 10
  backup_count: 3
```

### Data Encryption

**At Rest:**
- User data files encrypted with AES-256-GCM
- Encryption key derived from OS-specific keyring
- Transparent encryption/decryption in backend

**In Transit:**
- Localhost HTTP (no encryption needed - never leaves machine)
- AI API calls over HTTPS (provider responsibility)

---

## AI Provider Architecture

### Provider Abstraction Layer

**Design Pattern:** Strategy Pattern with async interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        max_tokens: int = 150
    ) -> str:
        """Generate response for a form field"""
        pass
    
    @abstractmethod
    async def extract_data(
        self,
        query: str,
        user_data: Dict[str, Any]
    ) -> Any:
        """Extract specific data from user profile"""
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Verify API key is valid"""
        pass

class OpenAIProvider(AIProvider):
    """OpenAI GPT implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_response(self, prompt, context, max_tokens=150):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a job application assistant."},
                {"role": "user", "content": f"{context}\n\n{prompt}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

class AnthropicProvider(AIProvider):
    """Anthropic Claude implementation"""
    # Similar implementation

class GoogleProvider(AIProvider):
    """Google Gemini implementation"""
    # Similar implementation

class ProviderFactory:
    """Factory for creating AI provider instances"""
    
    @staticmethod
    def create(provider_name: str, api_key: str, model: str) -> AIProvider:
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider
        }
        
        provider_class = providers.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        return provider_class(api_key=api_key, model=model)
```

### AI Processing Pipeline

**Request Flow:**
```
Extension detects form field
    ↓
POST /api/generate-response
    {
      "field_type": "text",
      "field_label": "Why do you want this job?",
      "field_name": "motivation",
      "job_context": {...}
    }
    ↓
Backend analyzes field type
    ↓
┌─────────────────────────────────┐
│  Is it factual extraction?     │
│  (name, date, GPA, etc.)        │
└─────────────────────────────────┘
    │
    ├─YES→ Direct data extraction from user_profile.json
    │      Return: "John Doe"
    │
    └─NO──→ Creative generation needed
            ↓
      Load AI Provider (from config)
            ↓
      Build prompt with context:
        - User's work experience
        - Job description (if available)
        - Field question
            ↓
      Call provider.generate_response()
            ↓
      Return generated text with confidence score
```

### Prompt Engineering Strategy

**Template System:**

```python
PROMPT_TEMPLATES = {
    "motivation": """
Based on this candidate's profile:
{user_summary}

And this job posting:
{job_description}

Generate a concise, genuine answer to: "{question}"

Guidelines:
- 2-3 sentences maximum
- Highlight relevant experience
- Show enthusiasm without hyperbole
- Be specific to this role
""",
    
    "challenge_overcome": """
From this candidate's experience:
{work_experience}

Describe a specific challenge they overcame. Make it concrete and results-oriented.
Question: "{question}"
""",
    
    # More templates...
}
```

---

## Component Architecture

### Chrome Extension Structure

```
extension/
├── manifest.json                 # Extension configuration (Manifest V3)
├── background/
│   └── service-worker.js        # Background service worker
├── content/
│   ├── content-script.js        # DOM manipulation, form detection
│   ├── form-detector.js         # Form field analysis
│   ├── form-filler.js           # Auto-fill logic
│   └── content-styles.css       # Injected styles
├── popup/
│   ├── popup.html               # Extension popup UI
│   ├── popup.js                 # Popup logic
│   └── popup.css                # Popup styles
├── lib/
│   ├── api-client.js            # Backend HTTP client
│   └── utils.js                 # Common utilities
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

**Key Components:**

**Content Script (`content-script.js`):**
- Injected into job application pages
- Detects forms using heuristics (field names, labels, patterns)
- Identifies field types (text, textarea, select, radio, checkbox, file)
- Sends form structure to background worker
- Receives fill instructions and executes DOM manipulation
- Observes DOM mutations for multi-stage forms

**Background Service Worker (`service-worker.js`):**
- Maintains extension state across tabs
- Communicates with FastAPI backend via fetch()
- Manages Chrome Storage API for settings
- Coordinates between multiple content script instances
- Handles extension lifecycle events

**Form Detector (`form-detector.js`):**
```javascript
class FormDetector {
  detectFields(document) {
    // Identify all form inputs
    const fields = [];
    
    // Text inputs
    document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"]')
      .forEach(input => {
        fields.push({
          type: 'text',
          element: input,
          label: this.findLabel(input),
          name: input.name,
          required: input.required,
          pattern: input.pattern,
          placeholder: input.placeholder
        });
      });
    
    // Detect field purpose using multiple signals
    fields.forEach(field => {
      field.purpose = this.identifyPurpose(field);
    });
    
    return fields;
  }
  
  identifyPurpose(field) {
    // Match against known patterns
    const patterns = {
      'first_name': /first.*name|fname|given.*name/i,
      'last_name': /last.*name|lname|surname|family.*name/i,
      'email': /email|e-mail/i,
      'phone': /phone|mobile|telephone/i,
      'address': /address|street/i,
      'city': /city|town/i,
      'zip': /zip|postal/i,
      // ... more patterns
    };
    
    // Check label, name, id, placeholder
    for (const [purpose, pattern] of Object.entries(patterns)) {
      if (pattern.test(field.label) || 
          pattern.test(field.name) ||
          pattern.test(field.element.id) ||
          pattern.test(field.placeholder)) {
        return purpose;
      }
    }
    
    return 'unknown';
  }
}
```

### FastAPI Backend Structure

```
backend/
├── main.py                      # FastAPI app entry point
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── form_processing.py  # Form analysis endpoints
│   │   ├── user_data.py        # User profile CRUD
│   │   ├── ai_provider.py      # AI configuration
│   │   └── health.py           # Health check
│   └── models/
│       ├── requests.py         # Pydantic request models
│       └── responses.py        # Pydantic response models
├── services/
│   ├── ai/
│   │   ├── provider_base.py    # Abstract AI provider
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── google_provider.py
│   │   └── provider_factory.py
│   ├── data/
│   │   ├── user_data_manager.py  # Load/save user data
│   │   ├── encryption.py         # AES-256 encryption
│   │   └── file_parser.py        # PDF/DOCX parsing
│   ├── form_analyzer.py        # Form field analysis
│   └── response_generator.py   # AI prompt construction
├── config/
│   ├── settings.py             # Configuration loading
│   └── logging_config.py       # Structured logging
├── utils/
│   ├── keyring_manager.py      # API key storage
│   └── validators.py           # Data validation
└── tests/
    ├── test_ai_providers.py
    ├── test_form_analyzer.py
    └── test_user_data.py
```

**Key Endpoints:**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AutoResumeFiller Backend API")

class FormField(BaseModel):
    field_type: str
    field_label: str
    field_name: str
    field_purpose: str
    required: bool
    current_value: str | None = None

class AnalyzeFormRequest(BaseModel):
    url: str
    fields: List[FormField]
    job_context: dict | None = None

class GenerateResponseRequest(BaseModel):
    field: FormField
    job_context: dict | None = None
    user_profile_section: str | None = None

@app.post("/api/analyze-form")
async def analyze_form(request: AnalyzeFormRequest):
    """Analyze form structure and prepare filling strategy"""
    # Classify fields, identify missing data, prepare AI prompts
    pass

@app.post("/api/generate-response")
async def generate_response(request: GenerateResponseRequest):
    """Generate AI response for specific field"""
    # Determine if extraction or generation needed
    # Call appropriate AI provider
    # Return response with confidence score
    pass

@app.get("/api/user-data")
async def get_user_data():
    """Retrieve user profile data"""
    pass

@app.post("/api/user-data/update")
async def update_user_data(updates: dict):
    """Update user profile (from chatbot)"""
    pass

@app.get("/api/status")
async def health_check():
    """Backend health check for GUI"""
    return {"status": "healthy", "version": "1.0.0"}
```

### PyQt5 GUI Structure

```
gui/
├── main.py                      # Application entry point
├── windows/
│   ├── main_window.py          # Primary application window
│   ├── config_dialog.py        # Settings/configuration
│   └── chatbot_window.py       # Data update chatbot
├── widgets/
│   ├── event_log.py            # Real-time event display
│   ├── confirmation_panel.py   # Q&A approval widget
│   └── status_bar.py           # Backend connection status
├── services/
│   ├── backend_client.py       # HTTP client for backend API
│   └── system_tray.py          # System tray integration
├── resources/
│   ├── icons/
│   └── styles.qss              # Qt stylesheet
└── utils/
    └── qt_helpers.py           # Qt utility functions
```

**Main Window Design:**

```python
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_backend_polling()
    
    def setup_ui(self):
        # Tab 1: Real-time monitoring
        self.monitor_tab = MonitorTab()
        
        # Tab 2: Data management
        self.data_tab = DataManagementTab()
        
        # Tab 3: Configuration
        self.config_tab = ConfigTab()
        
        # Tab 4: Chatbot
        self.chatbot_tab = ChatbotTab()
        
        tabs = QTabWidget()
        tabs.addTab(self.monitor_tab, "Monitor")
        tabs.addTab(self.data_tab, "My Data")
        tabs.addTab(self.config_tab, "Settings")
        tabs.addTab(self.chatbot_tab, "Update Data")
        
        self.setCentralWidget(tabs)
        
        # System tray
        self.setup_system_tray()
    
    def setup_backend_polling(self):
        """Poll backend for events to display"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_backend_events)
        self.timer.start(500)  # Poll every 500ms
    
    async def check_backend_events(self):
        # GET /api/events (Server-Sent Events or polling)
        # Update monitor_tab with new events
        pass
```

---

## Security Architecture

### Threat Model

**Assets to Protect:**
1. User personal data (resumes, work history, education)
2. AI provider API keys
3. Application configuration
4. Generated responses (potentially sensitive)

**Threat Vectors:**
1. Local file system access by other applications
2. Network interception (mitigated: localhost only)
3. Malicious browser extensions
4. API key theft
5. Data corruption/loss

### Security Controls

**Data at Rest:**
- **Encryption**: AES-256-GCM for all user data files
- **Key Management**: Encryption keys stored in OS keyring
  - Windows: Credential Manager
  - macOS: Keychain
  - Linux: Secret Service (GNOME Keyring, KWallet)
- **File Permissions**: User-only read/write (chmod 600 equivalent)

**API Key Storage:**
```python
import keyring

def store_api_key(provider: str, api_key: str):
    """Securely store API key in OS keyring"""
    service_name = "AutoResumeFiller"
    keyring.set_password(service_name, f"ai_{provider}", api_key)

def retrieve_api_key(provider: str) -> str:
    """Retrieve API key from OS keyring"""
    service_name = "AutoResumeFiller"
    return keyring.get_password(service_name, f"ai_{provider}")
```

**Network Security:**
- **Localhost binding**: Backend only listens on 127.0.0.1 (not 0.0.0.0)
- **CORS policy**: Strict whitelist for chrome-extension:// origins
- **No external exposure**: Firewall not required, nothing listening externally
- **HTTPS for AI APIs**: All external API calls use HTTPS

**Input Validation:**
- **Extension**: Sanitize all DOM-extracted content before sending to backend
- **Backend**: Pydantic models validate all API requests
- **AI responses**: Sanitize before auto-filling (prevent XSS in form fields)

**Extension Security:**
- **Content Security Policy**: Strict CSP in manifest.json
- **Minimal permissions**: Only activeTab, storage, and host permissions for localhost
- **Code review**: All form interactions logged for audit

---

## Deployment & Distribution

### Packaging Strategy

**PyInstaller Configuration:**

```python
# build.spec
a = Analysis(
    ['gui/main.py', 'backend/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/config', 'config'),
        ('gui/resources', 'resources'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.protocols',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoResumeFiller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui/resources/icons/app.ico'
)
```

**Build Process:**

```bash
# Windows
pyinstaller build.spec
# Output: dist/AutoResumeFiller.exe

# macOS (future)
pyinstaller build.spec
# Output: dist/AutoResumeFiller.app

# Linux (future)
pyinstaller build.spec
# Output: dist/AutoResumeFiller
```

### Installation Process

**User Installation Steps:**

1. **Download executable** from GitHub Releases
2. **Run AutoResumeFiller.exe**
   - First launch detects no config
   - Setup wizard appears
3. **Setup Wizard:**
   - Step 1: Choose data directory location
   - Step 2: Configure AI provider(s) - enter API key(s)
   - Step 3: Import resume (PDF/DOCX) or create profile manually
   - Step 4: Install Chrome extension
4. **Extension Installation:**
   - User loads unpacked extension from installation directory
   - Extension connects to backend on localhost:8765
5. **Ready to use!**

**Directory Structure Created:**

```
C:\Users\<username>\.autoresumefiller\  (Windows)
~/.autoresumefiller/                     (Mac/Linux)
├── config.yaml
├── data/
│   └── user_profile.json
├── resumes/
├── cover_letters/
├── logs/
│   └── app.log
└── backups/
```

### Extension Distribution

**Development/Beta:**
- Load unpacked from local directory
- Developer mode in Chrome

**Production (Future):**
- Chrome Web Store submission
- Automated via Chrome Web Store API
- Version sync with main application

---

## Development Workflow

### Repository Structure

```
autoresumefiller/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # GitHub Actions CI
│   │   └── release.yml         # Build and release
│   └── copilot-instructions.md
├── backend/
│   ├── api/
│   ├── services/
│   ├── config/
│   ├── utils/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── gui/
│   ├── windows/
│   ├── widgets/
│   ├── services/
│   ├── resources/
│   ├── main.py
│   └── requirements.txt
├── extension/
│   ├── manifest.json
│   ├── background/
│   ├── content/
│   ├── popup/
│   └── lib/
├── docs/
│   ├── prd.md
│   ├── architecture.md
│   └── api-docs.md
├── scripts/
│   ├── build.py
│   └── test.py
├── tests/
│   └── integration/
├── .gitignore
├── .pylintrc
├── build.spec
├── pyproject.toml
├── README.md
└── LICENSE
```

### Git Workflow (GitFlow)

**Branches:**
- `main` - Production-ready releases
- `develop` - Integration branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation
- `hotfix/*` - Production hotfixes

**Commit Convention:**
```
type(scope): subject

feat(backend): add OpenAI provider integration
fix(extension): correct form detection for WorkDay
docs(architecture): update data schema section
test(backend): add AI provider unit tests
```

### CI/CD Pipeline

**GitHub Actions (`.github/workflows/ci.yml`):**

```yaml
name: CI

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests --cov
      
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install black pylint mypy
      - run: black --check backend/ gui/
      - run: pylint backend/ gui/
      - run: mypy backend/ gui/
  
  test-extension:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install -g eslint
      - run: eslint extension/
```

**Release Build (`.github/workflows/release.yml`):**

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller build.spec
      - uses: actions/upload-artifact@v3
        with:
          name: AutoResumeFiller-Windows
          path: dist/AutoResumeFiller.exe
```

---

## Testing Strategy

### Unit Tests

**Backend (pytest):**
```python
# tests/test_ai_providers.py
import pytest
from backend.services.ai.openai_provider import OpenAIProvider

@pytest.mark.asyncio
async def test_openai_generate_response():
    provider = OpenAIProvider(api_key="test-key", model="gpt-4")
    
    response = await provider.generate_response(
        prompt="Why do you want this job?",
        context={"company": "Tech Corp", "role": "Software Engineer"},
        max_tokens=100
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
```

**Extension (Jest - optional):**
```javascript
// tests/form-detector.test.js
import { FormDetector } from '../extension/content/form-detector';

describe('FormDetector', () => {
  test('identifies email field correctly', () => {
    const detector = new FormDetector();
    const mockField = {
      name: 'email',
      label: 'Email Address',
      type: 'text'
    };
    
    expect(detector.identifyPurpose(mockField)).toBe('email');
  });
});
```

### Integration Tests

```python
# tests/integration/test_full_flow.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_form_filling_flow():
    # 1. Analyze form
    response = client.post("/api/analyze-form", json={
        "url": "https://example.com/apply",
        "fields": [
            {"field_type": "text", "field_label": "First Name", 
             "field_name": "fname", "field_purpose": "first_name", "required": True}
        ]
    })
    assert response.status_code == 200
    
    # 2. Generate response
    response = client.post("/api/generate-response", json={
        "field": {"field_label": "Why this company?", "field_purpose": "motivation"},
        "job_context": {"company": "TechCorp"}
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

### Test Coverage Goals

- **Backend**: 70%+ code coverage
- **Critical paths**: 90%+ (AI providers, data encryption, form processing)
- **Extension**: Manual testing initially, automated E2E with Playwright (future)

---

## Performance Considerations

### Optimization Strategies

**Backend:**
- **Async I/O**: FastAPI async endpoints for concurrent AI API calls
- **Connection pooling**: Reuse HTTP connections to AI providers
- **Caching**: Cache user profile in memory (invalidate on updates)
- **Lazy loading**: Load AI providers on-demand

**Extension:**
- **Debounced DOM observation**: Throttle mutation observer callbacks
- **Incremental form detection**: Analyze fields as they appear, not all at once
- **Minimal DOM manipulation**: Batch updates, use DocumentFragment

**GUI:**
- **Event buffering**: Batch UI updates to reduce repaints
- **Background threads**: Move HTTP requests to QThread
- **Lazy tab loading**: Initialize tabs on first access

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Form detection | <2s | User expects instant recognition |
| AI response generation | <5s | Acceptable wait for quality response |
| GUI update latency | <100ms | Feels real-time |
| Backend cold start | <3s | First request after launch |
| Memory usage (backend) | <500MB | Reasonable for desktop app |
| Extension memory | <100MB | Per tab, browser constraint |

---

## Future Enhancements

### Phase 2 (Post-MVP)

**Local LLM Support:**
- Integrate llama.cpp or Ollama for privacy-focused users
- Fallback to cloud APIs for complex generation
- Model quantization for reasonable memory footprint

**Advanced Form Handling:**
- Computer vision fallback (OCR + screenshot analysis)
- Dynamic form learning (ML model improves with usage)
- Multi-page form context preservation

**Analytics & Insights:**
- Track application success rates
- A/B test response variations
- Identify highest-converting answers

### Phase 3 (Enterprise Features)

**Multi-User Support:**
- Team/agency mode for managing multiple candidates
- Role-based access control
- Shared template library

**Web Dashboard:**
- Remote monitoring via web interface
- Mobile companion app
- Cloud sync (optional, encrypted)

---

## Appendix

### Glossary

- **ATS**: Applicant Tracking System (WorkDay, Greenhouse, Lever, etc.)
- **Content Script**: JavaScript injected into web pages by extension
- **Service Worker**: Background script in Manifest V3 extensions
- **CORS**: Cross-Origin Resource Sharing
- **Pydantic**: Python data validation library
- **PyInstaller**: Python application bundler

### References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Chrome Extension Manifest V3](https://developer.chrome.com/docs/extensions/mv3/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Keyring Library](https://pypi.org/project/keyring/)

---

_This architecture document defines the technical foundation for AutoResumeFiller, providing clear guidance for implementation while maintaining flexibility for evolution. The design prioritizes simplicity, security, and extensibility - perfect for a solo developer project with portfolio showcase goals._

_Architecture decisions made collaboratively between Ragnar (Product Owner) and Winston (Architect)._

