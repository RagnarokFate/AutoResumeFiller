"""
File System Data Manager for AutoResumeFiller.

Handles all file operations for user data:
- Cross-platform data directory initialization
- Atomic file writes with rollback
- Automatic backups (last 10)
- File locking for concurrent access prevention
- Load/save user profile data

Performance targets:
- Load: <100ms
- Save: <200ms
- Backup: <500ms
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional
import platform

# Platform-specific file locking
if platform.system() == "Windows":
    import msvcrt
else:
    import fcntl

from backend.services.data.schemas import UserProfile


class UserDataManager:
    """
    Manages user profile data with file system operations.
    
    Features:
    - Cross-platform data directory (AppData/Library/local)
    - Atomic writes (temp file → replace)
    - Auto-backup (last 10 backups kept)
    - File locking (prevents corruption from concurrent access)
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize UserDataManager.
        
        Args:
            data_dir: Custom data directory (optional, uses platform default if None)
        """
        self.data_dir = data_dir or self._get_default_data_dir()
        self.user_profile_path = self.data_dir / "user_profile.json"
        self.backups_dir = self.data_dir / "backups"
        
        # Initialize directories
        self._init_directories()
    
    def _get_default_data_dir(self) -> Path:
        """
        Get platform-specific default data directory.
        
        Returns:
            Path to data directory:
            - Windows: %APPDATA%/AutoResumeFiller
            - macOS: ~/Library/Application Support/AutoResumeFiller
            - Linux: ~/.local/share/AutoResumeFiller
        """
        system = platform.system()
        
        if system == "Windows":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif system == "Darwin":  # macOS
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux and others
            base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        
        return base / "AutoResumeFiller"
    
    def _init_directories(self) -> None:
        """Create data and backup directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
    
    def _lock_file(self, file_handle, exclusive=True):
        """
        Apply platform-specific file lock.
        
        Args:
            file_handle: Open file handle
            exclusive: True for exclusive lock (write), False for shared lock (read)
        """
        if platform.system() == "Windows":
            # Windows: msvcrt.locking()
            mode = msvcrt.LK_NBLCK if exclusive else msvcrt.LK_NBRLCK
            msvcrt.locking(file_handle.fileno(), mode, 1)
        else:
            # POSIX: fcntl.flock()
            lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(file_handle.fileno(), lock_type | fcntl.LOCK_NB)
    
    def _unlock_file(self, file_handle):
        """
        Remove platform-specific file lock.
        
        Args:
            file_handle: Open file handle
        """
        if platform.system() == "Windows":
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
    
    def load_user_profile(self) -> Optional[UserProfile]:
        """
        Load user profile from disk with file locking.
        
        Returns:
            UserProfile object if file exists and is valid, None otherwise
            
        Raises:
            IOError: If file is locked by another process
            ValidationError: If JSON is invalid or doesn't match schema
        """
        if not self.user_profile_path.exists():
            return None
        
        with open(self.user_profile_path, 'r', encoding='utf-8') as f:
            # Apply shared lock (allow multiple readers)
            try:
                self._lock_file(f, exclusive=False)
            except (IOError, OSError):
                raise IOError("User profile file is locked by another process")
            
            try:
                data = json.load(f)
                # Validate with Pydantic
                profile = UserProfile(**data)
                return profile
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in user profile: {e}")
            finally:
                try:
                    self._unlock_file(f)
                except (OSError, IOError):
                    # Ignore unlock errors (file may already be closed/released)
                    pass
    
    def save_user_profile(self, profile: UserProfile, create_backup: bool = True) -> None:
        """
        Save user profile to disk with atomic write and optional backup.
        
        Atomic write process:
        1. Write to temporary file in same directory
        2. Backup existing file (if exists)
        3. Atomically replace old file with temp file (os.replace)
        
        Args:
            profile: UserProfile object to save
            create_backup: Whether to create backup before saving (default: True)
            
        Raises:
            IOError: If file operations fail
        """
        # Update timestamp
        profile.last_updated = datetime.now()
        
        # Serialize to JSON
        json_data = profile.model_dump_json(indent=2)
        
        # Create backup if existing file exists
        if create_backup and self.user_profile_path.exists():
            self._create_backup()
        
        # Atomic write: temp file → replace
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.data_dir,
            prefix=".user_profile_",
            suffix=".tmp"
        )
        
        try:
            # Write to temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(json_data)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomically replace old file
            os.replace(temp_path, self.user_profile_path)
        
        except Exception as e:
            # Cleanup temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise IOError(f"Failed to save user profile: {e}")
    
    def _create_backup(self) -> None:
        """
        Create timestamped backup of current user profile.
        
        Backup filename: auto_backup_YYYYMMDD_HHMMSS.json
        Keeps only last 10 backups (deletes oldest if >10).
        """
        if not self.user_profile_path.exists():
            return
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"auto_backup_{timestamp}.json"
        backup_path = self.backups_dir / backup_filename
        
        # Copy current file to backup
        shutil.copy2(self.user_profile_path, backup_path)
        
        # Cleanup old backups (keep last 10)
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self, max_backups: int = 10) -> None:
        """
        Delete old backups, keeping only the most recent ones.
        
        Args:
            max_backups: Maximum number of backups to keep (default: 10)
        """
        # Get all backup files sorted by modification time (newest first)
        backups = sorted(
            self.backups_dir.glob("auto_backup_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Delete backups beyond max_backups
        for old_backup in backups[max_backups:]:
            old_backup.unlink()
    
    def list_backups(self) -> list[dict]:
        """
        List all available backups with metadata.
        
        Returns:
            List of dicts with backup info: {filename, path, created_at, size_bytes}
        """
        backups = []
        for backup_path in sorted(
            self.backups_dir.glob("auto_backup_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        ):
            stat = backup_path.stat()
            backups.append({
                "filename": backup_path.name,
                "path": str(backup_path),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_bytes": stat.st_size
            })
        return backups
    
    def restore_from_backup(self, backup_filename: str) -> UserProfile:
        """
        Restore user profile from specific backup.
        
        Args:
            backup_filename: Backup filename (e.g., "auto_backup_20251129_100000.json")
            
        Returns:
            Restored UserProfile object
            
        Raises:
            FileNotFoundError: If backup doesn't exist
            ValidationError: If backup JSON is invalid
        """
        backup_path = self.backups_dir / backup_filename
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_filename}")
        
        # Load and validate backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            profile = UserProfile(**data)
        
        # Save as current profile (creates new backup of current state)
        self.save_user_profile(profile, create_backup=True)
        
        return profile
    
    def delete_user_profile(self) -> bool:
        """
        Delete user profile file (creates backup first).
        
        Returns:
            True if deleted, False if file didn't exist
        """
        if not self.user_profile_path.exists():
            return False
        
        # Backup before deleting
        self._create_backup()
        
        # Delete file
        self.user_profile_path.unlink()
        return True
    
    def profile_exists(self) -> bool:
        """Check if user profile file exists."""
        return self.user_profile_path.exists()
    
    def get_data_dir(self) -> Path:
        """Get the data directory path."""
        return self.data_dir
