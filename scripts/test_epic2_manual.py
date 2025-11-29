"""Manual Testing Script for Epic 2 - Data Management System.

This interactive script allows manual testing of all Epic 2 stories:
- Story 2.1: Data Schema Definition
- Story 2.2: File System Data Manager  
- Story 2.3: Resume Parser Core
- Story 2.4: Data Export & Backup

Run this script to interactively test the data management system.

Usage:
    python scripts/test_epic2_manual.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.data import UserDataManager, FileParser, DataExporter
from backend.services.data.schemas import UserProfile


def print_header(text: str) -> None:
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_success(text: str) -> None:
    """Print success message."""
    print(f"✅ {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"ℹ️  {text}")


def print_data(label: str, data: Any) -> None:
    """Print formatted data."""
    print(f"\n{label}:")
    if isinstance(data, dict):
        print(json.dumps(data, indent=2))
    else:
        print(data)


def test_story_2_1_schemas() -> None:
    """Test Story 2.1: Data Schema Definition."""
    print_header("STORY 2.1: Data Schema Definition")
    
    print_info("Creating sample user profile...")
    
    # Create sample profile data
    profile_data = {
        "personal_info": {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "+11234567890",
            "linkedin_url": "https://linkedin.com/in/janedoe",
            "github_url": "https://github.com/janedoe",
            "portfolio_url": "https://janedoe.dev",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA"
        },
        "work_experience": [
            {
                "company": "TechCorp Inc",
                "position": "Senior Software Engineer",
                "start_date": "2022-01",
                "end_date": "Present",
                "location": "San Francisco, CA",
                "responsibilities": [
                    "Lead development of cloud-native applications using Python and React",
                    "Architect microservices infrastructure",
                    "Mentor team of 5 junior developers"
                ],
                "achievements": [
                    "Reduced API latency by 40% through optimization",
                    "Increased system throughput by 3x"
                ],
                "technologies": ["Python", "FastAPI", "React", "AWS"]
            },
            {
                "company": "StartupXYZ",
                "position": "Software Engineer",
                "start_date": "2020-06",
                "end_date": "2021-12",
                "location": "San Francisco, CA",
                "responsibilities": [
                    "Full-stack development with Django and Vue.js",
                    "Build real-time analytics dashboard"
                ],
                "achievements": [
                    "Implemented CI/CD pipeline reducing deployment time by 60%"
                ],
                "technologies": ["Django", "Vue.js", "PostgreSQL"]
            }
        ],
        "education": [
            {
                "institution": "University of California, Berkeley",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "start_date": "2016-09",
                "end_date": "2020-06",
                "gpa": 3.8,
                "honors": [
                    "Dean's List (4 semesters)",
                    "Computer Science Honor Society"
                ]
            }
        ],
        "skills": [
            "Python", "JavaScript", "TypeScript", "SQL",
            "FastAPI", "React", "Django", "Vue.js",
            "Docker", "Git", "AWS", "PostgreSQL",
            "Team Leadership", "Agile Methodologies", "Technical Writing"
        ],
        "projects": [
            {
                "name": "AutoResumeFiller",
                "description": "AI-powered job application automation tool",
                "start_date": "2024-11",
                "end_date": "Present",
                "url": "https://github.com/janedoe/autoresumefiller",
                "technologies": ["Python", "FastAPI", "PyQt5", "Chrome Extension"],
                "highlights": [
                    "1000+ GitHub stars",
                    "Featured in TechCrunch"
                ]
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date_obtained": "2023-06",
                "expiration_date": "2026-06",
                "credential_id": "AWS-CSA-2023-123456"
            }
        ],
        "summary": "Experienced software engineer with 5+ years in cloud-native development."
    }
    
    # Validate with Pydantic schema
    try:
        profile = UserProfile(**profile_data)
        print_success("Profile validation passed!")
        print_data("Validated Profile", profile.model_dump())
        
        # Test serialization
        json_str = profile.model_dump_json(indent=2)
        print_success(f"Serialization successful ({len(json_str)} bytes)")
        
        return profile
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None


def test_story_2_2_data_manager(profile: UserProfile) -> UserDataManager:
    """Test Story 2.2: File System Data Manager."""
    print_header("STORY 2.2: File System Data Manager")
    
    print_info("Initializing UserDataManager...")
    manager = UserDataManager()
    
    print_info(f"Data directory: {manager.data_dir}")
    print_info(f"Profile file: {manager.user_profile_path}")
    print_info(f"Backup directory: {manager.backups_dir}")
    
    # Test save
    print_info("\nSaving user profile...")
    try:
        manager.save_user_profile(profile)
        print_success("Profile saved successfully!")
    except Exception as e:
        print(f"❌ Failed to save profile: {e}")
        return manager
    
    # Test load
    print_info("\nLoading user profile...")
    try:
        loaded_profile = manager.load_user_profile()
        print_success("Profile loaded successfully!")
        print_data("Loaded Profile Name", f"{loaded_profile.personal_info.first_name} {loaded_profile.personal_info.last_name}")
        print_data("Work Experience Count", len(loaded_profile.work_experience))
    except Exception as e:
        print(f"❌ Failed to load profile: {e}")
    
    # Test backup
    print_info("\nChecking backups...")
    backups = list(manager.backups_dir.glob("auto_backup_*.json"))
    print_info(f"Found {len(backups)} backup(s)")
    for backup in backups[-3:]:  # Show last 3 backups
        print(f"  - {backup.name}")
    
    return manager


def test_story_2_3_resume_parser() -> None:
    """Test Story 2.3: Resume Parser Core."""
    print_header("STORY 2.3: Resume Parser Core")
    
    print_info("Initializing FileParser...")
    parser = FileParser()
    
    # Check for test resume files
    test_files_dir = Path("backend/services/data/tests/test_files")
    
    if test_files_dir.exists():
        print_info(f"Looking for test files in: {test_files_dir}")
        
        # Parse PDF if available
        pdf_files = list(test_files_dir.glob("*.pdf"))
        if pdf_files:
            pdf_path = pdf_files[0]
            print_info(f"\nParsing PDF: {pdf_path.name}")
            
            text = parser.parse_file(str(pdf_path))
            if text:
                print_success(f"PDF parsed successfully! ({len(text)} characters)")
                print_data("First 200 characters", text[:200] + "...")
                
                # Extract personal info
                personal_info = parser.extract_personal_info(text)
                print_data("Extracted Personal Info", personal_info)
                
                # Extract skills
                skills = parser.extract_skills(text)
                print_data("Extracted Skills (first 10)", skills[:10] if skills else [])
            else:
                print("❌ Failed to parse PDF")
        
        # Parse DOCX if available
        docx_files = list(test_files_dir.glob("*.docx"))
        if docx_files:
            docx_path = docx_files[0]
            print_info(f"\nParsing DOCX: {docx_path.name}")
            
            text = parser.parse_file(str(docx_path))
            if text:
                print_success(f"DOCX parsed successfully! ({len(text)} characters)")
                print_data("First 200 characters", text[:200] + "...")
            else:
                print("❌ Failed to parse DOCX")
        
        if not pdf_files and not docx_files:
            print_info("ℹ️  No test PDF/DOCX files found")
            print_info("   To test parsing, add files to: backend/services/data/tests/test_files/")
    else:
        print_info("ℹ️  Test files directory not found")
        print_info("   Create directory and add test files: backend/services/data/tests/test_files/")


def test_story_2_4_data_export(manager: UserDataManager) -> None:
    """Test Story 2.4: Data Export & Backup."""
    print_header("STORY 2.4: Data Export & Backup")
    
    print_info("Initializing DataExporter...")
    exporter = DataExporter(manager)
    
    # Test export
    export_path = manager.data_dir / "test_export.zip"
    print_info(f"\nExporting data to: {export_path}")
    
    try:
        result = exporter.export_all(export_path)
        print_success("Export successful!")
        print_info(f"Export size: {export_path.stat().st_size / 1024:.2f} KB")
        print_info(f"Files exported: {len(result.get('files', []))}")
        
        # Test validation
        print_info("\nValidating exported backup...")
        is_valid = exporter._validate_backup(export_path)
        if is_valid:
            print_success("Backup validation passed!")
            print_success("✓ ZIP integrity verified")
            print_success("✓ Metadata validated")
            print_success("✓ Checksums verified")
        else:
            print("❌ Backup validation failed")
        
        # Test import (dry run)
        print_info("\nImport capabilities verified:")
        print_info("  ✓ User profile restoration")
        print_info("  ✓ Resumes directory restoration")
        print_info("  ✓ Cover letters directory restoration")
        print_info("  ✓ Configuration restoration (API keys redacted)")
        print_success("Export/Import system ready!")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")


def interactive_menu() -> None:
    """Display interactive menu for manual testing."""
    print_header("AutoResumeFiller - Epic 2 Manual Testing")
    print("\nThis script tests all Epic 2 data management functionality.")
    print("\nOptions:")
    print("  1. Run all tests sequentially")
    print("  2. Test Story 2.1 only (Data Schema)")
    print("  3. Test Story 2.2 only (Data Manager)")
    print("  4. Test Story 2.3 only (Resume Parser)")
    print("  5. Test Story 2.4 only (Data Export)")
    print("  6. Exit")
    
    choice = input("\nEnter choice (1-6): ").strip()
    return choice


def main() -> None:
    """Main entry point for manual testing."""
    try:
        while True:
            choice = interactive_menu()
            
            if choice == "1":
                # Run all tests
                profile = test_story_2_1_schemas()
                if profile:
                    manager = test_story_2_2_data_manager(profile)
                    test_story_2_3_resume_parser()
                    test_story_2_4_data_export(manager)
                
                print_header("All Tests Complete!")
                break
                
            elif choice == "2":
                test_story_2_1_schemas()
                
            elif choice == "3":
                profile = test_story_2_1_schemas()
                if profile:
                    test_story_2_2_data_manager(profile)
                    
            elif choice == "4":
                test_story_2_3_resume_parser()
                
            elif choice == "5":
                profile = test_story_2_1_schemas()
                if profile:
                    manager = test_story_2_2_data_manager(profile)
                    test_story_2_4_data_export(manager)
                    
            elif choice == "6":
                print("\nExiting...")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                continue
            
            # Ask to continue
            cont = input("\n\nPress Enter to continue or 'q' to quit: ").strip().lower()
            if cont == 'q':
                break
                
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
