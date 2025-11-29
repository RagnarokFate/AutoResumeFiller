"""
Tests for DataExporter (Data Export & Backup Functionality).

Tests export/import, validation, checksum verification, and backup management.
"""

import json
import tempfile
import zipfile
from pathlib import Path

import pytest

from backend.services.data.data_exporter import DataExporter
from backend.services.data.user_data_manager import UserDataManager
from backend.services.data.schemas import UserProfile, PersonalInfo


class TestDataExport:
    """Test data export functionality."""
    
    def test_export_creates_zip(self, tmp_path):
        """Test that export creates ZIP file."""
        # Setup
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create test data
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        # Export
        output_path = tmp_path / "export_test.zip"
        result = exporter.export_all(output_path=output_path)
        
        assert result['success'] is True
        assert output_path.exists()
        assert result['files_exported'] >= 1
        assert 'user_profile.json' in str(result)
    
    def test_export_includes_metadata(self, tmp_path):
        """Test that export includes metadata.json."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create test data
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        # Export
        output_path = tmp_path / "export_test.zip"
        result = exporter.export_all(output_path=output_path)
        
        # Check ZIP contents
        with zipfile.ZipFile(output_path, 'r') as zipf:
            assert 'metadata.json' in zipf.namelist()
            
            # Verify metadata
            with zipf.open('metadata.json') as f:
                metadata = json.load(f)
            
            assert 'export_timestamp' in metadata
            assert 'app_version' in metadata
            assert 'files' in metadata
            assert len(metadata['files']) >= 1
            assert metadata['files'][0]['path'] == 'data/user_profile.json'
            assert 'checksum_sha256' in metadata['files'][0]
    
    def test_export_handles_missing_directories(self, tmp_path):
        """Test export handles missing resumes/cover_letters directories."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create only profile (no resumes/cover_letters)
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        # Export
        output_path = tmp_path / "export_test.zip"
        result = exporter.export_all(output_path=output_path)
        
        assert result['success'] is True
        assert 'resumes' in result['missing_directories']
        assert 'cover_letters' in result['missing_directories']
        assert len(result['warnings']) >= 2
    
    def test_export_default_filename(self, tmp_path):
        """Test export generates timestamped filename when not provided."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create test data
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        # Export without output_path
        result = exporter.export_all()
        
        assert result['success'] is True
        assert 'autoresumefiller_backup_' in result['filename']
        assert result['filename'].endswith('.zip')


class TestChecksumVerification:
    """Test checksum calculation and verification."""
    
    def test_calculate_checksum(self, tmp_path):
        """Test checksum calculation."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Calculate checksum
        checksum = exporter._calculate_checksum(test_file)
        
        assert checksum is not None
        assert len(checksum) == 64  # SHA256 hex length
        
        # Verify consistency
        checksum2 = exporter._calculate_checksum(test_file)
        assert checksum == checksum2
    
    def test_export_includes_checksums(self, tmp_path):
        """Test that exported metadata includes checksums."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create test data
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        # Export
        output_path = tmp_path / "export_test.zip"
        result = exporter.export_all(output_path=output_path)
        
        # Verify checksums in metadata
        metadata = result['metadata']
        for file_meta in metadata['files']:
            assert 'checksum_sha256' in file_meta
            assert len(file_meta['checksum_sha256']) == 64


class TestImportValidation:
    """Test import validation."""
    
    def test_validate_valid_backup(self, tmp_path):
        """Test validation passes for valid backup."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create and export test data
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        output_path = tmp_path / "export_test.zip"
        exporter.export_all(output_path=output_path)
        
        # Validate
        validation = exporter._validate_backup(output_path)
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        assert validation['metadata'] is not None
    
    def test_validate_nonexistent_backup(self, tmp_path):
        """Test validation fails for nonexistent file."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        fake_path = tmp_path / "nonexistent.zip"
        validation = exporter._validate_backup(fake_path)
        
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        assert "not found" in validation['errors'][0].lower()
    
    def test_validate_corrupted_zip(self, tmp_path):
        """Test validation fails for corrupted ZIP."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create fake corrupted ZIP
        corrupted_zip = tmp_path / "corrupted.zip"
        corrupted_zip.write_text("This is not a valid ZIP file")
        
        validation = exporter._validate_backup(corrupted_zip)
        
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        assert "corrupted" in validation['errors'][0].lower()


class TestImportRestore:
    """Test import and restore functionality."""
    
    def test_import_from_valid_backup(self, tmp_path):
        """Test importing from valid backup."""
        # Setup source data
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        source_manager = UserDataManager(data_dir=source_dir)
        
        # Create test data
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Original",
                last_name="User",
                email="original@example.com"
            )
        )
        source_manager.save_user_profile(profile, create_backup=False)
        
        # Export
        exporter_source = DataExporter(source_manager)
        backup_path = tmp_path / "backup.zip"
        exporter_source.export_all(output_path=backup_path)
        
        # Import to new location
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_manager = UserDataManager(data_dir=dest_dir)
        exporter_dest = DataExporter(dest_manager)
        
        result = exporter_dest.import_from_backup(
            backup_path,
            confirm=False,
            backup_existing=False
        )
        
        assert result['success'] is True
        assert result['files_restored'] >= 1
        
        # Verify imported data
        imported_profile = dest_manager.load_user_profile()
        assert imported_profile is not None
        assert imported_profile.personal_info.first_name == "Original"
        assert imported_profile.personal_info.email == "original@example.com"
    
    def test_import_validation_failure(self, tmp_path):
        """Test import fails with invalid backup."""
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create corrupted backup
        fake_backup = tmp_path / "fake.zip"
        fake_backup.write_text("Not a real backup")
        
        with pytest.raises(ValueError, match="validation failed"):
            exporter.import_from_backup(fake_backup, confirm=False)
    
    def test_import_creates_backup_of_existing(self, tmp_path):
        """Test import backs up existing data before overwriting."""
        # Create existing data
        manager = UserDataManager(data_dir=tmp_path)
        existing_profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Existing",
                last_name="User",
                email="existing@example.com"
            )
        )
        manager.save_user_profile(existing_profile, create_backup=False)
        
        # Create backup to import
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        source_manager = UserDataManager(data_dir=source_dir)
        new_profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="New",
                last_name="User",
                email="new@example.com"
            )
        )
        source_manager.save_user_profile(new_profile, create_backup=False)
        
        exporter_source = DataExporter(source_manager)
        backup_path = tmp_path / "backup.zip"
        exporter_source.export_all(output_path=backup_path)
        
        # Import (should backup existing first)
        exporter = DataExporter(manager)
        result = exporter.import_from_backup(
            backup_path,
            confirm=False,
            backup_existing=True
        )
        
        assert result['success'] is True
        assert result['backup_created'] is not None
        assert Path(result['backup_created']).exists()
        
        # Verify new data imported
        imported_profile = manager.load_user_profile()
        assert imported_profile.personal_info.first_name == "New"


class TestPerformance:
    """Test performance targets."""
    
    def test_export_performance(self, tmp_path):
        """Test export completes quickly for small datasets."""
        import time
        
        manager = UserDataManager(data_dir=tmp_path)
        exporter = DataExporter(manager)
        
        # Create test data
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        manager.save_user_profile(profile, create_backup=False)
        
        # Measure export time
        start = time.time()
        output_path = tmp_path / "export_test.zip"
        result = exporter.export_all(output_path=output_path)
        elapsed_ms = (time.time() - start) * 1000
        
        assert result['success'] is True
        # Small dataset should export very quickly (<1 second)
        assert elapsed_ms < 1000
    
    def test_import_performance(self, tmp_path):
        """Test import completes quickly."""
        import time
        
        # Create and export test data
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        source_manager = UserDataManager(data_dir=source_dir)
        
        profile = UserProfile(
            personal_info=PersonalInfo(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
        )
        source_manager.save_user_profile(profile, create_backup=False)
        
        exporter_source = DataExporter(source_manager)
        backup_path = tmp_path / "backup.zip"
        exporter_source.export_all(output_path=backup_path)
        
        # Measure import time
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_manager = UserDataManager(data_dir=dest_dir)
        exporter_dest = DataExporter(dest_manager)
        
        start = time.time()
        result = exporter_dest.import_from_backup(
            backup_path,
            confirm=False,
            backup_existing=False
        )
        elapsed_ms = (time.time() - start) * 1000
        
        assert result['success'] is True
        # Small dataset should import very quickly (<2 seconds with validation)
        assert elapsed_ms < 2000
