# Story 2.4: Data Export & Backup Functionality

**Story ID:** 2.4  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 2  
**Estimated Effort:** Medium (2-3 days)  
**Priority:** High  

---

## User Story

**As a** user  
**I want** to export and backup my complete data repository  
**So that** I can migrate to another machine or safeguard against data loss

---

## Context

This story extends the basic backup functionality from Story 2.2 to provide comprehensive export and import capabilities. Users can create complete backups of their data (profile, resumes, cover letters, config) with metadata and integrity verification. The system supports import/restoration from these backups with validation and user confirmation before overwriting existing data.

**Current State:**
- Auto-backup on save exists (Story 2.2)
- No manual export or import functionality
- No integrity verification for backups

**Desired State:**
- Manual export creates complete ZIP with all user data
- Metadata includes timestamp, version, checksums for integrity
- Import validates and restores from backup
- Export completes in <10 seconds for 100MB
- Import completes in <15 seconds with validation

---

## Dependencies

**Prerequisites:**
- Story 2.1: Data Schema Definition ✅ (Required - validates imported data)
- Story 2.2: File System Data Manager ✅ (Required - uses backup infrastructure)

**Optional Dependencies:**
- Story 2.6: Configuration Management (config.yaml export/import)
- Story 2.8: Data Encryption (encrypted backups)

---

## Acceptance Criteria

### AC1: Manual Export Creates Complete Backup
**Given** populated user data (profile, resumes, cover letters)  
**When** calling `UserDataManager.export_all(output_path)`  
**Then** ZIP file created with naming: `autoresumefiller_backup_YYYYMMDD_HHMMSS.zip`  

**And** ZIP contains:
- `data/user_profile.json` (or encrypted .enc version)
- `config.yaml` with API keys redacted
- `resumes/` directory with all files
- `cover_letters/` directory with all files
- `metadata.json` with:
  - Export timestamp (ISO 8601)
  - Application version
  - File checksums (SHA256 for each file)
  - File sizes
  - Total backup size

**And** export completes in <10 seconds for 100MB data  
**And** ZIP compression level: 6 (balanced speed/size)  
**And** returns backup metadata dict

### AC2: Export Handles Missing Directories
**Given** some directories don't exist (e.g., no cover_letters/)  
**When** calling export_all()  
**Then** export succeeds with warnings:
- Missing directories skipped
- Warning logged: "cover_letters/ directory not found, skipping"
- metadata.json includes list of missing directories

**And** export doesn't fail for missing optional data

### AC3: Import Validates Backup Before Restoration
**Given** exported ZIP backup file  
**When** calling `UserDataManager.import_from_backup(zip_path)`  
**Then** validation performed:
1. **ZIP integrity:** Verify ZIP not corrupted
2. **Metadata validation:** Parse metadata.json successfully
3. **Version compatibility:** Check version ≤ current version
4. **Checksum verification:** Validate all file checksums match
5. **Schema validation:** Validate user_profile.json against UserProfile schema
6. **File size verification:** Check files match expected sizes

**And** validation completes before any data modification  
**And** validation errors returned with clear messages:
- "Backup is corrupted (ZIP error)"
- "Version mismatch: backup v2.0, current v1.0"
- "Checksum mismatch for user_profile.json"
- "Invalid user profile schema"

### AC4: Import Prompts for Overwrite Confirmation
**Given** existing user data present  
**When** validation passes during import  
**Then** user prompted for confirmation:
```
Existing data found. Import will:
- Replace user_profile.json (last modified: 2025-11-20)
- Replace 5 resume files
- Replace 2 cover letter files
- Backup existing data before import? [Y/n]

Continue with import? [y/N]
```

**And** existing data backed up to backups/ directory before import (if user chooses)  
**And** import aborted if user declines  
**And** no data modified if user declines

### AC5: Import Restores All Data
**Given** validated backup and user confirmation  
**When** import proceeds  
**Then** all files restored:
1. Extract ZIP to temp directory
2. Backup existing data (if requested)
3. Copy user_profile.json → data/
4. Copy resumes/* → resumes/
5. Copy cover_letters/* → cover_letters/
6. Copy config.yaml → ./ (merge settings, preserve API keys)
7. Verify checksums after copy
8. Clean up temp directory

**And** import completes in <15 seconds for 100MB  
**And** returns import summary:
```python
{
  "success": true,
  "files_restored": 12,
  "backup_created": "backups/pre_import_backup_20251129_120000.zip",
  "warnings": ["API keys not imported (preserved existing)"],
  "duration_ms": 8500
}
```

### AC6: Export Redacts Sensitive Data
**Given** config.yaml with API keys  
**When** exporting config.yaml  
**Then** API keys redacted:
```yaml
# Original config.yaml
ai_providers:
  openai:
    api_key: "sk-abc123..."
    
# Exported config.yaml
ai_providers:
  openai:
    api_key: "**REDACTED**"
```

**And** other settings preserved  
**And** comment added: "# API keys redacted for security"

### AC7: List Available Backups
**Given** multiple backups in backups/ directory  
**When** calling `UserDataManager.list_backups()`  
**Then** returns list of all backups sorted by date (newest first):
```python
[
  {
    "filename": "autoresumefiller_backup_20251129_120000.zip",
    "path": Path("~/.autoresumefiller/backups/autoresumefiller_backup_20251129_120000.zip"),
    "size_bytes": 245678,
    "created": "2025-11-29T12:00:00Z",
    "type": "manual",  # or "auto"
    "metadata": {...}  # Parsed from ZIP if available
  },
  ...
]
```

**And** listing completes in <1 second for 100 backups

### AC8: Delete Old Backups
**Given** backup list  
**When** calling `UserDataManager.delete_backup(backup_path)`  
**Then** backup file deleted from filesystem  
**And** confirmation returned  
**And** operation is irreversible (user warned)

**When** calling `UserDataManager.cleanup_old_backups(max_backups=10, keep_manual=True)`  
**Then** auto-backups beyond max_backups deleted  
**And** manual backups preserved (if keep_manual=True)  
**And** returns count of deleted backups

### AC9: Export Progress for Large Backups
**Given** large data set (>500MB)  
**When** calling export_all with progress callback  
**Then** progress updates returned:
```python
def progress_callback(current_bytes, total_bytes, current_file):
    progress = (current_bytes / total_bytes) * 100
    print(f"Exporting: {current_file} ({progress:.1f}%)")

export_all(output_path, progress_callback=progress_callback)
```

**And** callback invoked for each file  
**And** export can be cancelled (raise exception in callback)

---

## Tasks

### Task 1: Extend UserDataManager with Export
**Description:** Add export_all method to UserDataManager

**Subtasks:**
1. Implement `export_all(output_path: Optional[Path] = None, progress_callback=None)` method
2. Generate filename: autoresumefiller_backup_{timestamp}.zip
3. Create temp directory for staging files
4. Copy user_profile.json to temp
5. Copy resumes/ directory to temp (if exists)
6. Copy cover_letters/ directory to temp (if exists)
7. Copy config.yaml to temp with API key redaction
8. Generate metadata.json with checksums, version, timestamp
9. Create ZIP archive from temp directory
10. Move ZIP to output_path or backups/
11. Clean up temp directory
12. Return export metadata

**Acceptance:** Export creates complete ZIP with all data

---

### Task 2: Implement Metadata Generation
**Description:** Generate metadata.json for backups

**Subtasks:**
1. Implement `_generate_metadata(files: List[Path])` helper:
   - Calculate SHA256 checksum for each file
   - Get file sizes
   - Get current timestamp
   - Get application version (from settings or package)
   - List all included files
2. Create metadata.json structure:
```json
{
  "export_timestamp": "2025-11-29T12:00:00Z",
  "app_version": "1.0.0",
  "total_size_bytes": 245678,
  "files": [
    {
      "path": "data/user_profile.json",
      "size_bytes": 12345,
      "checksum_sha256": "abc123..."
    },
    ...
  ],
  "missing_directories": ["cover_letters"],
  "notes": "API keys redacted for security"
}
```
3. Write metadata.json to backup

**Acceptance:** Metadata includes all required information

---

### Task 3: Implement API Key Redaction
**Description:** Redact sensitive data from config.yaml

**Subtasks:**
1. Implement `_redact_config(config_path: Path, output_path: Path)` helper:
   - Load config.yaml with PyYAML
   - Find all fields named "api_key", "secret", "password"
   - Replace values with "**REDACTED**"
   - Add comment: "# API keys redacted for security"
   - Preserve YAML formatting
   - Write to output_path
2. Test with various config structures
3. Ensure non-sensitive settings preserved

**Acceptance:** API keys redacted, other settings preserved

---

### Task 4: Implement Import Validation
**Description:** Validate backup before import

**Subtasks:**
1. Implement `_validate_backup(zip_path: Path)` method:
   - Check ZIP file exists and is readable
   - Extract to temp directory
   - Parse metadata.json
   - Check version compatibility
   - Verify checksums for all files
   - Validate user_profile.json against schema
   - Verify file sizes match metadata
2. Collect all validation errors
3. Return validation result dict:
```python
{
  "valid": True,
  "errors": [],
  "warnings": ["Version mismatch (minor)"],
  "metadata": {...}
}
```
4. Raise exception if validation fails

**Acceptance:** Validation catches corrupted, incompatible, or invalid backups

---

### Task 5: Implement Import with Confirmation
**Description:** Import backup with user confirmation

**Subtasks:**
1. Implement `import_from_backup(zip_path: Path, confirm=True, backup_existing=True)` method:
   - Validate backup
   - If existing data present and confirm=True:
     - Display data to be overwritten
     - Prompt for confirmation (CLI input or callback)
   - If backup_existing=True:
     - Create backup of existing data
   - Extract ZIP to temp directory
   - Copy files to correct locations
   - Verify checksums after copy
   - Clean up temp directory
2. Add confirmation callback parameter for GUI integration
3. Return import summary dict
4. Handle errors during import (rollback if possible)

**Acceptance:** Import works with confirmation and existing data backup

---

### Task 6: Implement Backup Listing
**Description:** List and manage backups

**Subtasks:**
1. Implement `list_backups()` method:
   - Scan backups/ directory
   - Find all ZIP files
   - Parse metadata from each ZIP (if available)
   - Sort by creation time (newest first)
   - Return list of backup dicts
2. Implement `delete_backup(backup_path: Path)` method:
   - Verify backup exists
   - Delete file
   - Return confirmation
3. Implement `cleanup_old_backups(max_backups=10, keep_manual=True)` method:
   - List all backups
   - Separate auto vs manual backups (by filename pattern)
   - Delete oldest auto backups beyond max_backups
   - Preserve manual backups if keep_manual=True
   - Return count of deleted backups

**Acceptance:** Backup management works correctly

---

### Task 7: Add Progress Reporting
**Description:** Report progress for large exports

**Subtasks:**
1. Add progress_callback parameter to export_all()
2. Calculate total size before export
3. Invoke callback for each file copied:
   - current_bytes (cumulative)
   - total_bytes
   - current_file (filename)
4. Allow cancellation (catch exception in callback)
5. Test with large data sets (>500MB)

**Acceptance:** Progress callback invoked correctly

---

### Task 8: Create API Endpoints
**Description:** Add REST API endpoints for export/import

**Subtasks:**
1. Create `backend/api/backup.py`:
   - POST /api/backup/create (manual export)
   - POST /api/backup/import (import from upload)
   - GET /api/backup/list (list all backups)
   - DELETE /api/backup/{filename} (delete backup)
2. Handle file uploads for import
3. Return progress updates via SSE or WebSocket
4. Add authentication if needed
5. Add error handling and validation

**Acceptance:** API endpoints work for export/import

---

### Task 9: Create Unit Tests
**Description:** Write comprehensive unit tests

**Subtasks:**
1. Create `backend/services/data/tests/test_export_import.py`
2. Write test_export_all_complete() - export with all data
3. Write test_export_missing_directories() - handle missing dirs
4. Write test_generate_metadata() - verify metadata structure
5. Write test_redact_config() - verify API key redaction
6. Write test_validate_backup_success() - valid backup
7. Write test_validate_backup_corrupted() - corrupted ZIP
8. Write test_validate_backup_version_mismatch() - version check
9. Write test_validate_backup_checksum_fail() - invalid checksum
10. Write test_import_with_confirmation() - user confirms
11. Write test_import_backup_existing() - backup existing data
12. Write test_list_backups() - list multiple backups
13. Write test_delete_backup() - delete single backup
14. Write test_cleanup_old_backups() - delete old auto-backups
15. Write test_export_progress_callback() - progress reporting
16. Use pytest fixtures: tmp_path, sample backups

**Acceptance:** All tests pass with >85% coverage

---

### Task 10: Create Integration Tests
**Description:** Test complete export/import workflows

**Subtasks:**
1. Create `backend/services/data/tests/test_backup_integration.py`
2. Write test_export_import_roundtrip():
   - Create sample data
   - Export to ZIP
   - Delete original data
   - Import from ZIP
   - Verify data matches
3. Write test_import_overwrites_existing():
   - Create original data
   - Create different data
   - Export different data
   - Import backup
   - Verify different data restored
4. Write test_corrupted_backup_recovery():
   - Create backup
   - Corrupt ZIP file
   - Attempt import
   - Verify error handling
5. Test with large data sets (>500MB)

**Acceptance:** Integration tests pass for complete workflows

---

## Technical Notes

### ZIP Archive Structure
```
autoresumefiller_backup_20251129_120000.zip
├── metadata.json
├── data/
│   └── user_profile.json
├── config.yaml
├── resumes/
│   ├── software_engineer.pdf
│   └── fullstack_developer.pdf
└── cover_letters/
    └── general_cover_letter.pdf
```

### Checksum Calculation
```python
import hashlib

def calculate_checksum(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()
```

### API Key Redaction
```python
import re
import yaml

def redact_config(config: dict) -> dict:
    redacted = config.copy()
    for key, value in redacted.items():
        if isinstance(value, dict):
            redacted[key] = redact_config(value)
        elif key in ['api_key', 'secret', 'password', 'token']:
            redacted[key] = '**REDACTED**'
    return redacted
```

---

## Definition of Done

- [ ] export_all() creates complete ZIP with all data
- [ ] Export includes metadata with checksums, version, timestamp
- [ ] Export redacts API keys from config.yaml
- [ ] Export handles missing directories gracefully
- [ ] Export completes in <10 seconds for 100MB
- [ ] import_from_backup() validates backup before import
- [ ] Import prompts for confirmation if existing data present
- [ ] Import backs up existing data before overwrite
- [ ] Import restores all files and verifies checksums
- [ ] Import completes in <15 seconds for 100MB
- [ ] list_backups() returns all backups sorted by date
- [ ] delete_backup() removes backup files
- [ ] cleanup_old_backups() maintains max backup count
- [ ] Progress callback works for large exports
- [ ] API endpoints created for GUI integration
- [ ] Unit tests written with >85% coverage
- [ ] Integration tests pass for complete workflows
- [ ] All 9 acceptance criteria validated
- [ ] Documentation updated with examples

---

## Traceability

**PRD References:**
- FR4: Export complete data repository for backup or migration

**Architecture References:**
- Component: backend/services/data/user_data_manager.py
- Section: APIs and Interfaces → Backup and Export

**Epic Tech Spec:**
- AC6: Export Creates Complete Backup
- AC7: Import Restores from Backup
- AC8: Auto-Backup System Works

---

## Notes

- ZIP compression level 6 balances speed and size
- Checksum verification ensures data integrity
- API key redaction prevents accidental exposure
- Consider encrypting backups in Story 2.8
- Consider cloud sync in future epic (out of scope for MVP)
- Progress reporting enables better UX for large backups
