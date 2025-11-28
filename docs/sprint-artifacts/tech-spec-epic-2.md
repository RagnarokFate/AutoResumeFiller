# Epic Technical Specification: Local Data Management System

Date: 2025-11-28
Author: Ragnar
Epic ID: 2
Status: Draft

---

## Overview

Epic 2 implements the local data management system for AutoResumeFiller, enabling users to securely store, manage, and update their personal information on their local machine without cloud dependencies. This epic delivers JSON/YAML data schemas, file system management, PDF/DOCX resume parsing, backup/export functionality, multi-version resume management, configuration persistence, conversational data updates via chatbot, and AES-256 encryption at rest.

The data management system follows a privacy-first architecture where all user data (resumes, work history, education, skills) remains on the user's local filesystem with optional encryption. Users can choose between single master file or multiple category files for data organization. The chatbot interface provides natural language data updates with AI-assisted categorization and completeness validation.

This epic enables 14 functional requirements (FR1-FR7, FR56-FR62) and establishes the data foundation required by all subsequent epics (AI processing, form filling, GUI data management).

## Objectives and Scope

**In Scope:**
- Pydantic data schemas for PersonalInfo, Education, WorkExperience, Skills, Projects, Certifications
- File system data manager with atomic writes, file locking, cross-platform directory support
- PDF parser (pdfplumber) and DOCX parser (python-docx) for resume text extraction
- Section extraction heuristics (Personal Info, Work Experience, Education, Skills, Projects)
- Data export/import with ZIP compression, metadata, integrity verification
- Automated backup system (last 10 backups, timestamped)
- Multiple resume/cover letter version management with tagging and metadata
- Configuration file (config.yaml) with YAML persistence
- Conversational chatbot backend for natural language data updates
- AES-256-GCM encryption at rest with OS keyring integration

**Out of Scope:**
- Cloud storage or synchronization (local-first design)
- Real-time collaboration or multi-user support (single-user application)
- AI-powered resume parsing (uses heuristics; AI enhancement in Epic 3)
- Chatbot UI implementation (Epic 6 - GUI)
- Advanced version control (git integration deferred)

**Success Criteria:**
- User data stored securely with file permissions (user-only read/write)
- Resume parsing achieves 80%+ accuracy for common formats
- Export/import preserves all data integrity (checksum validation)
- Chatbot updates complete user records with 90%+ data completeness
- Encryption/decryption transparent to user (automatic key management)
- Configuration changes persist across application restarts

## System Architecture Alignment

Epic 2 implements the **Local Data Store** layer from the architecture:

**Data Directory Structure:**
```
~/.autoresumefiller/                    # Windows: %APPDATA%\AutoResumeFiller
├── data/
│   ├── user_profile.json               # Main profile (Option A: single file)
│   ├── user_profile.json.enc           # Encrypted version (if encryption enabled)
│   ├── personal_info.json              # Option B: category files
│   ├── education.json
│   ├── work_experience.json
│   ├── skills.json
│   ├── certifications.json
│   └── projects.json
├── resumes/
│   ├── software_engineer.pdf
│   ├── fullstack_developer.pdf
│   └── .metadata.json                  # Resume metadata (tags, defaults)
├── cover_letters/
│   ├── general_cover_letter.pdf
│   └── .metadata.json
├── backups/
│   ├── auto_backup_20251128_100000.zip
│   └── ...                             # Last 10 backups
├── config.yaml                         # Application configuration
└── logs/
    ├── app.log
    └── data_operations.log
```

**Data Flow:**
```
User Input (GUI/Chatbot) → Backend API → DataManager (validation) → Encrypted Storage
                                           ↓
                              Pydantic schemas validate structure
                                           ↓
                              Atomic write (temp file → rename)
                                           ↓
                              File permissions (chmod 600)
```

**Encryption Architecture:**
- User data files encrypted with AES-256-GCM using `cryptography.fernet`
- Encryption key generated on first run, stored in OS keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- Transparent encryption: DataManager encrypts on save, decrypts on load
- Configuration file (config.yaml) remains unencrypted for debuggability (no sensitive data)

**Integration Points:**
- Epic 3 (AI): Reads user_profile.json for response generation context
- Epic 5 (Form Filling): Reads user_profile.json to populate form fields
- Epic 6 (GUI): Data Management Tab displays/edits user_profile.json, Chatbot Tab calls chatbot API

## Detailed Design

### Services and Modules

| Module | Responsibility | Key Interfaces | Owner |
|--------|---------------|----------------|-------|
| **backend/services/data/schemas.py** | Pydantic data models for validation | `PersonalInfo`, `Education`, `WorkExperience`, `Project`, `Certification`, `UserProfile` | Backend |
| **backend/services/data/user_data_manager.py** | File system operations, CRUD for user data | `load_user_profile()`, `save_user_profile()`, `backup_data()`, `export_all()`, `import_from_backup()` | Backend |
| **backend/services/data/file_parser.py** | PDF/DOCX parsing, section extraction | `parse_pdf()`, `parse_docx()`, `extract_sections()`, `extract_email()`, `extract_phone()` | Backend |
| **backend/services/data/encryption.py** | AES-256-GCM encryption/decryption | `encrypt_file()`, `decrypt_file()`, `generate_key()`, `store_key_in_keyring()` | Backend |
| **backend/services/data/version_manager.py** | Resume/cover letter version management | `list_resume_versions()`, `set_default_resume()`, `add_resume_tags()`, `get_resume_by_tags()` | Backend |
| **backend/services/chatbot/chatbot_service.py** | Natural language data updates | `process_message()`, `suggest_data_updates()`, `validate_completeness()` | Backend |
| **backend/config/config_manager.py** | config.yaml CRUD operations | `load_config()`, `save_config()`, `get_setting()`, `update_setting()` | Backend |

### Data Models and Contracts

**Pydantic Schemas (backend/services/data/schemas.py):**
```python
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"

class Education(BaseModel):
    institution: str
    degree: str  # BS, MS, PhD, etc.
    field_of_study: str
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}$')  # YYYY-MM
    end_date: Optional[str] = Field(None, pattern=r'^(\d{4}-\d{2}|Present)$')
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: Optional[List[str]] = []
    relevant_coursework: Optional[List[str]] = []

class WorkExperience(BaseModel):
    company: str
    position: str
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^(\d{4}-\d{2}|Present)$')
    location: Optional[str] = None
    responsibilities: List[str] = Field(..., min_items=1)
    achievements: List[str] = []
    technologies: List[str] = []

class Project(BaseModel):
    name: str
    description: str
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^(\d{4}-\d{2}|Present)$')
    url: Optional[HttpUrl] = None
    technologies: List[str] = []
    highlights: List[str] = []

class Certification(BaseModel):
    name: str
    issuer: str
    date_obtained: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    expiration_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}$')
    credential_id: Optional[str] = None
    url: Optional[HttpUrl] = None

class UserProfile(BaseModel):
    version: str = "1.0"
    personal_info: PersonalInfo
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    skills: List[str] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    summary: Optional[str] = None  # Professional bio
    last_updated: datetime = Field(default_factory=datetime.now)
```

**Configuration Schema (config.yaml):**
```yaml
version: "1.0"

# Data Management
data_directory: "~/.autoresumefiller"
data_structure: "single_file"  # or "multiple_files"
data_format: "json"            # or "yaml"
encryption_enabled: true

# Default Files
default_resume: "software_engineer.pdf"
default_cover_letter: "general_cover_letter.pdf"

# AI Providers (API keys in OS keyring)
ai_providers:
  openai:
    enabled: true
    model: "gpt-4"
    max_tokens: 500
    temperature: 0.7
  anthropic:
    enabled: false
    model: "claude-3-sonnet-20240229"
    max_tokens: 500
  google:
    enabled: false
    model: "gemini-pro"
    max_tokens: 500
  preferred_provider: "openai"

# Backend Server
server:
  host: "127.0.0.1"
  port: 8765
  log_level: "INFO"
  auto_start: true

# GUI Preferences
gui:
  theme: "light"
  always_on_top: false
  minimize_to_tray: true
  show_notifications: true

# Backup Settings
backup:
  auto_backup_enabled: true
  max_backups: 10
  backup_before_import: true

# Logging
logging:
  level: "INFO"
  file_path: "~/.autoresumefiller/logs/app.log"
  max_size_mb: 10
  backup_count: 3
```

### APIs and Interfaces

**Backend REST API Endpoints:**

**1. User Profile Management:**
```
GET    /api/user-data              # Retrieve complete user profile
POST   /api/user-data              # Create/update user profile
PUT    /api/user-data/section      # Update specific section (e.g., work_experience)
DELETE /api/user-data/section/{id} # Delete specific entry

Request (POST /api/user-data):
{
  "personal_info": { ... },
  "education": [ ... ],
  "work_experience": [ ... ],
  ...
}

Response (200 OK):
{
  "success": true,
  "message": "Profile saved successfully",
  "last_updated": "2025-11-28T10:00:00Z"
}
```

**2. File Parsing:**
```
POST   /api/parse-resume           # Upload and parse PDF/DOCX

Request (multipart/form-data):
file: resume.pdf

Response (200 OK):
{
  "success": true,
  "extracted_data": {
    "personal_info": { "name": "John Doe", "email": "...", ... },
    "work_experience": [ ... ],
    "education": [ ... ],
    "skills": [ ... ]
  },
  "confidence": 0.85,
  "warnings": ["Could not parse GPA", "Date format ambiguous"]
}
```

**3. Backup and Export:**
```
POST   /api/backup/create          # Create manual backup
GET    /api/backup/list            # List all backups
POST   /api/export                 # Export all data to ZIP
POST   /api/import                 # Import from ZIP backup

Response (POST /api/backup/create):
{
  "success": true,
  "backup_file": "~/.autoresumefiller/backups/backup_20251128_100000.zip",
  "size_bytes": 245678
}
```

**4. Resume Version Management:**
```
GET    /api/resumes                # List all resume files
POST   /api/resumes/set-default    # Set default resume
POST   /api/resumes/add-tags       # Add tags to resume
GET    /api/resumes/by-tags        # Search resumes by tags

Response (GET /api/resumes):
{
  "resumes": [
    {
      "filename": "software_engineer.pdf",
      "size_bytes": 123456,
      "modified": "2025-11-20T10:00:00Z",
      "tags": ["software", "backend", "python"],
      "is_default": true
    }
  ]
}
```

**5. Chatbot Data Updates:**
```
POST   /api/chatbot/message        # Send message to chatbot
GET    /api/chatbot/history        # Get conversation history
POST   /api/chatbot/approve-update # Approve suggested data update

Request (POST /api/chatbot/message):
{
  "message": "I started a new job at Google as Senior Software Engineer in January 2025",
  "session_id": "uuid-123"
}

Response (200 OK):
{
  "bot_response": "Great! I'll add that to your work experience. Can you tell me more about your responsibilities and achievements?",
  "suggested_update": {
    "section": "work_experience",
    "action": "add",
    "data": {
      "company": "Google",
      "position": "Senior Software Engineer",
      "start_date": "2025-01",
      "end_date": "Present"
    }
  },
  "requires_approval": true
}
```

**6. Configuration Management:**
```
GET    /api/config                 # Get all configuration
PUT    /api/config                 # Update configuration
GET    /api/config/{key}           # Get specific setting
PUT    /api/config/{key}           # Update specific setting

Response (GET /api/config):
{
  "version": "1.0",
  "data_directory": "~/.autoresumefiller",
  "ai_providers": { ... },
  ...
}
```

### Workflows and Sequencing

**User Profile Creation Workflow:**
1. User imports resume PDF via GUI
2. GUI uploads file to `POST /api/parse-resume`
3. Backend extracts text using pdfplumber
4. FileParser.extract_sections() identifies resume sections
5. Pydantic validation normalizes data to UserProfile schema
6. UserDataManager.save_user_profile() writes to user_profile.json
7. If encryption enabled, EncryptionService encrypts file
8. Atomic write (temp file → rename) prevents corruption
9. Auto-backup created in backups/ directory
10. Response sent to GUI with extracted data and warnings
11. GUI displays extracted data for user review/editing

**Chatbot Data Update Workflow:**
1. User types message in chatbot: "I learned React last month"
2. GUI sends `POST /api/chatbot/message`
3. ChatbotService.process_message() analyzes intent
4. AI suggests: Add "React" to skills section
5. Response includes suggested_update with requires_approval=true
6. GUI displays: "I'll add React to your skills. Is this correct?"
7. User approves: GUI sends `POST /api/chatbot/approve-update`
8. Backend validates update against Pydantic schema
9. UserDataManager.load_user_profile() reads current data
10. Append "React" to skills list
11. UserDataManager.save_user_profile() saves updated profile
12. Auto-backup created before save
13. Confirmation sent to GUI: "Skills updated successfully"

**Export and Backup Workflow:**
1. User clicks "Export Data" in GUI
2. GUI calls `POST /api/export`
3. Backend creates temp directory
4. Copy all files: user_profile.json, config.yaml (redacted), resumes/, cover_letters/
5. Generate metadata.json with timestamp, version, checksums
6. Create ZIP archive: autoresumefiller_backup_20251128_100000.zip
7. Move ZIP to user-selected location (Desktop)
8. Return file path to GUI
9. GUI shows success notification with file location

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Profile load time | <100ms | Time from file read to Pydantic validation complete |
| Profile save time | <200ms | Time from validation to atomic write complete (including backup) |
| PDF parsing (10-page resume) | <3 seconds | Time from upload to extracted data response |
| DOCX parsing (10-page resume) | <1 second | python-docx is faster than PDF |
| Export (100MB data) | <10 seconds | ZIP compression and file copy |
| Import (100MB data) | <15 seconds | Extract, validate, copy files |
| Encryption/decryption | <50ms overhead | Per file operation |

**Rationale:** Data operations must be fast to not disrupt user workflow. 3-second PDF parsing is acceptable for one-time import.

### Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| Data encrypted at rest | AES-256-GCM using `cryptography.fernet` | Architecture |
| File permissions | chmod 600 (user-only read/write) on all data files | POSIX best practice |
| API keys never in plaintext | Stored in OS keyring (Windows Credential Manager, macOS Keychain) | Architecture |
| Config file redaction on export | API keys replaced with "***REDACTED***" in exported config.yaml | Privacy requirement |
| Atomic writes prevent corruption | Write to .tmp file, then os.replace() (atomic on POSIX) | Data integrity |

**Threat Model (Epic 2 scope):**
- ✅ **Mitigated:** Local attacker reading unencrypted files (encryption at rest)
- ✅ **Mitigated:** File corruption during concurrent writes (atomic writes, file locking)
- ✅ **Mitigated:** Data loss (auto-backups, export/import)
- ❌ **Out of scope:** Malware with admin privileges (OS-level threat)
- ❌ **Out of scope:** Physical theft of encrypted disk (requires OS keyring compromise)

### Reliability/Availability

| Requirement | Implementation |
|-------------|----------------|
| Data corruption recovery | Auto-backups before any modification; last 10 backups retained |
| Graceful degradation | If encryption fails, warn user and save unencrypted (user approval required) |
| Validation errors | Pydantic catches schema violations; return detailed error messages to GUI |
| File lock conflicts | Retry with exponential backoff (max 3 attempts, 1s, 2s, 4s) |
| Missing directories | Auto-create data directories on first run (mkdir -p equivalent) |

**Availability Target:** 99.9% data write success rate (measured over 1000 operations in testing).

### Observability

| Component | Logging Strategy | Output |
|-----------|-----------------|--------|
| DataManager | Log all CRUD operations with timestamps, file paths, sizes | `~/.autoresumefiller/logs/data_operations.log` |
| FileParser | Log parsing attempts, extraction confidence scores, warnings | Structured JSON logs |
| ChatbotService | Log all messages, intents, suggested updates | Session-based log files |
| EncryptionService | Log encryption/decryption operations (NOT key material) | Security audit log |

**Log Example (data_operations.log):**
```json
{
  "timestamp": "2025-11-28T10:00:00.123Z",
  "level": "INFO",
  "operation": "save_user_profile",
  "file_path": "/home/user/.autoresumefiller/data/user_profile.json",
  "size_bytes": 12345,
  "encrypted": true,
  "backup_created": true,
  "duration_ms": 145
}
```

## Dependencies and Integrations

### Python Dependencies (backend/requirements.txt additions)

```
# Data Validation
pydantic>=2.5.0
pydantic-settings>=2.1.0
email-validator>=2.1.0      # For EmailStr validation

# File Parsing
pdfplumber>=0.10.0          # PDF text extraction
python-docx>=1.0.0          # DOCX parsing
python-dateutil>=2.8.2      # Date parsing

# Encryption
cryptography>=41.0.0        # AES-256-GCM encryption
keyring>=24.3.0             # OS keyring integration

# Configuration
pyyaml>=6.0                 # YAML parsing

# Utilities
python-magic>=0.4.27        # File type detection
```

### System Requirements

| Requirement | Notes |
|-------------|-------|
| OS Keyring | Windows: Credential Manager (built-in), macOS: Keychain (built-in), Linux: Secret Service (gnome-keyring or KWallet) |
| File System | POSIX-compliant for atomic writes (os.replace()), Windows NTFS supported |
| Disk Space | 1GB for user data (resumes, backups) |

### Integration Points

| Epic | Integration | Data Flow |
|------|------------|-----------|
| Epic 1 | Uses settings.py for config | config.yaml → Settings model |
| Epic 3 | AI reads user_profile.json for context | DataManager → AI Service |
| Epic 5 | Form filling reads user_profile.json | DataManager → Form Filler |
| Epic 6 | GUI displays/edits user data | GUI → Data Management API → DataManager |
| Epic 6 | Chatbot UI calls chatbot API | GUI → Chatbot API → ChatbotService → DataManager |

## Acceptance Criteria (Authoritative)

### AC1: Data Schemas Defined and Validated
**Given** Pydantic models in schemas.py  
**When** validating sample user data  
**Then** PersonalInfo, Education, WorkExperience, Project, Certification models validate successfully  
**And** Invalid data raises ValidationError with detailed error messages  
**And** UserProfile.model_json_schema() exports OpenAPI-compatible JSON schema

### AC2: Data Directory Initialized
**Given** first run of application  
**When** DataManager initializes  
**Then** directory structure created at platform-specific location:
- Windows: `%APPDATA%\AutoResumeFiller`
- macOS: `~/Library/Application Support/AutoResumeFiller`
- Linux: `~/.local/share/autoresumefiller`  
**And** subdirectories created: data/, resumes/, cover_letters/, backups/, logs/  
**And** Empty user_profile.json created with minimal structure  
**And** config.yaml created with default settings

### AC3: Profile Load and Save Works
**Given** user_profile.json exists with valid data  
**When** calling DataManager.load_user_profile()  
**Then** UserProfile model returned with all fields populated  
**And** load completes in <100ms  
**When** calling DataManager.save_user_profile(profile)  
**Then** file written atomically (temp file → rename)  
**And** last_updated timestamp auto-updated  
**And** auto-backup created in backups/ directory  
**And** save completes in <200ms

### AC4: PDF Resume Parsing Extracts Data
**Given** PDF resume file (10 pages, single-column layout)  
**When** calling FileParser.parse_pdf(file_path)  
**Then** parsing completes in <3 seconds  
**And** extracted data includes:
- Personal info (name, email, phone) with 90%+ accuracy
- Work experience entries (company, position, dates) with 80%+ accuracy
- Education entries (institution, degree, dates) with 85%+ accuracy
- Skills list with 75%+ accuracy  
**And** warnings logged for ambiguous sections  
**And** confidence score returned (0.0-1.0)

### AC5: DOCX Resume Parsing Extracts Data
**Given** DOCX resume file (10 pages)  
**When** calling FileParser.parse_docx(file_path)  
**Then** parsing completes in <1 second  
**And** extracted data accuracy similar to PDF (80%+ overall)  
**And** handles tables and formatted text correctly

### AC6: Export Creates Complete Backup
**Given** user data exists (profile, resumes, cover letters)  
**When** calling DataManager.export_all()  
**Then** ZIP file created with naming: `autoresumefiller_backup_YYYYMMDD_HHMMSS.zip`  
**And** ZIP contains:
- data/user_profile.json
- config.yaml (with API keys redacted)
- resumes/ directory with all files
- cover_letters/ directory with all files
- metadata.json with timestamp, version, checksums  
**And** export completes in <10 seconds for 100MB data

### AC7: Import Restores from Backup
**Given** exported ZIP backup file  
**When** calling DataManager.import_from_backup(zip_path)  
**Then** ZIP extracted to temp directory  
**And** data validated (JSON parsing, schema validation)  
**And** existing data backed up before import  
**And** user prompted for overwrite confirmation  
**And** all files restored to correct locations  
**And** import completes in <15 seconds

### AC8: Auto-Backup System Works
**Given** auto_backup_enabled=true in config  
**When** any data modification occurs (save, chatbot update)  
**Then** backup created in backups/ directory before modification  
**And** backups/ directory maintains last 10 backups (auto-delete older)  
**And** backup naming: `auto_backup_YYYYMMDD_HHMMSS.zip`

### AC9: Resume Version Management Works
**Given** multiple resume files in resumes/ directory  
**When** calling VersionManager.list_resume_versions()  
**Then** returns list with filename, size, modified date, tags, is_default  
**When** calling VersionManager.set_default_resume("filename.pdf")  
**Then** config.yaml updated with default_resume  
**And** .metadata.json updated with is_default=true  
**When** calling VersionManager.add_resume_tags("filename.pdf", ["backend", "python"])  
**Then** tags saved in .metadata.json  
**When** calling VersionManager.get_resume_by_tags(["python"])  
**Then** returns all resumes with "python" tag

### AC10: Configuration Persists
**Given** config.yaml exists  
**When** calling ConfigManager.load_config()  
**Then** returns dict with all settings  
**When** calling ConfigManager.update_setting("ai_providers.openai.model", "gpt-4-turbo")  
**Then** config.yaml updated  
**And** change persists after application restart  
**And** YAML formatting preserved (comments, indentation)

### AC11: Chatbot Processes Data Updates
**Given** user message: "I started a new job at Google as Senior Engineer in January 2025"  
**When** calling ChatbotService.process_message(message)  
**Then** bot response suggests adding to work_experience section  
**And** suggested_update includes: company="Google", position="Senior Engineer", start_date="2025-01"  
**And** requires_approval=true (user must confirm)  
**When** user approves update  
**Then** UserDataManager.save_user_profile() called with updated data  
**And** auto-backup created  
**And** confirmation message returned

### AC12: Data Encryption Works
**Given** encryption_enabled=true in config  
**When** calling DataManager.save_user_profile(profile)  
**Then** user_profile.json.enc created (encrypted file)  
**And** encryption key stored in OS keyring  
**When** calling DataManager.load_user_profile()  
**Then** file decrypted automatically  
**And** UserProfile model returned with plaintext data  
**And** encryption/decryption adds <50ms overhead

## Traceability Mapping

| Acceptance Criteria | Spec Section(s) | Component(s) | Test Idea |
|---------------------|----------------|--------------|-----------|
| AC1: Schemas Defined | Data Models → Pydantic Schemas | schemas.py | `test_user_profile_validation()` |
| AC2: Directory Initialized | Workflows → User Profile Creation | user_data_manager.py | `test_initialize_data_directory()` |
| AC3: Load/Save Works | APIs → User Profile Management | user_data_manager.py | `test_load_save_profile()` |
| AC4: PDF Parsing | APIs → File Parsing | file_parser.py | `test_parse_pdf_resume()` |
| AC5: DOCX Parsing | APIs → File Parsing | file_parser.py | `test_parse_docx_resume()` |
| AC6: Export Works | APIs → Backup and Export | user_data_manager.py | `test_export_all_data()` |
| AC7: Import Works | APIs → Backup and Export | user_data_manager.py | `test_import_from_backup()` |
| AC8: Auto-Backup | NFR → Reliability | user_data_manager.py | `test_auto_backup_on_save()` |
| AC9: Version Management | APIs → Resume Version Management | version_manager.py | `test_resume_version_management()` |
| AC10: Config Persists | APIs → Configuration Management | config_manager.py | `test_config_persistence()` |
| AC11: Chatbot Updates | APIs → Chatbot Data Updates, Workflows | chatbot_service.py | `test_chatbot_data_update()` |
| AC12: Encryption | NFR → Security, Data Models | encryption.py, user_data_manager.py | `test_encryption_at_rest()` |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **R1: PDF parsing accuracy varies by format** | High | Use pdfplumber (better than PyPDF2); provide manual edit UI; consider AI-powered parsing in Epic 3 |
| **R2: OS keyring unavailable on some Linux distros** | Medium | Detect keyring availability; fall back to encrypted local file with master password |
| **R3: Large resume files (>10MB) slow parsing** | Low | Add file size limit (5MB); optimize pdfplumber settings; show progress bar |
| **R4: Concurrent access from GUI and CLI** | Medium | Implement file locking (fcntl.flock on POSIX, msvcrt.locking on Windows) |
| **R5: Backup directory fills disk space** | Low | Monitor disk space; warn user if <100MB free; auto-delete old backups (keep 10) |

### Assumptions

| Assumption | Validation | Impact if Wrong |
|------------|-----------|-----------------|
| **A1: Users have <100MB of data** | Test with large datasets (500MB) | Performance degradation on export/import; add streaming for large files |
| **A2: Resume PDFs are searchable (not scanned images)** | Test with scanned PDFs | OCR required (tesseract integration); add warning for image-based PDFs |
| **A3: Users keep <50 resume versions** | Test with 100+ resumes | Slow metadata operations; add pagination to version list |
| **A4: Chatbot requires internet for AI** | Offline detection | Chatbot unavailable offline; document requirement in README |
| **A5: Users run single instance of application** | Multi-instance testing | File lock conflicts; add instance detection (PID file) |

### Open Questions

| Question | Owner | Resolution Target |
|----------|-------|------------------|
| **Q1: Should we support LaTeX resume parsing?** | Architect | Deferred to Epic 7; LaTeX less common than PDF/DOCX |
| **Q2: What AI model should chatbot use?** | Epic 3 | Use configured AI provider (OpenAI/Anthropic/Google) |
| **Q3: Should encryption be mandatory or optional?** | Security lead (Ragnar) | Optional by default; warn user if disabled |
| **Q4: How to handle resume parsing failures?** | PM | Show extracted data + errors; allow manual corrections in GUI |
| **Q5: Support for multiple languages (i18n)?** | PM | English only for MVP; i18n deferred to Epic 7 |

## Test Strategy Summary

### Test Levels

**Unit Tests (80%+ coverage target):**
- Pydantic schema validation (valid/invalid data)
- FileParser: PDF extraction, DOCX extraction, section detection, date parsing
- UserDataManager: load, save, atomic writes, backups, export, import
- EncryptionService: encrypt, decrypt, key generation, keyring storage
- VersionManager: list, set default, tag management
- ChatbotService: message processing, intent detection, data updates
- ConfigManager: load, save, get/set settings

**Integration Tests:**
- Complete user profile creation workflow (import PDF → parse → save → load)
- Export and import roundtrip (export → import → validate data integrity)
- Chatbot update workflow (message → suggest → approve → save)
- Encryption roundtrip (encrypt → decrypt → validate plaintext match)

**End-to-End Tests (Epic 6):**
- GUI imports resume → data appears in Data Management Tab
- Chatbot message in GUI → data updated → displayed in GUI

### Testing Frameworks

| Component | Framework | Rationale |
|-----------|-----------|-----------|
| Pydantic models | pytest | Standard Python testing |
| File operations | pytest + tmp_path fixture | Isolated temp directories |
| Encryption | pytest + cryptography test utils | Key generation, cipher testing |

### Test Execution

**Local Development:**
```bash
# Run Epic 2 tests with coverage
pytest backend/services/data/tests/ --cov=backend/services/data --cov-report=html

# Test specific module
pytest backend/services/data/tests/test_file_parser.py

# Test with real resume files
pytest backend/services/data/tests/test_file_parser.py --use-real-files
```

**CI/CD (GitHub Actions):**
```yaml
- name: Test data management
  run: pytest backend/services/data/tests/ --cov=backend/services/data --cov-fail-under=80
```

### Coverage Goals

| Module | Target Coverage | Rationale |
|--------|----------------|-----------|
| schemas.py | 90% | Critical data contracts |
| user_data_manager.py | 85% | Core data operations |
| file_parser.py | 75% | Heuristic-based, harder to test all edge cases |
| encryption.py | 90% | Security-critical |
| chatbot_service.py | 80% | AI-dependent, partial coverage acceptable |

### Edge Cases and Negative Tests

**DataManager:**
- ✅ Corrupted JSON file (invalid syntax) → return error, offer backup restore
- ✅ Missing required fields in JSON → Pydantic ValidationError with details
- ✅ Disk full during save → raise IOError, preserve original file
- ✅ File locked by another process → retry with backoff, fail after 3 attempts

**FileParser:**
- ✅ Encrypted PDF (password-protected) → return error, prompt for password
- ✅ Scanned resume (image-based PDF) → low confidence score, suggest OCR
- ✅ Corrupted PDF → pdfplumber raises error, return parsing failure
- ✅ Non-English resume → parsing works but accuracy lower

**ChatbotService:**
- ✅ Ambiguous message ("I worked at Google") → ask clarifying questions (position? dates?)
- ✅ Invalid date ("I started in Summer 2020") → suggest YYYY-MM format
- ✅ Conflicting data (user already has Google job) → ask if update or new entry

---

## Summary

Epic 2 delivers a robust local data management system with:
- ✅ Type-safe Pydantic schemas (validation built-in)
- ✅ Cross-platform file system manager (atomic writes, backups)
- ✅ Resume parsing (PDF/DOCX) with 80%+ accuracy
- ✅ Export/import with data integrity (checksums)
- ✅ Multiple resume versions with tagging
- ✅ Configuration persistence (YAML)
- ✅ Conversational data updates (chatbot backend)
- ✅ AES-256-GCM encryption at rest

**Next Epic:** Epic 3 (AI Provider Integration & Processing) builds on this data foundation to implement OpenAI, Anthropic, and Google AI providers for form response generation.

**Status:** Ready for implementation. All acceptance criteria are testable, dependencies are specified, and integration points are clearly defined.
