# Story 2.8: Data Encryption at Rest

**Story ID:** 2.8  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 3  
**Estimated Effort:** Medium (2-3 days)  
**Priority:** High  

---

## User Story

**As a** user  
**I want** my personal data encrypted on my local machine  
**So that** my information remains secure even if my device is compromised

---

## Context

This story implements AES-256-GCM encryption for user data at rest. The EncryptionService handles encryption/decryption with keys stored securely in the OS keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service). UserDataManager integrates encryption transparently - data is encrypted on save and decrypted on load without user intervention.

**Current State:**
- User data stored in plaintext JSON (Story 2.2)
- No encryption capability
- Security risk if device compromised

**Desired State:**
- AES-256-GCM encryption for user_profile.json
- Encryption key stored in OS keyring
- Transparent encryption/decryption (<50ms overhead)
- Optional encryption (configurable via config.yaml)
- Authentication tags prevent tampering

---

## Dependencies

**Prerequisites:**
- Story 2.2: File System Data Manager ✅ (Integrates with save/load)
- Story 2.6: Configuration Management ✅ (Uses encryption_enabled setting)

---

## Acceptance Criteria

### AC1: Generate and Store Encryption Key
**Given** first run with encryption enabled  
**When** EncryptionService initializes  
**Then** encryption key generated:
- Algorithm: Fernet (AES-256-GCM)
- Key size: 256 bits (32 bytes)
- Base64-encoded key

**And** key stored in OS keyring:
- **Windows:** Windows Credential Manager (`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Credentials`)
- **macOS:** Keychain (`security add-generic-password`)
- **Linux:** Secret Service (gnome-keyring or KWallet via `keyring` library)

**And** keyring service: "autoresumefiller"  
**And** keyring key name: "encryption_key"

### AC2: Encrypt File Works
**Given** plaintext user_profile.json  
**When** calling `EncryptionService.encrypt_file(plaintext_path, encrypted_path)`  
**Then** encrypted file created:
- Filename: user_profile.json.enc
- Encrypted with Fernet (AES-256-GCM)
- Includes authentication tag (AEAD)
- Original plaintext securely deleted (overwrite then delete)

**And** encryption completes in <50ms  
**And** encrypted file size ≈ plaintext size + 57 bytes (Fernet overhead)

### AC3: Decrypt File Works
**Given** encrypted user_profile.json.enc  
**When** calling `EncryptionService.decrypt_file(encrypted_path, plaintext_path)`  
**Then** plaintext file restored:
- Decryption successful
- Authentication tag verified (prevents tampering)
- Plaintext written to temp location (never permanent on disk)

**And** decryption completes in <50ms  
**And** raises error if authentication fails (file tampered)

### AC4: Transparent Encryption in UserDataManager
**Given** encryption_enabled=true in config  
**When** calling `UserDataManager.save_user_profile(profile)`  
**Then** automatically:
1. Serialize profile to JSON
2. Write JSON to temp file
3. Encrypt temp file → user_profile.json.enc
4. Delete plaintext temp file (secure overwrite)
5. Store only encrypted file

**When** calling `UserDataManager.load_user_profile()`  
**Then** automatically:
1. Read user_profile.json.enc
2. Decrypt to memory (not to disk)
3. Parse JSON from decrypted bytes
4. Return UserProfile instance
5. Never write plaintext to disk

**And** encryption/decryption transparent to caller

### AC5: Encrypt Data in Memory
**Given** data as bytes (not file)  
**When** calling `EncryptionService.encrypt_data(data: bytes)`  
**Then** encrypted bytes returned (no file I/O)  
**When** calling `EncryptionService.decrypt_data(encrypted_data: bytes)`  
**Then** plaintext bytes returned

**And** useful for in-memory encryption (API responses, network transfer)

### AC6: Key Rotation Supported
**Given** existing encryption key  
**When** calling `EncryptionService.rotate_key()`  
**Then** new key generated:
1. Generate new Fernet key
2. Decrypt all encrypted files with old key
3. Re-encrypt with new key
4. Store new key in keyring (overwrite old)
5. Delete old key

**And** rotation completes successfully  
**And** all data remains accessible

### AC7: Handle Missing Key
**Given** encrypted file exists but key missing from keyring  
**When** attempting to load  
**Then** error raised: "Encryption key not found. Cannot decrypt data."  
**And** suggests:
- Check if keyring service is running
- Restore key from backup (if available)
- Recreate key (will lose existing encrypted data)

**And** no data corruption

### AC8: Encryption Performance
**Given** 1MB user_profile.json  
**When** encrypting and decrypting  
**Then** performance targets met:
- Encryption: <50ms overhead
- Decryption: <50ms overhead
- Total save time: <250ms (200ms base + 50ms encryption)
- Total load time: <150ms (100ms base + 50ms decryption)

### AC9: Tamper Detection
**Given** encrypted file tampered with (modified bytes)  
**When** attempting to decrypt  
**Then** error raised: "Authentication failed. File may be corrupted or tampered."  
**And** no plaintext data returned  
**And** suggests restoring from backup

---

## Tasks

### Task 1: Create EncryptionService Module
- Create `backend/services/data/encryption.py`
- Install cryptography: `pip install cryptography`
- Install keyring: `pip install keyring`
- Implement EncryptionService class
- Use Fernet (AES-256-GCM wrapper)

### Task 2: Implement Key Generation
- Generate Fernet key: `Fernet.generate_key()`
- Store in OS keyring via `keyring.set_password()`
- Retrieve via `keyring.get_password()`
- Handle keyring unavailable (Linux fallback)
- Test on Windows, macOS, Linux

### Task 3: Implement File Encryption
- Implement encrypt_file() method:
  - Read plaintext file
  - Encrypt with Fernet
  - Write encrypted file
  - Securely delete plaintext (overwrite with random bytes)
- Add error handling for file I/O

### Task 4: Implement File Decryption
- Implement decrypt_file() method:
  - Read encrypted file
  - Decrypt with Fernet
  - Return plaintext bytes (or write to file)
  - Verify authentication tag
- Raise error if tampered

### Task 5: Implement In-Memory Encryption
- Implement encrypt_data(data: bytes) → bytes
- Implement decrypt_data(encrypted: bytes) → bytes
- No file I/O, pure memory operations

### Task 6: Integrate with UserDataManager
- Modify save_user_profile():
  - Check if encryption_enabled in config
  - If true, encrypt JSON before final save
  - Save as user_profile.json.enc
- Modify load_user_profile():
  - Check if .enc file exists
  - If true, decrypt to memory
  - Parse JSON from memory
  - Never write plaintext to disk

### Task 7: Implement Key Rotation
- Implement rotate_key() method:
  - Generate new key
  - Decrypt all encrypted files with old key
  - Re-encrypt with new key
  - Update keyring
- Test rotation doesn't lose data

### Task 8: Add Error Handling
- Handle missing keyring service (Linux)
- Handle tampered files (authentication failure)
- Handle corrupted encrypted files
- Provide recovery suggestions

### Task 9: Create Unit Tests
- Test key generation and storage
- Test file encryption/decryption
- Test in-memory encryption/decryption
- Test tamper detection
- Test key rotation
- Test missing key error handling
- Test performance (<50ms overhead)
- Coverage target: >90%

### Task 10: Create Integration Tests
- Test complete save/load with encryption
- Test encryption disabled (plaintext save/load)
- Test migration from plaintext to encrypted
- Test cross-platform (Windows, macOS, Linux)

---

## Definition of Done

- [ ] EncryptionService implemented with Fernet
- [ ] Key generation and OS keyring storage works
- [ ] File encryption/decryption works
- [ ] In-memory encryption/decryption works
- [ ] UserDataManager integrates encryption transparently
- [ ] Encryption adds <50ms overhead
- [ ] Tamper detection with authentication tags
- [ ] Key rotation supported
- [ ] Error handling for missing key, tampering
- [ ] Unit tests >90% coverage
- [ ] Integration tests pass
- [ ] Cross-platform tested (Windows, macOS, Linux)
- [ ] All 9 acceptance criteria validated
- [ ] Documentation updated with security notes

---

## Traceability

**PRD:** FR80 (All user data stored locally), FR81 (Secure credential storage)  
**Architecture:** Security → Data Encryption at Rest  
**Epic Tech Spec:** AC12 (Data Encryption Works)

---

## Notes

- **Fernet (AES-256-GCM):** Provides encryption + authentication (AEAD)
- **OS Keyring:** Secure key storage prevents key exposure in config files
- **Secure Deletion:** Overwrite plaintext with random bytes before delete
- **Performance:** Fernet is fast (~10-50ms for 1MB files)
- **Fallback:** If keyring unavailable (Linux), consider encrypted local file with master password
- **Future:** Consider encrypting resumes/cover letters (currently only user_profile.json)
- **Compliance:** Encryption helps meet data protection regulations (GDPR, CCPA)
