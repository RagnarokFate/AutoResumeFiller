# Story 2.5: Multiple Resume/Cover Letter Version Management

**Story ID:** 2.5  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 2  
**Estimated Effort:** Medium (2-3 days)  
**Priority:** Medium  

---

## User Story

**As a** user  
**I want** to maintain multiple versions of my resume and cover letters  
**So that** I can tailor applications to different job types or industries

---

## Context

This story implements version management for resume and cover letter files. Users can store multiple versions (e.g., "software_engineer_resume.pdf", "data_scientist_resume.pdf"), tag them for easy retrieval, set defaults for auto-uploads, and manage metadata. The system tracks creation dates, file sizes, tags, and default status for each version.

**Current State:**
- Files can be stored in resumes/ and cover_letters/ directories (Story 2.2)
- No version management or metadata

**Desired State:**
- List all resume/cover letter versions with metadata
- Tag versions for categorization (e.g., ["backend", "python", "senior"])
- Set default versions for auto-uploads
- Search by tags
- Metadata stored in `.metadata.json` files

---

## Dependencies

**Prerequisites:**
- Story 2.2: File System Data Manager ✅ (Required - file operations)

---

## Acceptance Criteria

### AC1: List Resume Versions
**Given** multiple resume files in resumes/ directory  
**When** calling `VersionManager.list_resume_versions()`  
**Then** returns list with metadata:
```python
[
  {
    "filename": "software_engineer_resume.pdf",
    "path": Path("~/.autoresumefiller/resumes/software_engineer_resume.pdf"),
    "size_bytes": 245678,
    "created": "2025-11-15T10:00:00Z",
    "modified": "2025-11-20T15:30:00Z",
    "tags": ["software", "backend", "python"],
    "is_default": True
  },
  ...
]
```

### AC2: Set Default Resume
**Given** resume file exists  
**When** calling `VersionManager.set_default_resume("filename.pdf")`  
**Then** `.metadata.json` updated with is_default=True for file  
**And** previous default set to is_default=False  
**And** config.yaml updated: `default_resume: "filename.pdf"`

### AC3: Add Tags to Resume
**Given** resume file exists  
**When** calling `VersionManager.add_resume_tags("filename.pdf", ["backend", "python"])`  
**Then** tags added to file metadata in `.metadata.json`  
**And** duplicate tags prevented  
**And** tags normalized (lowercase, stripped)

### AC4: Search Resumes by Tags
**Given** multiple resumes with tags  
**When** calling `VersionManager.get_resumes_by_tags(["python"])`  
**Then** returns all resumes with "python" tag  
**And** supports AND logic (all tags must match) or OR logic (any tag matches)

### AC5: Cover Letter Version Management
**Given** cover letter files exist  
**When** using VersionManager with cover_letters/ directory  
**Then** same functionality as resumes:
- list_cover_letter_versions()
- set_default_cover_letter()
- add_cover_letter_tags()
- get_cover_letters_by_tags()

### AC6: Metadata Persistence
**Given** metadata changes made  
**When** application restarts  
**Then** metadata persists from `.metadata.json`  
**And** metadata file format:
```json
{
  "version": "1.0",
  "files": {
    "software_engineer_resume.pdf": {
      "tags": ["software", "backend"],
      "is_default": true,
      "notes": "Updated for backend positions"
    }
  }
}
```

---

## Tasks

### Task 1: Create VersionManager Module
- Create `backend/services/data/version_manager.py`
- Implement VersionManager class
- Add methods: list_*, set_default_*, add_tags_*, get_by_tags_*
- Handle both resumes/ and cover_letters/ directories

### Task 2: Implement Metadata Storage
- Create `.metadata.json` format
- Implement save/load metadata methods
- Handle concurrent access with file locking
- Support atomic updates

### Task 3: Implement Version Listing
- Scan directory for files
- Get file stats (size, created, modified)
- Merge with metadata from .metadata.json
- Return sorted list

### Task 4: Implement Tagging
- Add/remove tags from metadata
- Normalize tags (lowercase, strip)
- Prevent duplicates
- Support tag search (AND/OR logic)

### Task 5: Implement Default Management
- Set/unset default flag
- Update config.yaml
- Ensure only one default per type

### Task 6: Create Unit Tests
- Test all methods with sample files
- Test metadata persistence
- Test concurrent access
- Test edge cases (missing files, corrupted metadata)
- Coverage target: >85%

---

## Definition of Done

- [ ] VersionManager implemented for resumes and cover letters
- [ ] list_versions() returns complete metadata
- [ ] set_default() updates metadata and config
- [ ] add_tags() persists tags in metadata
- [ ] get_by_tags() searches correctly
- [ ] Metadata persists across restarts
- [ ] Unit tests >85% coverage
- [ ] All 6 acceptance criteria validated
- [ ] Documentation updated

---

## Traceability

**PRD:** FR5 (Maintain multiple resume versions)  
**Epic Tech Spec:** AC9 (Resume Version Management Works)

