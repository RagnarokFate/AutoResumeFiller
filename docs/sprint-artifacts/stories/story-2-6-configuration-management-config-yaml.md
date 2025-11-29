# Story 2.6: Configuration Management (config.yaml)

**Story ID:** 2.6  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 2  
**Estimated Effort:** Small (1-2 days)  
**Priority:** High  

---

## User Story

**As a** user  
**I want** my application settings persisted in a configuration file  
**So that** my preferences are maintained across application restarts

---

## Context

This story implements configuration file management using YAML format. The config.yaml file stores application settings (AI providers, data directory, encryption, defaults) and persists across restarts. The ConfigManager provides CRUD operations with validation and default initialization.

**Current State:**
- Settings stored in backend/config/settings.py (Story 1.3)
- No persistent user preferences
- Config not exportable

**Desired State:**
- config.yaml stores user preferences
- Settings persist across restarts
- Get/set operations with validation
- Default config on first run
- YAML formatting preserved (comments, indentation)

---

## Dependencies

**Prerequisites:**
- Story 1.3: Settings Management ✅ (Integrates with existing settings)
- Story 2.2: File System Data Manager ✅ (Uses data directory)

---

## Acceptance Criteria

### AC1: Default Config Created on First Run
**Given** no config.yaml exists  
**When** ConfigManager initializes  
**Then** default config.yaml created:
```yaml
version: "1.0"

# Data Management
data_directory: "~/.autoresumefiller"
data_structure: "single_file"  # or "multiple_files"
data_format: "json"
encryption_enabled: false

# AI Providers (API keys in OS keyring)
ai_providers:
  openai:
    model: "gpt-4"
    temperature: 0.7
  anthropic:
    model: "claude-3-sonnet"
  google:
    model: "gemini-pro"
  
selected_provider: "openai"

# Defaults
default_resume: null
default_cover_letter: null

# Auto-Backup
auto_backup_enabled: true
max_backups: 10
```

### AC2: Load Config Works
**Given** config.yaml exists  
**When** calling `ConfigManager.load_config()`  
**Then** returns dict with all settings  
**And** validates against schema  
**And** handles missing keys with defaults  
**And** completes in <50ms

### AC3: Get Setting Works
**Given** config loaded  
**When** calling `ConfigManager.get_setting("ai_providers.openai.model")`  
**Then** returns nested value using dot notation  
**And** supports default parameter if key not found  
**And** raises error for invalid paths

### AC4: Update Setting Works
**Given** config exists  
**When** calling `ConfigManager.update_setting("selected_provider", "anthropic")`  
**Then** config.yaml updated  
**And** YAML formatting preserved (comments, indentation)  
**And** change persists after application restart  
**And** validates value before saving

### AC5: Save Config Works
**Given** modified config dict  
**When** calling `ConfigManager.save_config(config_dict)`  
**Then** config.yaml overwritten with atomic write  
**And** YAML formatted with proper indentation  
**And** comments preserved (if using ruamel.yaml)  
**And** backup created before save

### AC6: Config Validation Works
**Given** invalid config values  
**When** attempting to save  
**Then** validation errors raised:
- `selected_provider` must be in ["openai", "anthropic", "google"]
- `max_backups` must be positive integer
- `data_structure` must be in ["single_file", "multiple_files"]
- `data_format` must be in ["json", "yaml"]

---

## Tasks

### Task 1: Create ConfigManager Module
- Create `backend/config/config_manager.py`
- Implement ConfigManager class with singleton pattern
- Add load/save/get/update methods
- Use ruamel.yaml for comment preservation

### Task 2: Implement Default Config
- Define default config structure
- Create on first run in data directory
- Add comments explaining each setting
- Validate default config

### Task 3: Implement Load/Save
- Load config with PyYAML or ruamel.yaml
- Save with atomic writes
- Preserve YAML formatting
- Handle missing files gracefully

### Task 4: Implement Get/Update
- Support dot notation for nested values
- Validate values before update
- Auto-save on update (optional)
- Handle type conversions

### Task 5: Add Config Validation
- Define Pydantic schema for config
- Validate on load and save
- Provide clear error messages
- Support schema versioning

### Task 6: Create Unit Tests
- Test load/save operations
- Test get/update with nested keys
- Test validation errors
- Test default config creation
- Coverage target: >90%

---

## Definition of Done

- [ ] ConfigManager implemented with all methods
- [ ] Default config created on first run
- [ ] Load/save preserves YAML formatting
- [ ] Get/update supports dot notation
- [ ] Config validation with clear errors
- [ ] Changes persist across restarts
- [ ] Unit tests >90% coverage
- [ ] All 6 acceptance criteria validated
- [ ] Documentation updated

---

## Traceability

**PRD:** FR7 (Configure default data directory location)  
**Epic Tech Spec:** AC10 (Configuration Persists)

