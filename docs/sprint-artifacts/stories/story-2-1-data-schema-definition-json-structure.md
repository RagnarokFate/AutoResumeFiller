# Story 2.1: Data Schema Definition (JSON Structure)

**Story ID:** 2.1  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 1  
**Estimated Effort:** Small (1-2 days)  
**Priority:** Critical  

---

## User Story

**As a** developer  
**I want** Pydantic data models for all user data types  
**So that** I can validate, serialize, and enforce data integrity across the application

---

## Context

This story establishes the foundational data schemas for AutoResumeFiller using Pydantic v2. These schemas define the structure for personal information, education, work experience, projects, certifications, and the complete user profile. The schemas will be used by all subsequent Epic 2 stories and throughout the application for data validation, API contracts, and JSON serialization.

**Current State:**
- Backend scaffolding exists from Story 1.2
- No data models defined yet
- Need type-safe structures for user data

**Desired State:**
- Pydantic models in `backend/services/data/schemas.py`
- All data types validated with proper rules
- JSON schema export capability for API documentation
- Example JSON file demonstrating structure

---

## Dependencies

**Prerequisites:**
- Story 1.2: Python Backend Scaffolding ✅ (DONE)
- Story 1.6: Testing Infrastructure ✅ (DONE)

**Blocks:**
- Story 2.2: File System Data Manager (needs schemas)
- Story 2.3: Resume Document Parser (needs schemas)
- All other Epic 2 stories

---

## Acceptance Criteria

### AC1: PersonalInfo Schema Defined
**Given** Pydantic model for personal information  
**When** validating sample personal data  
**Then** schema validates successfully with:
- Required: first_name, last_name, email, phone
- Optional: linkedin_url, github_url, portfolio_url, address, city, state, zip_code, country
- EmailStr validation for email field
- HttpUrl validation for URL fields
- Phone regex validation: `^\+?1?\d{9,15}$`
- Default country: "USA"

### AC2: Education Schema Defined
**Given** Pydantic model for education entries  
**When** validating sample education data  
**Then** schema validates successfully with:
- Required: institution, degree, field_of_study, start_date
- Optional: end_date, gpa, honors, relevant_coursework
- Date format: YYYY-MM (e.g., "2020-09")
- end_date supports "Present" for current education
- GPA validation: 0.0-4.0 range
- Lists for honors and coursework

### AC3: WorkExperience Schema Defined
**Given** Pydantic model for work experience entries  
**When** validating sample work data  
**Then** schema validates successfully with:
- Required: company, position, start_date, responsibilities (min 1 item)
- Optional: end_date, location, achievements, technologies
- Date format: YYYY-MM
- end_date supports "Present" for current positions
- responsibilities list requires at least 1 item
- achievements and technologies are optional lists

### AC4: Project Schema Defined
**Given** Pydantic model for project entries  
**When** validating sample project data  
**Then** schema validates successfully with:
- Required: name, description
- Optional: start_date, end_date, url, technologies, highlights
- Date format: YYYY-MM
- HttpUrl validation for url field
- technologies and highlights are optional lists

### AC5: Certification Schema Defined
**Given** Pydantic model for certification entries  
**When** validating sample certification data  
**Then** schema validates successfully with:
- Required: name, issuer, date_obtained
- Optional: expiration_date, credential_id, url
- Date format: YYYY-MM
- HttpUrl validation for url field
- credential_id is optional string

### AC6: UserProfile Schema Defined
**Given** Pydantic model for complete user profile  
**When** validating sample profile data  
**Then** schema validates successfully with:
- Required: version, personal_info
- Optional: education, work_experience, skills, projects, certifications, summary
- Lists default to empty if not provided
- last_updated auto-populated with current timestamp
- version defaults to "1.0"

### AC7: Invalid Data Rejected
**Given** invalid data for any schema  
**When** validation is attempted  
**Then** ValidationError raised with:
- Clear error messages indicating which fields failed
- Specific validation rules violated
- Field paths for nested validation errors
- No data saved if validation fails

### AC8: JSON Schema Export Works
**Given** any Pydantic model  
**When** calling model_json_schema()  
**Then** returns OpenAPI-compatible JSON schema with:
- All field definitions
- Required vs optional fields
- Validation rules (pattern, min, max)
- Field descriptions
- Nested object schemas

### AC9: Example JSON Created
**Given** complete schema definitions  
**When** creating example file  
**Then** `backend/services/data/examples/user_profile_example.json` contains:
- Valid sample data for all fields
- Demonstrates proper date formats
- Shows nested structures
- Comments explaining field purposes
- Validates successfully against UserProfile schema

---

## Tasks

### Task 1: Create Schemas Module
**Description:** Set up the module structure for Pydantic schemas

**Subtasks:**
1. Create directory: `backend/services/data/`
2. Create file: `backend/services/data/__init__.py`
3. Create file: `backend/services/data/schemas.py`
4. Add imports: pydantic (BaseModel, Field, EmailStr, HttpUrl), typing (List, Optional), datetime

**Acceptance:** Module structure created and importable

---

### Task 2: Implement PersonalInfo Schema
**Description:** Define Pydantic model for personal information

**Subtasks:**
1. Create PersonalInfo class inheriting from BaseModel
2. Add required fields: first_name, last_name, email (EmailStr), phone (with regex pattern)
3. Add optional fields: linkedin_url, github_url, portfolio_url (HttpUrl)
4. Add optional address fields: address, city, state, zip_code
5. Set country default: "USA"
6. Add field descriptions using Field(description="...")

**Acceptance:** PersonalInfo validates email, phone, and URLs correctly

---

### Task 3: Implement Education Schema
**Description:** Define Pydantic model for education entries

**Subtasks:**
1. Create Education class inheriting from BaseModel
2. Add required fields: institution, degree, field_of_study, start_date (YYYY-MM pattern)
3. Add optional fields: end_date (YYYY-MM or "Present"), gpa (0.0-4.0), honors (list), relevant_coursework (list)
4. Add date format validation: `Field(..., pattern=r'^\d{4}-\d{2}$')`
5. Add GPA validation: `Field(None, ge=0.0, le=4.0)`
6. Default empty lists for honors and coursework

**Acceptance:** Education validates date formats and GPA range

---

### Task 4: Implement WorkExperience Schema
**Description:** Define Pydantic model for work experience entries

**Subtasks:**
1. Create WorkExperience class inheriting from BaseModel
2. Add required fields: company, position, start_date, responsibilities (min_items=1)
3. Add optional fields: end_date ("Present" support), location, achievements, technologies
4. Add date format validation for start_date and end_date
5. Validate responsibilities list has at least 1 item
6. Default empty lists for achievements and technologies

**Acceptance:** WorkExperience validates dates and requires at least 1 responsibility

---

### Task 5: Implement Project and Certification Schemas
**Description:** Define Pydantic models for projects and certifications

**Subtasks:**
1. Create Project class with required fields: name, description
2. Add optional Project fields: start_date, end_date, url (HttpUrl), technologies, highlights
3. Create Certification class with required fields: name, issuer, date_obtained
4. Add optional Certification fields: expiration_date, credential_id, url (HttpUrl)
5. Add date format validation for all date fields
6. Default empty lists where appropriate

**Acceptance:** Both schemas validate URLs and date formats

---

### Task 6: Implement UserProfile Schema
**Description:** Define top-level Pydantic model aggregating all data

**Subtasks:**
1. Create UserProfile class inheriting from BaseModel
2. Add version field with default "1.0"
3. Add personal_info field (required): PersonalInfo
4. Add list fields (optional, default []): education, work_experience, projects, certifications
5. Add skills field (optional, default []): List[str]
6. Add summary field (optional): Optional[str]
7. Add last_updated field with default_factory: datetime.now
8. Add model_json_schema() export test

**Acceptance:** UserProfile aggregates all schemas with proper defaults

---

### Task 7: Create Unit Tests
**Description:** Write comprehensive unit tests for all schemas

**Subtasks:**
1. Create `backend/services/data/tests/__init__.py`
2. Create `backend/services/data/tests/test_schemas.py`
3. Write test_personal_info_valid_data() - validates correct data
4. Write test_personal_info_invalid_email() - rejects bad email
5. Write test_personal_info_invalid_phone() - rejects bad phone
6. Write test_education_valid_data() - validates education entry
7. Write test_education_invalid_gpa() - rejects GPA >4.0 or <0.0
8. Write test_work_experience_valid_data() - validates work entry
9. Write test_work_experience_empty_responsibilities() - rejects empty list
10. Write test_project_valid_data() - validates project entry
11. Write test_certification_valid_data() - validates certification entry
12. Write test_user_profile_complete() - validates full profile
13. Write test_user_profile_minimal() - validates minimal profile (only personal_info)
14. Write test_json_schema_export() - validates model_json_schema() output
15. Use pytest fixtures for sample valid/invalid data

**Acceptance:** All tests pass with >90% coverage on schemas.py

---

### Task 8: Create Example JSON File
**Description:** Create sample user_profile.json demonstrating structure

**Subtasks:**
1. Create directory: `backend/services/data/examples/`
2. Create file: `user_profile_example.json`
3. Add complete PersonalInfo with all fields populated
4. Add 2 Education entries (one with "Present" end_date)
5. Add 3 WorkExperience entries (one current job)
6. Add 5-10 skills as string array
7. Add 2 Project entries with technologies
8. Add 1-2 Certification entries
9. Add professional summary (2-3 sentences)
10. Validate JSON parses correctly and matches UserProfile schema
11. Add inline comments explaining field purposes (if JSON5 used) or create separate README

**Acceptance:** Example JSON validates successfully against UserProfile schema

---

### Task 9: Add JSON Schema Documentation
**Description:** Export JSON schema for API documentation

**Subtasks:**
1. Create script: `backend/services/data/export_schema.py`
2. Import UserProfile from schemas
3. Call UserProfile.model_json_schema()
4. Save output to: `backend/services/data/schemas/user_profile_schema.json`
5. Format JSON with proper indentation
6. Verify schema is OpenAPI 3.0 compatible
7. Add script to pytest tests to ensure schema exports correctly

**Acceptance:** JSON schema file generated and validates in JSON Schema validator

---

### Task 10: Update Documentation
**Description:** Document schemas in README

**Subtasks:**
1. Update `backend/services/data/README.md` (create if not exists)
2. Document each schema with field descriptions
3. Add examples of valid data
4. Document validation rules
5. Link to example JSON file
6. Add usage examples for creating UserProfile instances
7. Document how to export JSON schema

**Acceptance:** README clearly explains all schemas and their usage

---

## Technical Notes

### Pydantic Configuration
```python
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator
from typing import List, Optional
from datetime import datetime

class PersonalInfo(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$', description="Phone number")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[HttpUrl] = Field(None, description="Portfolio website URL")
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')
    country: str = Field(default="USA", max_length=100)
```

### Date Validation Pattern
```python
class Education(BaseModel):
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}$', description="Start date (YYYY-MM)")
    end_date: Optional[str] = Field(None, pattern=r'^(\d{4}-\d{2}|Present)$', description="End date (YYYY-MM) or 'Present'")
```

### Custom Validators (Optional Enhancement)
```python
from pydantic import field_validator

class WorkExperience(BaseModel):
    start_date: str
    end_date: Optional[str] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        if v and v != "Present":
            # Could add logic to ensure end_date >= start_date
            pass
        return v
```

### Testing Strategy
- **Unit Tests:** Test each schema independently with valid/invalid data
- **Integration Tests:** Test UserProfile with nested schemas
- **Edge Cases:** Empty lists, "Present" dates, missing optional fields, invalid formats
- **Performance:** Validation should be <1ms per model instance

---

## Definition of Done

- [ ] All 6 Pydantic schemas implemented (PersonalInfo, Education, WorkExperience, Project, Certification, UserProfile)
- [ ] All schemas validate correctly with proper error messages
- [ ] Email, URL, phone, date format validation works
- [ ] GPA range validation (0.0-4.0) works
- [ ] responsibilities list requires at least 1 item
- [ ] UserProfile has proper defaults (version="1.0", empty lists, auto timestamp)
- [ ] JSON schema export works via model_json_schema()
- [ ] Example JSON file created and validates successfully
- [ ] Unit tests written with >90% coverage
- [ ] All 9 acceptance criteria validated
- [ ] Documentation updated in README
- [ ] Code follows PEP 8 and passes linting (black, pylint, mypy)
- [ ] No breaking changes to existing backend code

---

## Traceability

**PRD References:**
- FR1: Create and manage local data repository
- FR2: Choose single master file or multiple category files

**Architecture References:**
- Section: Data Models and Contracts
- Component: backend/services/data/schemas.py

**Epic Tech Spec:**
- AC1: Data Schemas Defined and Validated
- Section: Data Models and Contracts → Pydantic Schemas

---

## Notes

- Use Pydantic v2 syntax (Field(...) instead of Field(default=...))
- Consider adding custom validators for complex business logic (e.g., date range validation)
- JSON schema export enables OpenAPI documentation generation
- Schemas should be immutable once released (use versioning for breaking changes)
- Example JSON should demonstrate real-world use cases
- Keep validation rules in sync with database constraints (if database added later)
