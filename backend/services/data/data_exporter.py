"""
Data Export and Import functionality for AutoResumeFiller.

Provides comprehensive backup and restore capabilities:
- Manual export creates complete ZIP with all user data
- Metadata includes checksums for integrity verification
- Import validates and restores from backup
- API key redaction for security

Performance targets:
- Export: <10 seconds for 100MB
- Import: <15 seconds with validation
"""

import os
import json
import shutil
import zipfile
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

try:
    import yaml
except ImportError:
    yaml = None

from backend.services.data.schemas import UserProfile
from backend.services.data.user_data_manager import UserDataManager


class DataExporter:
    """
    Handles data export and import operations.

    Features:
    - Complete data export to ZIP
    - Checksum verification (SHA256)
    - API key redaction
    - Import validation
    - Backup before import
    """

    def __init__(self, data_manager: UserDataManager):
        """
        Initialize DataExporter.

        Args:
            data_manager: UserDataManager instance for file operations
        """
        self.data_manager = data_manager
        self.data_dir = data_manager.data_dir

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum for file.

        Args:
            file_path: Path to file

        Returns:
            Hex string of SHA256 checksum
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _generate_metadata(
        self, files: List[Dict[str, Any]], missing_dirs: List[str]
    ) -> Dict[str, Any]:
        """
        Generate metadata for backup.

        Args:
            files: List of file dicts with path, size, checksum
            missing_dirs: List of directories that weren't found

        Returns:
            Metadata dict
        """
        total_size = sum(f["size_bytes"] for f in files)

        return {
            "export_timestamp": datetime.now().isoformat(),
            "app_version": "1.0.0",  # TODO: Get from package metadata
            "total_size_bytes": total_size,
            "file_count": len(files),
            "files": files,
            "missing_directories": missing_dirs,
            "notes": (
                "API keys redacted for security"
                if any("config" in f["path"] for f in files)
                else None
            ),
        }

    def _redact_config(self, config_path: Path, output_path: Path) -> None:
        """
        Copy config file with API keys redacted.

        Args:
            config_path: Source config.yaml
            output_path: Destination path
        """
        if not config_path.exists():
            return

        if yaml is None:
            # If PyYAML not available, just copy as-is with warning comment
            with open(config_path, "r", encoding="utf-8") as f_in, open(
                output_path, "w", encoding="utf-8"
            ) as f_out:
                f_out.write("# WARNING: PyYAML not installed, API keys not redacted\n")
                f_out.write(f_in.read())
            return

        # Load config
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        # Redact sensitive fields
        def redact_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in ["api_key", "secret", "password", "token"]:
                        obj[key] = "**REDACTED**"
                    elif isinstance(value, (dict, list)):
                        redact_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        redact_recursive(item)

        redact_recursive(config)

        # Write redacted config
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# API keys redacted for security\n")
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def export_all(
        self,
        output_path: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Export all user data to ZIP archive.

        Creates backup with:
        - user_profile.json
        - config.yaml (API keys redacted)
        - resumes/ directory (if exists)
        - cover_letters/ directory (if exists)
        - metadata.json with checksums

        Args:
            output_path: Output ZIP path (defaults to backups/ directory)
            progress_callback: Optional callback(current_bytes, total_bytes, current_file)

        Returns:
            Export metadata dict with filename, size, files exported

        Raises:
            IOError: If export fails
        """
        start_time = datetime.now()

        # Generate output filename if not provided
        if output_path is None:
            timestamp = start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"autoresumefiller_backup_{timestamp}.zip"
            output_path = self.data_manager.backups_dir / filename

        # Create temp directory for staging
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            stage_path = temp_path / "backup"
            stage_path.mkdir()

            files_metadata = []
            missing_dirs = []
            total_bytes = 0
            current_bytes = 0

            # Stage user_profile.json
            if self.data_manager.user_profile_path.exists():
                dest = stage_path / "data" / "user_profile.json"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.data_manager.user_profile_path, dest)

                checksum = self._calculate_checksum(dest)
                size = dest.stat().st_size
                files_metadata.append(
                    {
                        "path": "data/user_profile.json",
                        "size_bytes": size,
                        "checksum_sha256": checksum,
                    }
                )
                total_bytes += size

                if progress_callback:
                    current_bytes += size
                    progress_callback(current_bytes, total_bytes, "data/user_profile.json")

            # Stage config.yaml (with redaction)
            config_path = self.data_dir / "config.yaml"
            if config_path.exists():
                dest = stage_path / "config.yaml"
                self._redact_config(config_path, dest)

                checksum = self._calculate_checksum(dest)
                size = dest.stat().st_size
                files_metadata.append(
                    {"path": "config.yaml", "size_bytes": size, "checksum_sha256": checksum}
                )
                total_bytes += size

                if progress_callback:
                    current_bytes += size
                    progress_callback(current_bytes, total_bytes, "config.yaml")

            # Stage resumes/ directory
            resumes_dir = self.data_dir / "resumes"
            if resumes_dir.exists() and resumes_dir.is_dir():
                dest_resumes = stage_path / "resumes"
                dest_resumes.mkdir()

                for resume_file in resumes_dir.iterdir():
                    if resume_file.is_file():
                        dest = dest_resumes / resume_file.name
                        shutil.copy2(resume_file, dest)

                        checksum = self._calculate_checksum(dest)
                        size = dest.stat().st_size
                        files_metadata.append(
                            {
                                "path": f"resumes/{resume_file.name}",
                                "size_bytes": size,
                                "checksum_sha256": checksum,
                            }
                        )
                        total_bytes += size

                        if progress_callback:
                            current_bytes += size
                            progress_callback(
                                current_bytes, total_bytes, f"resumes/{resume_file.name}"
                            )
            else:
                missing_dirs.append("resumes")

            # Stage cover_letters/ directory
            cover_letters_dir = self.data_dir / "cover_letters"
            if cover_letters_dir.exists() and cover_letters_dir.is_dir():
                dest_letters = stage_path / "cover_letters"
                dest_letters.mkdir()

                for letter_file in cover_letters_dir.iterdir():
                    if letter_file.is_file():
                        dest = dest_letters / letter_file.name
                        shutil.copy2(letter_file, dest)

                        checksum = self._calculate_checksum(dest)
                        size = dest.stat().st_size
                        files_metadata.append(
                            {
                                "path": f"cover_letters/{letter_file.name}",
                                "size_bytes": size,
                                "checksum_sha256": checksum,
                            }
                        )
                        total_bytes += size

                        if progress_callback:
                            current_bytes += size
                            progress_callback(
                                current_bytes, total_bytes, f"cover_letters/{letter_file.name}"
                            )
            else:
                missing_dirs.append("cover_letters")

            # Generate metadata.json
            metadata = self._generate_metadata(files_metadata, missing_dirs)
            metadata_path = stage_path / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            # Create ZIP archive
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for root, _, files in os.walk(stage_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(stage_path)
                        zipf.write(file_path, arcname)

        # Calculate export duration
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Return export metadata
        return {
            "success": True,
            "output_path": str(output_path),
            "filename": output_path.name,
            "size_bytes": output_path.stat().st_size,
            "files_exported": len(files_metadata),
            "missing_directories": missing_dirs,
            "warnings": [f"Directory not found: {d}" for d in missing_dirs] if missing_dirs else [],
            "duration_ms": round(duration_ms, 2),
            "metadata": metadata,
        }

    def _validate_backup(self, zip_path: Path) -> Dict[str, Any]:
        """
        Validate backup ZIP before import.

        Args:
            zip_path: Path to backup ZIP

        Returns:
            Validation result dict with valid, errors, warnings, metadata
        """
        errors = []
        warnings = []
        metadata = None

        # Check ZIP exists
        if not zip_path.exists():
            errors.append(f"Backup file not found: {zip_path}")
            return {"valid": False, "errors": errors, "warnings": warnings, "metadata": None}

        # Check ZIP is readable
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                # Test ZIP integrity
                bad_file = zipf.testzip()
                if bad_file:
                    errors.append(f"Backup is corrupted: {bad_file} failed CRC check")
                    return {
                        "valid": False,
                        "errors": errors,
                        "warnings": warnings,
                        "metadata": None,
                    }

                # Check for metadata.json
                if "metadata.json" not in zipf.namelist():
                    warnings.append("metadata.json not found - unable to verify checksums")
                else:
                    # Parse metadata
                    with zipf.open("metadata.json") as f:
                        metadata = json.load(f)

                    # Check version compatibility
                    backup_version = metadata.get("app_version", "0.0.0")
                    current_version = "1.0.0"  # TODO: Get from package
                    if backup_version > current_version:
                        warnings.append(
                            f"Backup from newer version ({backup_version} > {current_version})"
                        )

                    # Verify checksums (in temp directory)
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        zipf.extractall(temp_path)

                        for file_meta in metadata.get("files", []):
                            file_path = temp_path / file_meta["path"]
                            if not file_path.exists():
                                errors.append(f"Missing file: {file_meta['path']}")
                                continue

                            # Verify checksum
                            actual_checksum = self._calculate_checksum(file_path)
                            expected_checksum = file_meta["checksum_sha256"]
                            if actual_checksum != expected_checksum:
                                errors.append(f"Checksum mismatch for {file_meta['path']}")

                            # Verify size
                            actual_size = file_path.stat().st_size
                            expected_size = file_meta["size_bytes"]
                            if actual_size != expected_size:
                                errors.append(
                                    f"Size mismatch for {file_meta['path']}: "
                                    f"{actual_size} != {expected_size}"
                                )

                        # Validate user_profile.json schema
                        profile_path = temp_path / "data" / "user_profile.json"
                        if profile_path.exists():
                            try:
                                with open(profile_path, "r", encoding="utf-8") as f:
                                    profile_data = json.load(f)
                                UserProfile(**profile_data)  # Validate against schema
                            except Exception as e:
                                errors.append(f"Invalid user profile schema: {e}")

        except zipfile.BadZipFile:
            errors.append("Backup is corrupted (invalid ZIP file)")
        except Exception as e:
            errors.append(f"Validation failed: {e}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata,
        }

    def import_from_backup(
        self,
        zip_path: Path,
        confirm: bool = True,
        backup_existing: bool = True,
        confirm_callback: Optional[Callable[[str], bool]] = None,
    ) -> Dict[str, Any]:
        """
        Import data from backup ZIP.

        Args:
            zip_path: Path to backup ZIP
            confirm: Whether to prompt for confirmation (default: True)
            backup_existing: Whether to backup existing data before import (default: True)
            confirm_callback: Optional callback(message) -> bool for confirmation

        Returns:
            Import summary dict

        Raises:
            ValueError: If validation fails
            RuntimeError: If import fails
        """
        start_time = datetime.now()

        # Validate backup
        validation = self._validate_backup(zip_path)
        if not validation["valid"]:
            raise ValueError(f"Backup validation failed: {', '.join(validation['errors'])}")

        warnings = validation["warnings"].copy()

        # Check for existing data
        existing_files = []
        if self.data_manager.user_profile_path.exists():
            last_modified = datetime.fromtimestamp(
                self.data_manager.user_profile_path.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M")
            existing_files.append(f"user_profile.json (last modified: {last_modified})")

        resumes_dir = self.data_dir / "resumes"
        if resumes_dir.exists():
            resume_count = len(list(resumes_dir.iterdir()))
            if resume_count > 0:
                existing_files.append(f"{resume_count} resume file(s)")

        cover_letters_dir = self.data_dir / "cover_letters"
        if cover_letters_dir.exists():
            letter_count = len(list(cover_letters_dir.iterdir()))
            if letter_count > 0:
                existing_files.append(f"{letter_count} cover letter file(s)")

        # Confirm overwrite
        if existing_files and confirm:
            message = "Existing data found. Import will replace:\n"
            for item in existing_files:
                message += f"  - {item}\n"
            if backup_existing:
                message += "\nExisting data will be backed up before import.\n"
            message += "\nContinue with import? [y/N]"

            if confirm_callback:
                confirmed = confirm_callback(message)
            else:
                # Default CLI confirmation
                print(message)
                response = input().strip().lower()
                confirmed = response == "y"

            if not confirmed:
                return {"success": False, "cancelled": True, "message": "Import cancelled by user"}

        # Backup existing data
        backup_path = None
        if backup_existing and existing_files:
            try:
                backup_result = self.export_all()
                backup_path = backup_result["output_path"]
            except Exception as e:
                warnings.append(f"Failed to backup existing data: {e}")

        # Extract and restore files
        files_restored = 0
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract ZIP
            with zipfile.ZipFile(zip_path, "r") as zipf:
                zipf.extractall(temp_path)

            # Restore user_profile.json
            profile_src = temp_path / "data" / "user_profile.json"
            if profile_src.exists():
                self.data_manager.user_profile_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(profile_src, self.data_manager.user_profile_path)
                files_restored += 1

            # Restore resumes/
            resumes_src = temp_path / "resumes"
            if resumes_src.exists():
                resumes_dest = self.data_dir / "resumes"
                resumes_dest.mkdir(parents=True, exist_ok=True)
                for resume_file in resumes_src.iterdir():
                    if resume_file.is_file():
                        shutil.copy2(resume_file, resumes_dest / resume_file.name)
                        files_restored += 1

            # Restore cover_letters/
            letters_src = temp_path / "cover_letters"
            if letters_src.exists():
                letters_dest = self.data_dir / "cover_letters"
                letters_dest.mkdir(parents=True, exist_ok=True)
                for letter_file in letters_src.iterdir():
                    if letter_file.is_file():
                        shutil.copy2(letter_file, letters_dest / letter_file.name)
                        files_restored += 1

            # Note: config.yaml is NOT restored (preserve API keys)
            warnings.append("config.yaml not imported (preserved existing API keys)")

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        return {
            "success": True,
            "files_restored": files_restored,
            "backup_created": backup_path,
            "warnings": warnings,
            "duration_ms": round(duration_ms, 2),
        }
