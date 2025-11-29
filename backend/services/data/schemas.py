"""
Pydantic data schemas for AutoResumeFiller.

Defines the data models for:
- PersonalInfo: User's personal/contact information
- Education: Educational background entries
- WorkExperience: Work history entries
- Project: Project portfolio entries
- Certification: Professional certifications
- UserProfile: Complete user profile (combines all above)

All schemas use Pydantic v2 for validation and serialization.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, model_validator, ConfigDict
import re


class PersonalInfo(BaseModel):
    """
    User's personal and contact information.
    
    Used for basic form fields like name, email, phone, and portfolio links.
    """
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    email: EmailStr = Field(..., description="Primary email address")
    phone: Optional[str] = Field(None, pattern=r"^\+?1?\d{9,15}$", description="Phone number (9-15 digits, optional +1 prefix)")
    
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[HttpUrl] = Field(None, description="Personal portfolio website URL")
    
    address: Optional[str] = Field(None, max_length=200, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State/Province")
    zip_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")
    country: str = Field(default="USA", max_length=100, description="Country")
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+11234567890",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "github_url": "https://github.com/johndoe",
                "portfolio_url": "https://johndoe.dev",
                "address": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94102",
                "country": "USA"
            }
        }


class Education(BaseModel):
    """
    Educational background entry.
    
    Represents a degree, certificate, or educational program.
    """
    institution: str = Field(..., min_length=1, max_length=200, description="School/University name")
    degree: str = Field(..., min_length=1, max_length=100, description="Degree type (e.g., Bachelor of Science)")
    field_of_study: str = Field(..., min_length=1, max_length=150, description="Major/Field of study")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Start date in YYYY-MM format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM format or 'Present'")
    
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA on 4.0 scale")
    honors: Optional[List[str]] = Field(default_factory=list, description="Honors and awards")
    relevant_coursework: Optional[List[str]] = Field(default_factory=list, description="Relevant courses")
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate end_date is either YYYY-MM format or 'Present'"""
        if v is None:
            return v
        if v == "Present":
            return v
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("end_date must be in YYYY-MM format or 'Present'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "institution": "Stanford University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "start_date": "2016-09",
                "end_date": "2020-06",
                "gpa": 3.8,
                "honors": ["Cum Laude", "Dean's List"],
                "relevant_coursework": ["Data Structures", "Machine Learning", "Algorithms"]
            }
        }


class WorkExperience(BaseModel):
    """
    Work experience entry.
    
    Represents a job position with company, role, dates, and accomplishments.
    """
    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    position: str = Field(..., min_length=1, max_length=150, description="Job title/position")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Start date in YYYY-MM format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM format or 'Present'")
    
    location: Optional[str] = Field(None, max_length=150, description="Job location (e.g., 'San Francisco, CA')")
    responsibilities: List[str] = Field(..., min_length=1, description="List of responsibilities (min 1 required)")
    achievements: Optional[List[str]] = Field(default_factory=list, description="Key achievements with metrics")
    technologies: Optional[List[str]] = Field(default_factory=list, description="Technologies/tools used")
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate end_date is either YYYY-MM format or 'Present'"""
        if v is None:
            return v
        if v == "Present":
            return v
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("end_date must be in YYYY-MM format or 'Present'")
        return v
    
    @field_validator('responsibilities')
    @classmethod
    def validate_responsibilities(cls, v: List[str]) -> List[str]:
        """Ensure at least one responsibility is provided"""
        if not v or len(v) == 0:
            raise ValueError("At least one responsibility is required")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "company": "Google",
                "position": "Senior Software Engineer",
                "start_date": "2020-07",
                "end_date": "Present",
                "location": "Mountain View, CA",
                "responsibilities": [
                    "Led development of cloud infrastructure services",
                    "Mentored team of 5 junior engineers",
                    "Designed scalable microservices architecture"
                ],
                "achievements": [
                    "Reduced latency by 40% through optimization",
                    "Increased system throughput by 3x"
                ],
                "technologies": ["Python", "Kubernetes", "Docker", "PostgreSQL", "gRPC"]
            }
        }


class Project(BaseModel):
    """
    Personal or professional project entry.
    
    Showcases side projects, open source contributions, or portfolio work.
    """
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: str = Field(..., min_length=1, max_length=1000, description="Project description")
    
    start_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$", description="Start date in YYYY-MM format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM format or 'Present'")
    url: Optional[HttpUrl] = Field(None, description="Project URL (GitHub, demo, etc.)")
    
    technologies: Optional[List[str]] = Field(default_factory=list, description="Technologies used")
    highlights: Optional[List[str]] = Field(default_factory=list, description="Key features or accomplishments")
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate end_date is either YYYY-MM format or 'Present'"""
        if v is None:
            return v
        if v == "Present":
            return v
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("end_date must be in YYYY-MM format or 'Present'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "AutoResumeFiller",
                "description": "AI-powered job application automation tool",
                "start_date": "2024-11",
                "end_date": "Present",
                "url": "https://github.com/johndoe/autoresumefiller",
                "technologies": ["Python", "FastAPI", "React", "OpenAI GPT-4"],
                "highlights": [
                    "Automated 80% of form filling tasks",
                    "Reduced application time from 20 min to 2 min"
                ]
            }
        }


class Certification(BaseModel):
    """
    Professional certification entry.
    
    Represents certifications, licenses, or credentials.
    """
    name: str = Field(..., min_length=1, max_length=200, description="Certification name")
    issuer: str = Field(..., min_length=1, max_length=150, description="Issuing organization")
    date_obtained: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Date obtained in YYYY-MM format")
    
    expiration_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$", description="Expiration date in YYYY-MM format")
    credential_id: Optional[str] = Field(None, max_length=100, description="Credential ID or license number")
    url: Optional[HttpUrl] = Field(None, description="Verification URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date_obtained": "2023-06",
                "expiration_date": "2026-06",
                "credential_id": "AWS-12345",
                "url": "https://www.credly.com/badges/12345"
            }
        }


class UserProfile(BaseModel):
    """
    Complete user profile combining all data types.
    
    This is the top-level schema for user data storage.
    Includes personal info, education, work experience, projects, certifications, and skills.
    """
    version: str = Field(default="1.0", description="Schema version for data migration compatibility")
    last_updated: datetime = Field(default_factory=datetime.now, description="Timestamp of last profile update")
    
    personal_info: PersonalInfo = Field(..., description="Personal and contact information")
    
    education: List[Education] = Field(default_factory=list, description="Educational background")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="Work history")
    skills: List[str] = Field(default_factory=list, description="Technical and soft skills")
    projects: List[Project] = Field(default_factory=list, description="Personal/professional projects")
    certifications: List[Certification] = Field(default_factory=list, description="Certifications and licenses")
    
    summary: Optional[str] = Field(None, max_length=2000, description="Professional summary or bio")
    
    @model_validator(mode='after')
    def update_timestamp(self):
        """Auto-update last_updated timestamp on any modification"""
        self.last_updated = datetime.now()
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "last_updated": "2025-11-29T10:00:00",
                "personal_info": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+11234567890",
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "USA"
                },
                "education": [],
                "work_experience": [],
                "skills": ["Python", "JavaScript", "React", "Docker"],
                "projects": [],
                "certifications": [],
                "summary": "Experienced software engineer with 5+ years in backend development."
            }
        }
