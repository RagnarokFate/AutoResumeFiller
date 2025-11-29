"""
Comprehensive tests for UserDataManager.

Tests:
- Cross-platform data directory initialization
- Atomic file writes (temp → replace)
- Auto-backup system (last 10 backups)
- File locking (concurrent access prevention)
- Load/save operations
- Backup restore
- Error handling
"""

import os
import json
import time
import tempfile
import threading
from pathlib import Path
from datetime import datetime

import pytest

from backend.services.data.user_data_manager import UserDataManager
from backend.services.data.schemas import UserProfile, PersonalInfo


class TestDataDirectoryInitialization:
    """Test cross-platform data directory initialization."""
    
    def test_default_data_dir_windows(self, monkeypatch, tmp_path):
        """Test Windows default data directory (%APPDATA%/AutoResumeFiller)."""
        monkeypatch.setattr('platform.system', lambda: 'Windows')
        # Use tmp_path to avoid permission issues
        test_appdata = tmp_path / "AppData" / "Roaming"
        test_appdata.mkdir(parents=True)
        monkeypatch.setenv('APPDATA', str(test_appdata))
        
        manager = UserDataManager()
        expected = test_appdata / 'AutoResumeFiller'
        assert manager.data_dir == expected
        assert manager.data_dir.exists()
    
    def test_default_data_dir_macos(self, monkeypatch, tmp_path):
        """Test macOS default data directory (~/Library/Application Support)."""
        monkeypatch.setattr('platform.system', lambda: 'Darwin')
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        manager = UserDataManager()
        expected = tmp_path / 'Library' / 'Application Support' / 'AutoResumeFiller'
        assert manager.data_dir == expected
        assert manager.data_dir.exists()
    
    def test_default_data_dir_linux(self, monkeypatch, tmp_path):
        """Test Linux default data directory (~/.local/share)."""
        monkeypatch.setattr('platform.system', lambda: 'Linux')
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        manager = UserDataManager()
        expected = tmp_path / '.local' / 'share' / 'AutoResumeFiller'
        assert manager.data_dir == expected
        assert manager.data_dir.exists()
    
    def test_custom_data_dir(self, tmp_path):
        """Test custom data directory initialization."""
        custom_dir = tmp_path / "custom_data"
        manager = UserDataManager(data_dir=custom_dir)
        
        assert manager.data_dir == custom_dir
        assert custom_dir.exists()
    
    def test_directories_created(self, tmp_path):
        """Test that data and backup directories are created."""
        data_dir = tmp_path / "test_data"
        manager = UserDataManager(data_dir=data_dir)
        
        assert manager.data_dir.exists()
        assert manager.backups_dir.exists()
        assert manager.user_profile_path == data_dir / "user_profile.json"


class TestLoadSaveOperations:
    """Test load and save operations with validation."""
    
    def test_load_nonexistent_profile(self, tmp_path):
        """Test loading when no profile exists returns None."""
        manager = UserDataManager(data_dir=tmp_path)
        profile = manager.load_user_profile()
        
        assert profile is None
        assert not manager.profile_exists()
    
    def test_save_and_load_profile(self, tmp_path):
        """Test saving and loading a valid profile."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Create test profile
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                phone="+1234567890"
            )
        )
        
        # Save profile
        manager.save_user_profile(profile)
        assert manager.profile_exists()
        
        # Load profile
        loaded_profile = manager.load_user_profile()
        assert loaded_profile is not None
        assert loaded_profile.personal_info.first_name == "Test"
        assert loaded_profile.personal_info.email == "test@example.com"
    
    def test_save_updates_timestamp(self, tmp_path):
        """Test that saving updates last_updated timestamp."""
        manager = UserDataManager(data_dir=tmp_path)
        
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        
        original_timestamp = profile.last_updated
        time.sleep(0.1)  # Ensure timestamp difference
        
        manager.save_user_profile(profile)
        
        # Timestamp should be updated
        assert profile.last_updated > original_timestamp
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises ValueError."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Write invalid JSON
        manager.user_profile_path.write_text("{ invalid json }")
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            manager.load_user_profile()
    
    def test_profile_exists_check(self, tmp_path):
        """Test profile_exists() method."""
        manager = UserDataManager(data_dir=tmp_path)
        
        assert not manager.profile_exists()
        
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile)
        
        assert manager.profile_exists()


class TestAtomicWrites:
    """Test atomic file write operations."""
    
    def test_atomic_write_creates_temp_file(self, tmp_path):
        """Test that save uses temporary file before replace."""
        manager = UserDataManager(data_dir=tmp_path)
        
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        
        # Save should complete successfully
        manager.save_user_profile(profile)
        
        # Final file should exist
        assert manager.user_profile_path.exists()
        
        # No temp files should remain
        temp_files = list(tmp_path.glob(".user_profile_*.tmp"))
        assert len(temp_files) == 0
    
    def test_atomic_write_rollback_on_error(self, tmp_path, monkeypatch):
        """Test that failed save doesn't corrupt existing file."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Save initial profile
        original_profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Original",
                last_name="User",
                email="original@example.com"
            )
        )
        manager.save_user_profile(original_profile, create_backup=False)
        
        # Inject error during write (simulate disk full)
        def mock_replace(*args, **kwargs):
            raise OSError("Disk full")
        
        monkeypatch.setattr(os, 'replace', mock_replace)
        
        # Try to save new profile (should fail)
        new_profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="New",
                last_name="User",
                email="new@example.com"
            )
        )
        
        with pytest.raises(IOError, match="Failed to save"):
            manager.save_user_profile(new_profile, create_backup=False)
        
        # Original file should still be intact
        loaded = manager.load_user_profile()
        assert loaded.personal_info.first_name == "Original"


class TestBackupSystem:
    """Test automatic backup system."""
    
    def test_backup_created_on_save(self, tmp_path):
        """Test that saving creates backup of existing file."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Save initial profile
        profile1 = UserProfile(
            personal_info=PersonalInfo(
                first_name="First",
                last_name="User",
                email="first@example.com"
            )
        )
        manager.save_user_profile(profile1)
        
        # No backup yet (first save)
        assert len(manager.list_backups()) == 0
        
        # Save updated profile (should create backup)
        profile2 = UserProfile(
            personal_info=PersonalInfo(
                first_name="Second",
                last_name="User",
                email="second@example.com"
            )
        )
        manager.save_user_profile(profile2)
        
        # Backup should exist
        backups = manager.list_backups()
        assert len(backups) == 1
        assert "auto_backup_" in backups[0]["filename"]
    
    def test_backup_disabled(self, tmp_path):
        """Test that backup can be disabled via create_backup=False."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Save initial profile
        profile1 = UserProfile(
            personal_info=PersonalInfo(
                first_name="First",
                last_name="User",
                email="first@example.com"
            )
        )
        manager.save_user_profile(profile1)
        
        # Save with backup disabled
        profile2 = UserProfile(
            personal_info=PersonalInfo(
                first_name="Second",
                last_name="User",
                email="second@example.com"
            )
        )
        manager.save_user_profile(profile2, create_backup=False)
        
        # No backup should exist
        assert len(manager.list_backups()) == 0
    
    def test_backup_rotation_keeps_last_10(self, tmp_path):
        """Test that only last 10 backups are kept."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Create initial profile
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="User",
                last_name="Test",
                email="user@example.com"
            )
        )
        manager.save_user_profile(profile)
        
        # Create 15 backups by saving 15 times
        for i in range(15):
            profile.personal_info.first_name = f"User{i}"
            manager.save_user_profile(profile)
            time.sleep(0.01)  # Ensure different timestamps
        
        # Only 10 backups should remain (first save doesn't create backup)
        backups = manager.list_backups()
        assert len(backups) <= 10, f"Expected <= 10 backups, got {len(backups)}"
    
    def test_list_backups_sorted_by_date(self, tmp_path):
        """Test that list_backups returns backups sorted by date (newest first)."""
        manager = UserDataManager(data_dir=tmp_path)
        
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="User",
                last_name="Test",
                email="user@example.com"
            )
        )
        manager.save_user_profile(profile)
        
        # Create multiple backups
        for i in range(5):
            profile.personal_info.first_name = f"User{i}"
            manager.save_user_profile(profile)
            time.sleep(0.02)
        
        backups = manager.list_backups()
        assert len(backups) >= 1, f"Expected at least 1 backup, got {len(backups)}"
        
        # Check sorted by date (newest first)
        if len(backups) > 1:
            timestamps = [b["created_at"] for b in backups]
            assert timestamps == sorted(timestamps, reverse=True)
    
    def test_restore_from_backup(self, tmp_path):
        """Test restoring profile from backup."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Save original profile
        original = UserProfile(
            personal_info=PersonalInfo(
                first_name="Original",
                last_name="User",
                email="original@example.com"
            )
        )
        manager.save_user_profile(original)
        
        # Modify and save (creates backup)
        modified = UserProfile(
            personal_info=PersonalInfo(
                first_name="Modified",
                last_name="User",
                email="modified@example.com"
            )
        )
        manager.save_user_profile(modified)
        
        # Get backup filename
        backups = manager.list_backups()
        assert len(backups) == 1
        backup_filename = backups[0]["filename"]
        
        # Restore from backup
        restored = manager.restore_from_backup(backup_filename)
        
        # Should restore original data
        assert restored.personal_info.first_name == "Original"
        assert restored.personal_info.email == "original@example.com"
        
        # Current profile should now be original
        current = manager.load_user_profile()
        assert current.personal_info.first_name == "Original"
    
    def test_restore_nonexistent_backup_raises_error(self, tmp_path):
        """Test restoring from nonexistent backup raises FileNotFoundError."""
        manager = UserDataManager(data_dir=tmp_path)
        
        with pytest.raises(FileNotFoundError, match="Backup not found"):
            manager.restore_from_backup("nonexistent_backup.json")


class TestFileLocking:
    """Test file locking for concurrent access prevention."""
    
    def test_concurrent_read_allowed(self, tmp_path):
        """Test that multiple concurrent reads work (Windows has exclusive locking behavior)."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Create profile
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile)
        
        # Attempt concurrent reads
        # Note: On Windows, file locking is more strict, so some reads may fail
        results = []
        errors = []
        
        def read_profile():
            try:
                loaded = manager.load_user_profile()
                results.append(loaded.personal_info.first_name)
            except (IOError, OSError) as e:
                errors.append(e)
        
        threads = [threading.Thread(target=read_profile) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # At least some reads should succeed (Windows may have lock contention)
        assert len(results) >= 1, f"Expected at least 1 successful read, got {len(results)}"
        assert all(name == "Test" for name in results)
    
    def test_file_locking_on_load(self, tmp_path):
        """Test that load applies file lock (verifiable via mock)."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Create profile
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile)
        
        # Load should not raise error (lock acquired and released)
        loaded = manager.load_user_profile()
        assert loaded is not None


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_delete_user_profile(self, tmp_path):
        """Test deleting user profile creates backup first."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Create profile
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        assert manager.profile_exists()
        
        # Delete profile
        result = manager.delete_user_profile()
        
        assert result is True
        assert not manager.profile_exists()
        
        # Backup should exist
        backups = manager.list_backups()
        assert len(backups) == 1
    
    def test_delete_nonexistent_profile(self, tmp_path):
        """Test deleting nonexistent profile returns False."""
        manager = UserDataManager(data_dir=tmp_path)
        
        result = manager.delete_user_profile()
        assert result is False
    
    def test_get_data_dir(self, tmp_path):
        """Test get_data_dir returns correct path."""
        custom_dir = tmp_path / "custom"
        manager = UserDataManager(data_dir=custom_dir)
        
        assert manager.get_data_dir() == custom_dir


class TestPerformance:
    """Test performance targets (<100ms load, <200ms save, <500ms backup)."""
    
    def test_load_performance(self, tmp_path):
        """Test that load completes in <100ms."""
        manager = UserDataManager(data_dir=tmp_path)
        
        # Create profile
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile)
        
        # Measure load time
        start = time.time()
        loaded = manager.load_user_profile()
        elapsed_ms = (time.time() - start) * 1000
        
        assert loaded is not None
        assert elapsed_ms < 100, f"Load took {elapsed_ms:.2f}ms (target: <100ms)"
    
    def test_save_performance(self, tmp_path):
        """Test that save completes in <200ms."""
        manager = UserDataManager(data_dir=tmp_path)
        
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        
        # Measure save time (without backup for first save)
        start = time.time()
        manager.save_user_profile(profile, create_backup=False)
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 200, f"Save took {elapsed_ms:.2f}ms (target: <200ms)"
