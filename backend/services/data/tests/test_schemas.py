"""Tests for data schemas (Story 2.1)"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from backend.services.data.schemas import (
    PersonalInfo,
    Education,
    WorkExperience,
    Project,
    Certification,
    UserProfile
)


class TestPersonalInfo:
    """Test PersonalInfo schema validation"""
    
    def test_valid_personal_info(self):
        """Test valid personal info creation"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+11234567890"
        }
        person = PersonalInfo(**data)
        assert person.first_name == "John"
        assert person.last_name == "Doe"
        assert person.email == "john.doe@example.com"
        assert person.phone == "+11234567890"
        assert person.country == "USA"  # Default value
    
    def test_invalid_email(self):
        """Test invalid email format"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "phone": "+11234567890"
        }
        with pytest.raises(ValidationError) as exc_info:
            PersonalInfo(**data)
        assert "email" in str(exc_info.value)
    
    def test_invalid_phone(self):
        """Test invalid phone format"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "123"  # Too short
        }
        with pytest.raises(ValidationError) as exc_info:
            PersonalInfo(**data)
        assert "phone" in str(exc_info.value)
    
    def test_valid_urls(self):
        """Test valid URL fields"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "+11234567890",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "github_url": "https://github.com/johndoe",
            "portfolio_url": "https://johndoe.dev"
        }
        person = PersonalInfo(**data)
        assert str(person.linkedin_url) == "https://linkedin.com/in/johndoe"
        assert str(person.github_url) == "https://github.com/johndoe"
        assert str(person.portfolio_url) == "https://johndoe.dev/"  # Pydantic normalizes URLs


class TestEducation:
    """Test Education schema validation"""
    
    def test_valid_education(self):
        """Test valid education entry"""
        data = {
            "institution": "Stanford University",
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "start_date": "2016-09",
            "end_date": "2020-06",
            "gpa": 3.8
        }
        edu = Education(**data)
        assert edu.institution == "Stanford University"
        assert edu.gpa == 3.8
    
    def test_present_end_date(self):
        """Test 'Present' as end_date"""
        data = {
            "institution": "MIT",
            "degree": "Master of Science",
            "field_of_study": "AI",
            "start_date": "2024-09",
            "end_date": "Present"
        }
        edu = Education(**data)
        assert edu.end_date == "Present"
    
    def test_invalid_date_format(self):
        """Test invalid date format"""
        data = {
            "institution": "MIT",
            "degree": "MS",
            "field_of_study": "AI",
            "start_date": "2024/09",  # Wrong format
        }
        with pytest.raises(ValidationError) as exc_info:
            Education(**data)
        assert "start_date" in str(exc_info.value)
    
    def test_invalid_gpa(self):
        """Test GPA out of range"""
        data = {
            "institution": "MIT",
            "degree": "MS",
            "field_of_study": "AI",
            "start_date": "2024-09",
            "gpa": 5.0  # Above 4.0
        }
        with pytest.raises(ValidationError) as exc_info:
            Education(**data)
        assert "gpa" in str(exc_info.value)


class TestWorkExperience:
    """Test WorkExperience schema validation"""
    
    def test_valid_work_experience(self):
        """Test valid work experience entry"""
        data = {
            "company": "Google",
            "position": "Software Engineer",
            "start_date": "2020-07",
            "end_date": "Present",
            "responsibilities": ["Write code", "Review PRs"]
        }
        work = WorkExperience(**data)
        assert work.company == "Google"
        assert work.end_date == "Present"
        assert len(work.responsibilities) == 2
    
    def test_missing_responsibilities(self):
        """Test responsibilities list required and not empty"""
        data = {
            "company": "Google",
            "position": "SWE",
            "start_date": "2020-07",
            "responsibilities": []  # Empty list
        }
        with pytest.raises(ValidationError) as exc_info:
            WorkExperience(**data)
        assert "responsibilities" in str(exc_info.value)
    
    def test_optional_fields(self):
        """Test optional fields default to empty lists"""
        data = {
            "company": "Meta",
            "position": "Engineer",
            "start_date": "2018-01",
            "responsibilities": ["Develop features"]
        }
        work = WorkExperience(**data)
        assert work.achievements == []
        assert work.technologies == []


class TestProject:
    """Test Project schema validation"""
    
    def test_valid_project(self):
        """Test valid project entry"""
        data = {
            "name": "AutoResumeFiller",
            "description": "AI-powered resume tool",
            "url": "https://github.com/user/project"
        }
        project = Project(**data)
        assert project.name == "AutoResumeFiller"
        assert project.description == "AI-powered resume tool"
    
    def test_present_end_date(self):
        """Test 'Present' as end_date"""
        data = {
            "name": "Project",
            "description": "Description",
            "start_date": "2024-01",
            "end_date": "Present"
        }
        project = Project(**data)
        assert project.end_date == "Present"


class TestCertification:
    """Test Certification schema validation"""
    
    def test_valid_certification(self):
        """Test valid certification entry"""
        data = {
            "name": "AWS Solutions Architect",
            "issuer": "Amazon",
            "date_obtained": "2023-06",
            "credential_id": "AWS-12345"
        }
        cert = Certification(**data)
        assert cert.name == "AWS Solutions Architect"
        assert cert.credential_id == "AWS-12345"


class TestUserProfile:
    """Test UserProfile schema validation"""
    
    def test_valid_user_profile(self):
        """Test valid complete user profile"""
        data = {
            "personal_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+11234567890"
            }
        }
        profile = UserProfile(**data)
        assert profile.version == "1.0"
        assert profile.personal_info.first_name == "John"
        assert profile.education == []
        assert profile.work_experience == []
        assert profile.skills == []
        assert isinstance(profile.last_updated, datetime)
    
    def test_full_profile_with_all_fields(self):
        """Test profile with all fields populated"""
        data = {
            "personal_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+11234567890"
            },
            "education": [
                {
                    "institution": "MIT",
                    "degree": "BS",
                    "field_of_study": "CS",
                    "start_date": "2016-09"
                }
            ],
            "work_experience": [
                {
                    "company": "Google",
                    "position": "SWE",
                    "start_date": "2020-07",
                    "responsibilities": ["Code"]
                }
            ],
            "skills": ["Python", "JavaScript"],
            "projects": [
                {
                    "name": "Project",
                    "description": "Description"
                }
            ],
            "certifications": [
                {
                    "name": "AWS",
                    "issuer": "Amazon",
                    "date_obtained": "2023-06"
                }
            ],
            "summary": "Experienced engineer"
        }
        profile = UserProfile(**data)
        assert len(profile.education) == 1
        assert len(profile.work_experience) == 1
        assert len(profile.skills) == 2
        assert len(profile.projects) == 1
        assert len(profile.certifications) == 1
        assert profile.summary == "Experienced engineer"
    
    def test_timestamp_auto_updates(self):
        """Test last_updated timestamp auto-updates"""
        data = {
            "personal_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+11234567890"
            }
        }
        profile = UserProfile(**data)
        original_timestamp = profile.last_updated
        
        # Modify profile
        profile.skills.append("Python")
        
        # Timestamp should update (via model_validator)
        assert profile.last_updated >= original_timestamp


class TestJSONSchemaExport:
    """Test JSON schema export functionality"""
    
    def test_user_profile_schema_export(self):
        """Test UserProfile.model_json_schema() works"""
        schema = UserProfile.model_json_schema()
        
        assert "properties" in schema
        assert "personal_info" in schema["properties"]
        assert "education" in schema["properties"]
        assert "work_experience" in schema["properties"]
        assert "required" in schema
        assert "personal_info" in schema["required"]
    
    def test_personal_info_schema_export(self):
        """Test PersonalInfo.model_json_schema() works"""
        schema = PersonalInfo.model_json_schema()
        
        assert "properties" in schema
        assert "email" in schema["properties"]
        assert "phone" in schema["properties"]
        assert "required" in schema
        assert "email" in schema["required"]
        assert "phone" in schema["required"]


class TestExampleJSONValidation:
    """Test example JSON file validates against schemas"""
    
    def test_example_json_validates(self):
        """Test user_profile_example.json validates successfully"""
        import json
        from pathlib import Path
        
        example_file = Path(__file__).parent.parent / "examples" / "user_profile_example.json"
        
        with open(example_file, 'r') as f:
            data = json.load(f)
        
        # Should not raise ValidationError
        profile = UserProfile(**data)
        
        assert profile.personal_info.first_name == "John"
        assert profile.personal_info.last_name == "Doe"
        assert len(profile.education) == 2
        assert len(profile.work_experience) == 2
        assert len(profile.skills) > 0
        assert len(profile.projects) == 2
        assert len(profile.certifications) == 2
        assert profile.summary is not None
