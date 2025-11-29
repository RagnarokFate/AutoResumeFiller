"""
Data services package for AutoResumeFiller.

This package contains all data-related services including:
- schemas: Pydantic data models
- user_data_manager: File system data operations
- file_parser: Resume document parsing (PDF/DOCX)
- encryption: Data encryption at rest
- version_manager: Resume/cover letter version management
"""

from .schemas import (
    PersonalInfo,
    Education,
    WorkExperience,
    Project,
    Certification,
    UserProfile
)
from .user_data_manager import UserDataManager
from .file_parser import FileParser

__all__ = [
    'PersonalInfo',
    'Education',
    'WorkExperience',
    'Project',
    'Certification',
    'UserProfile',
    'UserDataManager',
    'FileParser'
]
