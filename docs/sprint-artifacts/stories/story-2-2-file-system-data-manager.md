# Story 2.2: File System Data Manager

**Story ID:** 2.2  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 1  
**Estimated Effort:** Medium (2-3 days)  
**Priority:** Critical  

---

## User Story

**As a** user  
**I want** my data stored in organized local files with atomic writes and backups  
**So that** I can safely manage, backup, and migrate my information without data loss

---

## Context

This story implements the core file system operations for AutoResumeFiller's local data storage. The UserDataManager provides CRUD operations for user profiles, automatic backups, atomic writes to prevent corruption, and cross-platform directory management. This is a foundational component used by all other Epic 2 stories and throughout the application.

**Current State:**
- Pydantic schemas defined (Story 2.1)
- No file system operations implemented
- Need persistent storage with data integrity

**Desired State:**
- Cross-platform data directory structure
- Atomic file writes (temp file → rename pattern)
- Automatic backups on every save
- Load/save operations completing in <100ms/<200ms
- File permissions set to user-only (chmod 600 equivalent)

---

## Dependencies

**Prerequisites:**
- Story 2.1: Data Schema Definition ✅ (Required - uses Pydantic schemas)
- Story 1.2: Python Backend Scaffolding ✅ (DONE)
- Story 1.6: Testing Infrastructure ✅ (DONE)

**Blocks:**
- Story 2.3: Resume Document Parser (needs load/save)
- Story 2.4: Data Export/Backup (uses backup functionality)
- Story 2.5: Version Management (uses file operations)
- Story 2.8: Data Encryption (integrates with save/load)

---

## Acceptance Criteria

### AC1: Data Directory Initialized
**Given** first run of application  
**When** UserDataManager initializes  
**Then** directory structure created at platform-specific location:
- **Windows:** `%APPDATA%\AutoResumeFiller` (e.g., `C:\Users\<user>\AppData\Roaming\AutoResumeFiller`)
- **macOS:** `~/Library/Application Support/AutoResumeFiller`
- **Linux:** `~/.local/share/autoresumefiller`

**And** subdirectories created:
- `data/` - user profile JSON
- `resumes/` - resume files
- `cover_letters/` - cover letter files
- `backups/` - automatic backups
- `logs/` - application logs

**And** empty `user_profile.json` created with minimal structure:
```json
{
  "version": "1.0",
  "personal_info": null,
  "education": [],
  "work_experience": [],
  "skills": [],
  "projects": [],
  "certifications": [],
  "last_updated": "2025-11-29T10:00:00Z"
}
```

**And** initialization completes in <500ms

### AC2: Profile Load Works
**Given** `user_profile.json` exists with valid data  
**When** calling `UserDataManager.load_user_profile()`  
**Then** UserProfile Pydantic model returned with all fields populated  
**And** JSON deserialization completes successfully  
**And** Pydantic validation passes  
**And** load operation completes in <100ms  
**And** last_updated timestamp parsed correctly

### AC3: Profile Save Works Atomically
**Given** UserProfile instance to save  
**When** calling `UserDataManager.save_user_profile(profile)`  
**Then** data written atomically:
1. Serialize UserProfile to JSON string
2. Write to temporary file: `user_profile.json.tmp`
3. Atomic rename: `user_profile.json.tmp` → `user_profile.json`
4. Delete temp file if rename fails

**And** last_updated timestamp auto-updated to current time  
**And** file permissions set to user-only (0o600 on POSIX)  
**And** save operation completes in <200ms (excluding backup)  
**And** JSON formatted with proper indentation (indent=2)

### AC4: Auto-Backup on Save
**Given** `user_profile.json` exists  
**When** calling `UserDataManager.save_user_profile(profile)`  
**Then** backup created in `backups/` directory **before** save:
- Filename format: `auto_backup_YYYYMMDD_HHMMSS.zip`
- Contains: `user_profile.json` (current version before save)
- Metadata: timestamp, version, source file path

**And** backups directory maintains last 10 backups (oldest auto-deleted)  
**And** backup creation completes in <500ms  
**And** save proceeds even if backup fails (log warning)

### AC5: Manual Backup Works
**Given** user data directory exists  
**When** calling `UserDataManager.backup_data(backup_name)`  
**Then** ZIP file created in `backups/` directory:
- Filename: `{backup_name}_YYYYMMDD_HHMMSS.zip`
- Contains: `data/user_profile.json`, `config.yaml`, `resumes/`, `cover_letters/`
- Metadata file included: `metadata.json` with timestamp, version, file checksums

**And** backup completes in <10 seconds for 100MB data  
**And** ZIP compression level: 6 (balanced speed/size)

### AC6: File Locking Prevents Corruption
**Given** two processes accessing data simultaneously  
**When** one process writes while another reads  
**Then** file locking prevents concurrent writes:
- Use `fcntl.flock()` on POSIX systems
- Use `msvcrt.locking()` on Windows
- Lock acquired before read/write, released after

**And** second writer waits or fails gracefully (timeout: 5 seconds)  
**And** readers can access concurrently (shared lock)  
**And** no data corruption occurs

### AC7: Error Handling for Corrupted Data
**Given** `user_profile.json` exists with invalid JSON  
**When** calling `UserDataManager.load_user_profile()`  
**Then** error raised with clear message: "Failed to parse user_profile.json: {error details}"  
**And** suggests restoring from backup  
**And** lists available backups in `backups/` directory  
**And** no data modification occurs

### AC8: Error Handling for Disk Full
**Given** disk space <10MB available  
**When** calling `UserDataManager.save_user_profile(profile)`  
**Then** error raised: "Insufficient disk space (10MB required)"  
**And** original file preserved (temp file deleted)  
**And** no data corruption occurs  
**And** suggests freeing disk space or changing data directory

### AC9: Cross-Platform Path Handling
**Given** different operating systems  
**When** initializing data directory  
**Then** paths resolved correctly:
- `~` expands to user home directory
- Path separators use `os.path.join()` or `pathlib.Path`
- Platform-specific defaults used (APPDATA on Windows, XDG_DATA_HOME on Linux)

**And** all paths work on Windows, macOS, and Linux  
**And** special characters in paths handled correctly

---

## Tasks

### Task 1: Create UserDataManager Module
**Description:** Set up the module structure for data manager

**Subtasks:**
1. Create file: `backend/services/data/user_data_manager.py`
2. Add imports: pathlib (Path), json, shutil, zipfile, fcntl/msvcrt, datetime
3. Import UserProfile from schemas.py
4. Define UserDataManager class with __init__(data_dir: Optional[Path])
5. Add class constants: DEFAULT_DATA_DIRS (dict for each OS), MAX_BACKUPS = 10

**Acceptance:** Module created and importable

---

### Task 2: Implement Directory Initialization
**Description:** Create data directory structure on first run

**Subtasks:**
1. Implement `_get_default_data_dir()` class method:
   - Windows: `Path(os.environ['APPDATA']) / 'AutoResumeFiller'`
   - macOS: `Path.home() / 'Library' / 'Application Support' / 'AutoResumeFiller'`
   - Linux: `Path.home() / '.local' / 'share' / 'autoresumefiller'`
2. Implement `initialize_data_directory()` method:
   - Create data_dir if not exists (parents=True, exist_ok=True)
   - Create subdirectories: data/, resumes/, cover_letters/, backups/, logs/
   - Create empty user_profile.json if not exists
   - Set directory permissions (0o700 on POSIX)
3. Call `initialize_data_directory()` in __init__ if data_dir doesn't exist
4. Add logging for directory creation

**Acceptance:** Directory structure created correctly on all platforms

---

### Task 3: Implement Profile Load
**Description:** Load and validate user profile from JSON

**Subtasks:**
1. Implement `load_user_profile()` method:
   - Check if user_profile.json exists (raise FileNotFoundError if not)
   - Read JSON file content
   - Parse JSON with proper error handling (json.JSONDecodeError)
   - Validate with UserProfile.model_validate(data)
   - Return UserProfile instance
2. Add file locking (shared lock for reading)
3. Add performance logging (time load operation)
4. Handle corrupted JSON with helpful error messages
5. Suggest backup restoration if load fails

**Acceptance:** Profile loads successfully with validation in <100ms

---

### Task 4: Implement Atomic Profile Save
**Description:** Save profile with atomic writes to prevent corruption

**Subtasks:**
1. Implement `save_user_profile(profile: UserProfile)` method:
   - Update profile.last_updated to current timestamp
   - Serialize to JSON: profile.model_dump_json(indent=2)
   - Write to temp file: user_profile.json.tmp
   - Acquire exclusive lock on temp file
   - Atomic rename: os.replace(temp_path, final_path)
   - Delete temp file if rename fails
2. Set file permissions: 0o600 on POSIX, deny ACLs on Windows
3. Add pre-save backup (call backup_data before write)
4. Add performance logging
5. Handle disk full errors gracefully

**Acceptance:** Save completes atomically in <200ms without corruption

---

### Task 5: Implement Auto-Backup System
**Description:** Create automatic backups before every save

**Subtasks:**
1. Implement `_create_auto_backup()` private method:
   - Generate filename: auto_backup_{timestamp}.zip
   - Copy user_profile.json to temp directory
   - Create ZIP with current user_profile.json
   - Move ZIP to backups/ directory
   - Return backup path
2. Implement `_cleanup_old_backups()` private method:
   - List all backups in backups/ directory
   - Sort by creation time (oldest first)
   - Delete backups beyond MAX_BACKUPS (keep last 10)
3. Call `_create_auto_backup()` at start of save_user_profile()
4. Call `_cleanup_old_backups()` after backup creation
5. Log backup creation and cleanup

**Acceptance:** Auto-backup created before save, old backups cleaned up

---

### Task 6: Implement Manual Backup
**Description:** Create manual backups of all user data

**Subtasks:**
1. Implement `backup_data(backup_name: str = "manual")` method:
   - Generate filename: {backup_name}_{timestamp}.zip
   - Create temp directory
   - Copy user_profile.json, config.yaml, resumes/, cover_letters/ to temp
   - Generate metadata.json with timestamp, version, checksums (SHA256)
   - Create ZIP archive with all files
   - Move ZIP to backups/ directory
   - Clean up temp directory
   - Return backup path
2. Add progress callback for large backups (optional)
3. Add compression level parameter (default: 6)
4. Handle missing files gracefully (e.g., no config.yaml yet)

**Acceptance:** Manual backup creates complete ZIP in <10s for 100MB

---

### Task 7: Implement File Locking
**Description:** Prevent concurrent access corruption

**Subtasks:**
1. Implement `_acquire_lock(file_path: Path, exclusive: bool)` context manager:
   - POSIX: fcntl.flock(fd, fcntl.LOCK_EX or fcntl.LOCK_SH)
   - Windows: msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
   - Timeout: 5 seconds (retry with exponential backoff)
   - Yield file handle
   - Release lock in __exit__
2. Use `_acquire_lock()` in load_user_profile (shared lock)
3. Use `_acquire_lock()` in save_user_profile (exclusive lock)
4. Handle lock timeout with clear error message

**Acceptance:** File locking prevents concurrent write corruption

---

### Task 8: Add Error Handling
**Description:** Handle edge cases and errors gracefully

**Subtasks:**
1. Add try/except blocks for:
   - FileNotFoundError (suggest initialize_data_directory)
   - json.JSONDecodeError (suggest backup restoration)
   - PermissionError (suggest checking file permissions)
   - OSError disk full (suggest freeing space)
   - ValidationError (show which fields failed)
2. Implement `list_available_backups()` method for recovery
3. Add logging for all errors with context
4. Add suggestions in error messages (e.g., "Try: restore from backup")
5. Preserve original data on any error (rollback pattern)

**Acceptance:** All error cases handled with helpful messages

---

### Task 9: Create Unit Tests
**Description:** Write comprehensive unit tests

**Subtasks:**
1. Create `backend/services/data/tests/test_user_data_manager.py`
2. Write test_initialize_data_directory() - verify structure created
3. Write test_load_user_profile_valid() - load valid profile
4. Write test_load_user_profile_corrupted_json() - handle invalid JSON
5. Write test_save_user_profile_atomic() - verify atomic write
6. Write test_save_user_profile_updates_timestamp() - verify auto-update
7. Write test_auto_backup_created_on_save() - verify backup before save
8. Write test_cleanup_old_backups() - verify max 10 backups kept
9. Write test_manual_backup_complete() - verify all files in ZIP
10. Write test_file_locking_prevents_concurrent_writes() - multiprocessing test
11. Write test_disk_full_error_handling() - mock disk full scenario
12. Write test_cross_platform_paths() - parametrize for Windows/macOS/Linux
13. Use pytest fixtures: tmp_path for temporary directories
14. Use pytest-mock for OS-specific behavior

**Acceptance:** All tests pass with >85% coverage

---

### Task 10: Create Integration Tests
**Description:** Test complete workflows

**Subtasks:**
1. Create `backend/services/data/tests/test_integration.py`
2. Write test_complete_profile_lifecycle():
   - Initialize directory
   - Create profile
   - Save profile
   - Load profile
   - Verify data matches
   - Verify backup created
3. Write test_backup_restoration():
   - Create profile
   - Save profile (creates backup)
   - Corrupt user_profile.json
   - Restore from backup
   - Verify data restored
4. Write test_concurrent_access():
   - Spawn multiple processes
   - All try to save simultaneously
   - Verify no corruption
   - Verify all saves complete or timeout gracefully

**Acceptance:** Integration tests pass for complete workflows

---

## Technical Notes

### Atomic Write Pattern
```python
def save_user_profile(self, profile: UserProfile) -> None:
    profile.last_updated = datetime.now()
    temp_path = self.profile_path.with_suffix('.tmp')
    
    # Create auto-backup before save
    self._create_auto_backup()
    
    # Write to temp file
    with self._acquire_lock(temp_path, exclusive=True):
        temp_path.write_text(profile.model_dump_json(indent=2))
    
    # Atomic rename (POSIX: atomic, Windows: nearly atomic)
    os.replace(temp_path, self.profile_path)
    
    # Set permissions
    self.profile_path.chmod(0o600)  # POSIX only
```

### File Locking Context Manager
```python
from contextlib import contextmanager
import fcntl  # POSIX
import msvcrt  # Windows

@contextmanager
def _acquire_lock(self, file_path: Path, exclusive: bool):
    with open(file_path, 'r+b') as f:
        if sys.platform == 'win32':
            lock_mode = msvcrt.LK_NBLCK if exclusive else msvcrt.LK_NBRLCK
            msvcrt.locking(f.fileno(), lock_mode, 1)
        else:
            lock_mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(f.fileno(), lock_mode)
        
        try:
            yield f
        finally:
            if sys.platform != 'win32':
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### Performance Targets
- **Profile load:** <100ms (JSON parse + Pydantic validation)
- **Profile save:** <200ms (serialize + atomic write + permission set)
- **Auto-backup:** <500ms (copy single file to ZIP)
- **Manual backup:** <10s for 100MB (ZIP compression at level 6)

---

## Definition of Done

- [ ] UserDataManager class implemented with all methods
- [ ] Data directory initialized correctly on all platforms (Windows, macOS, Linux)
- [ ] Profile load completes in <100ms with validation
- [ ] Profile save uses atomic writes (temp → rename pattern)
- [ ] Auto-backup created before every save (last 10 kept)
- [ ] Manual backup creates complete ZIP with metadata
- [ ] File locking prevents concurrent write corruption
- [ ] File permissions set to user-only (0o600 on POSIX)
- [ ] All error cases handled with helpful messages
- [ ] Unit tests written with >85% coverage
- [ ] Integration tests pass for complete workflows
- [ ] All 9 acceptance criteria validated
- [ ] Cross-platform compatibility verified
- [ ] Performance targets met (<100ms load, <200ms save)
- [ ] Documentation updated in README

---

## Traceability

**PRD References:**
- FR1: Create and manage local data repository
- FR4: Export complete data repository
- FR7: Configure default data directory location

**Architecture References:**
- Section: System Architecture → Data Directory Structure
- Component: backend/services/data/user_data_manager.py

**Epic Tech Spec:**
- AC2: Data Directory Initialized
- AC3: Profile Load and Save Works
- AC8: Auto-Backup System Works
- Section: Services and Modules → user_data_manager.py

---

## Notes

- Atomic writes prevent corruption even if process crashes during save
- File locking is OS-specific: fcntl (POSIX) vs msvcrt (Windows)
- Windows doesn't support POSIX chmod, use ACLs or file attributes
- Auto-backups keep last 10 to prevent disk space issues
- Manual backups include metadata for integrity verification
- Consider adding async variants for large file operations (future enhancement)
