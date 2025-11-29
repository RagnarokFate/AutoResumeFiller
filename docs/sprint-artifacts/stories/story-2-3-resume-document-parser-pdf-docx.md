# Story 2.3: Resume Document Parser (PDF & DOCX)

**Story ID:** 2.3  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 2  
**Estimated Effort:** Large (3-5 days)  
**Priority:** High  

---

## User Story

**As a** user  
**I want** to import my existing resume from PDF or DOCX files  
**So that** I can quickly populate my profile without manual data entry

---

## Context

This story implements resume parsing functionality to extract structured data from PDF and DOCX files. The parser uses pdfplumber for PDF extraction and python-docx for DOCX parsing, applying heuristic rules to identify sections (Personal Info, Work Experience, Education, Skills, Projects) and extract data with 80%+ accuracy. Parsed data is validated against Pydantic schemas and returned with confidence scores and warnings.

**Current State:**
- Schemas defined (Story 2.1)
- File system operations ready (Story 2.2)
- No parsing capability exists

**Desired State:**
- Parse PDF resumes in <3 seconds (10-page documents)
- Parse DOCX resumes in <1 second
- Extract personal info, work history, education, skills with 80%+ accuracy
- Handle multiple resume formats and layouts
- Provide confidence scores and warnings for ambiguous sections

---

## Dependencies

**Prerequisites:**
- Story 2.1: Data Schema Definition ✅ (Required - validates parsed data)
- Story 2.2: File System Data Manager ✅ (Required - saves parsed data)

**Optional Dependencies:**
- Story 3.2: OpenAI Provider (future: AI-enhanced parsing)

---

## Acceptance Criteria

### AC1: PDF Text Extraction Works
**Given** PDF resume file (searchable, not scanned)  
**When** calling `FileParser.parse_pdf(file_path)`  
**Then** text extracted successfully using pdfplumber:
- All pages processed
- Text preserves reasonable formatting (newlines, spacing)
- Tables detected and extracted separately
- Parsing completes in <3 seconds for 10-page document

**And** returns dict with:
```python
{
  "raw_text": "Complete resume text...",
  "pages": 5,
  "tables": [...],  # Extracted table data
  "parsing_time_ms": 2345
}
```

### AC2: DOCX Text Extraction Works
**Given** DOCX resume file  
**When** calling `FileParser.parse_docx(file_path)`  
**Then** text extracted successfully using python-docx:
- All paragraphs extracted
- Tables detected and extracted
- Formatting preserved (bold, headers)
- Parsing completes in <1 second for 10-page document

**And** returns dict with same structure as PDF

### AC3: Personal Info Extracted
**Given** resume text with personal information section  
**When** calling `FileParser.extract_personal_info(text)`  
**Then** personal info extracted with 90%+ accuracy:
- **Name:** Detected from first few lines or header (regex patterns, name dictionaries)
- **Email:** Extracted with regex: `r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'`
- **Phone:** Extracted with regex: `r'\+?1?\d{9,15}'` (handles +1, country codes, various formats)
- **LinkedIn:** URL pattern: `linkedin.com/in/...`
- **GitHub:** URL pattern: `github.com/...`
- **Portfolio:** URL pattern matching (http/https URLs)
- **Address:** City, state, ZIP extracted if present

**And** returns PersonalInfo dict (validated against schema)  
**And** includes confidence score (0.0-1.0) for each field

### AC4: Work Experience Extracted
**Given** resume text with work experience section  
**When** calling `FileParser.extract_work_experience(text)`  
**Then** work entries extracted with 80%+ accuracy:
- **Section detection:** Keywords: "Experience", "Work History", "Employment"
- **Company names:** Capitalized words, known company patterns
- **Positions:** Job titles (Engineer, Manager, Developer, etc.)
- **Dates:** Regex patterns for MM/YYYY, Month YYYY, etc. (e.g., "Jan 2020 - Dec 2022")
- **Present jobs:** Detect "Present", "Current", "Now"
- **Responsibilities:** Bullet points or paragraphs under each job
- **Technologies:** Tech keywords (Python, Java, AWS, React, etc.)

**And** returns List[WorkExperience] (validated against schema)  
**And** includes warnings for ambiguous dates or missing required fields

### AC5: Education Extracted
**Given** resume text with education section  
**When** calling `FileParser.extract_education(text)`  
**Then** education entries extracted with 85%+ accuracy:
- **Section detection:** Keywords: "Education", "Academic", "Degrees"
- **Institution:** University/college names (known patterns, "University of...", etc.)
- **Degree:** BS, MS, PhD, Bachelor's, Master's, etc.
- **Field:** Major/specialization (Computer Science, Engineering, etc.)
- **Dates:** Graduation dates or date ranges
- **GPA:** Patterns: "3.8 GPA", "GPA: 3.8/4.0"
- **Honors:** Dean's List, Cum Laude, etc.

**And** returns List[Education] (validated against schema)  
**And** includes confidence scores per entry

### AC6: Skills Extracted
**Given** resume text with skills section  
**When** calling `FileParser.extract_skills(text)`  
**Then** skills list extracted with 75%+ accuracy:
- **Section detection:** Keywords: "Skills", "Technologies", "Technical Skills"
- **Skill detection:** Comma-separated lists, bullet points
- **Tech keywords:** Predefined list of 500+ common tech skills
- **Programming languages:** Python, Java, JavaScript, etc.
- **Frameworks:** React, Django, Spring, etc.
- **Tools:** Git, Docker, AWS, etc.

**And** returns List[str] deduplicated skills  
**And** excludes generic words ("and", "or", "including")

### AC7: Complete Profile Parsing Works
**Given** complete resume file (PDF or DOCX)  
**When** calling `FileParser.parse_resume(file_path)`  
**Then** returns complete parsed profile:
```python
{
  "personal_info": {...},       # PersonalInfo dict
  "work_experience": [...],     # List[WorkExperience]
  "education": [...],           # List[Education]
  "skills": [...],              # List[str]
  "projects": [...],            # List[Project] (optional)
  "certifications": [...],      # List[Certification] (optional)
  "confidence": 0.85,           # Overall confidence score
  "warnings": [                 # Warnings for user review
    "Could not parse GPA for degree entry",
    "Date format ambiguous for job entry 2"
  ],
  "parsing_time_ms": 2500
}
```

**And** data validates against UserProfile schema  
**And** parsing completes in <3 seconds for PDF, <1 second for DOCX

### AC8: Error Handling for Invalid Files
**Given** invalid or unsupported file  
**When** parsing is attempted  
**Then** clear errors returned:
- **Encrypted PDF:** "PDF is password-protected. Please provide unencrypted version."
- **Scanned PDF (image-based):** "PDF appears to be scanned image. OCR not supported. Accuracy will be low." (still attempt extraction)
- **Corrupted file:** "File is corrupted or unreadable."
- **Unsupported format:** "File format not supported. Use PDF or DOCX."
- **Empty file:** "File contains no text."

**And** no data modification occurs  
**And** suggests alternative actions

### AC9: Confidence Scores Calculated
**Given** parsed resume data  
**When** extraction completes  
**Then** confidence scores calculated:
- **Per-field confidence:** Based on pattern matches, validation success
- **Overall confidence:** Weighted average (Personal Info: 30%, Work: 40%, Education: 20%, Skills: 10%)
- **Thresholds:**
  - High confidence: >0.85 (green indicator)
  - Medium confidence: 0.60-0.85 (yellow indicator)
  - Low confidence: <0.60 (red indicator, manual review required)

**And** confidence scores included in response  
**And** warnings generated for low-confidence fields

---

## Tasks

### Task 1: Create FileParser Module
**Description:** Set up module structure for parsing

**Subtasks:**
1. Create file: `backend/services/data/file_parser.py`
2. Add imports: pdfplumber, python-docx, re, typing, pathlib
3. Import schemas from schemas.py
4. Define FileParser class
5. Add constants: TECH_KEYWORDS, DEGREE_PATTERNS, DATE_PATTERNS, etc.

**Acceptance:** Module created and importable

---

### Task 2: Implement PDF Text Extraction
**Description:** Extract text from PDF files using pdfplumber

**Subtasks:**
1. Install pdfplumber: `pip install pdfplumber`
2. Implement `parse_pdf(file_path: Path)` method:
   - Open PDF with pdfplumber.open()
   - Iterate through pages
   - Extract text: page.extract_text()
   - Extract tables: page.extract_tables()
   - Combine text from all pages
   - Measure parsing time
3. Handle encrypted PDFs (check is_encrypted property)
4. Detect scanned PDFs (low text/image ratio)
5. Add error handling for corrupted PDFs

**Acceptance:** PDF text extraction works in <3 seconds

---

### Task 3: Implement DOCX Text Extraction
**Description:** Extract text from DOCX files using python-docx

**Subtasks:**
1. Install python-docx: `pip install python-docx`
2. Implement `parse_docx(file_path: Path)` method:
   - Open DOCX with docx.Document()
   - Iterate through paragraphs
   - Extract text: paragraph.text
   - Detect tables: doc.tables
   - Preserve formatting (bold, headers)
   - Measure parsing time
3. Handle corrupted DOCX files
4. Add error handling for unsupported formats

**Acceptance:** DOCX text extraction works in <1 second

---

### Task 4: Implement Personal Info Extraction
**Description:** Extract personal information using regex and heuristics

**Subtasks:**
1. Implement `extract_personal_info(text: str)` method:
   - Email regex: `r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'`
   - Phone regex: `r'\+?1?\d{9,15}'`
   - LinkedIn URL: `r'linkedin\.com/in/[\w-]+'`
   - GitHub URL: `r'github\.com/[\w-]+'`
   - Name detection: First few lines, capitalized words
   - Address: City, state, ZIP patterns
2. Validate extracted data against PersonalInfo schema
3. Calculate confidence per field (pattern match quality)
4. Return PersonalInfo dict with confidence scores

**Acceptance:** Personal info extracted with 90%+ accuracy

---

### Task 5: Implement Work Experience Extraction
**Description:** Extract work history using section detection and patterns

**Subtasks:**
1. Implement `_find_section(text: str, keywords: List[str])` helper:
   - Search for section headers (case-insensitive)
   - Return section text (from header to next section)
2. Implement `extract_work_experience(text: str)` method:
   - Find "Experience" section
   - Split into job entries (date patterns as delimiters)
   - Extract company (capitalized words, known patterns)
   - Extract position (job title keywords)
   - Extract dates (MM/YYYY, Month YYYY, "Present")
   - Extract bullet points as responsibilities
   - Detect technologies (TECH_KEYWORDS matching)
3. Validate against WorkExperience schema
4. Calculate confidence per entry
5. Generate warnings for missing dates or responsibilities

**Acceptance:** Work experience extracted with 80%+ accuracy

---

### Task 6: Implement Education Extraction
**Description:** Extract education entries using patterns

**Subtasks:**
1. Implement `extract_education(text: str)` method:
   - Find "Education" section
   - Split into degree entries
   - Extract institution (university patterns, "University of...")
   - Extract degree (BS, MS, PhD, Bachelor's, Master's)
   - Extract field (major, specialization)
   - Extract dates (graduation year or date range)
   - Extract GPA ("3.8 GPA", "GPA: 3.8/4.0")
   - Extract honors (Dean's List, Cum Laude)
2. Validate against Education schema
3. Calculate confidence per entry

**Acceptance:** Education extracted with 85%+ accuracy

---

### Task 7: Implement Skills Extraction
**Description:** Extract skills list using keyword matching

**Subtasks:**
1. Create `TECH_KEYWORDS` list: 500+ common tech skills
   - Programming languages: Python, Java, JavaScript, C++, etc.
   - Frameworks: React, Django, Spring, Angular, etc.
   - Tools: Git, Docker, Kubernetes, AWS, etc.
   - Databases: MySQL, PostgreSQL, MongoDB, etc.
2. Implement `extract_skills(text: str)` method:
   - Find "Skills" section
   - Split by commas, bullet points, newlines
   - Match against TECH_KEYWORDS (case-insensitive)
   - Deduplicate skills
   - Exclude generic words ("and", "or", "including")
3. Return List[str] sorted alphabetically
4. Calculate confidence based on match rate

**Acceptance:** Skills extracted with 75%+ accuracy

---

### Task 8: Implement Complete Resume Parsing
**Description:** Orchestrate all extraction methods

**Subtasks:**
1. Implement `parse_resume(file_path: Path)` method:
   - Detect file type (PDF or DOCX)
   - Call parse_pdf() or parse_docx()
   - Extract personal_info
   - Extract work_experience
   - Extract education
   - Extract skills
   - Extract projects (optional, similar to work experience)
   - Extract certifications (optional)
2. Calculate overall confidence (weighted average)
3. Collect all warnings
4. Validate complete profile against UserProfile schema
5. Return parsed data dict with metadata
6. Measure total parsing time

**Acceptance:** Complete parsing works in <3 seconds for PDF, <1 second for DOCX

---

### Task 9: Implement Confidence Scoring
**Description:** Calculate confidence scores for parsed data

**Subtasks:**
1. Implement `_calculate_field_confidence(value, pattern)` helper:
   - Pattern match quality (1.0 if perfect, 0.5 if partial)
   - Validation success (1.0 if validates, 0.0 if fails)
   - Required field presence (1.0 if present, 0.0 if missing)
2. Implement `_calculate_overall_confidence()` method:
   - Personal Info: 30% weight
   - Work Experience: 40% weight
   - Education: 20% weight
   - Skills: 10% weight
   - Weighted average
3. Add confidence thresholds: HIGH (>0.85), MEDIUM (0.60-0.85), LOW (<0.60)
4. Generate warnings for low-confidence fields

**Acceptance:** Confidence scores calculated correctly

---

### Task 10: Add Error Handling
**Description:** Handle invalid files and edge cases

**Subtasks:**
1. Handle encrypted PDFs (raise error with message)
2. Detect scanned PDFs (warn user, attempt extraction anyway)
3. Handle corrupted files (raise error)
4. Handle unsupported formats (raise error)
5. Handle empty files (raise error)
6. Add logging for all errors
7. Return helpful error messages with suggestions

**Acceptance:** All error cases handled gracefully

---

### Task 11: Create Unit Tests
**Description:** Write comprehensive unit tests

**Subtasks:**
1. Create `backend/services/data/tests/test_file_parser.py`
2. Create sample resume files in `tests/fixtures/`:
   - sample_resume_simple.pdf
   - sample_resume_complex.pdf
   - sample_resume.docx
   - sample_resume_encrypted.pdf (test error handling)
3. Write test_parse_pdf_simple() - parse simple PDF
4. Write test_parse_docx() - parse DOCX
5. Write test_extract_personal_info() - validate email, phone, URLs
6. Write test_extract_work_experience() - validate entries
7. Write test_extract_education() - validate degrees
8. Write test_extract_skills() - validate skill list
9. Write test_parse_resume_complete() - full pipeline
10. Write test_encrypted_pdf_error() - error handling
11. Write test_confidence_scoring() - validate scores
12. Write test_performance() - verify <3s for PDF, <1s for DOCX
13. Use pytest fixtures for sample data

**Acceptance:** All tests pass with >75% coverage

---

### Task 12: Create Integration Tests
**Description:** Test with real-world resume examples

**Subtasks:**
1. Create `backend/services/data/tests/test_parser_integration.py`
2. Test with 10+ real resume formats:
   - Single-column layouts
   - Two-column layouts
   - Tables
   - Various date formats
   - Multiple pages
3. Measure accuracy on test set (target: 80%+)
4. Document known limitations
5. Generate test report with accuracy metrics

**Acceptance:** 80%+ accuracy on test set of 10+ resumes

---

## Technical Notes

### Regex Patterns
```python
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'\+?1?\d{9,15}'
DATE_PATTERNS = [
    r'(\d{1,2})/(\d{4})',           # MM/YYYY
    r'(\w+)\s+(\d{4})',              # Month YYYY
    r'(\d{4})-(\d{2})',              # YYYY-MM
    r'(\w+)\s+(\d{4})\s*-\s*(\w+)\s+(\d{4})'  # Month YYYY - Month YYYY
]
LINKEDIN_PATTERN = r'linkedin\.com/in/([\w-]+)'
GITHUB_PATTERN = r'github\.com/([\w-]+)'
```

### Tech Keywords List (Sample)
```python
TECH_KEYWORDS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala",
    
    # Frameworks
    "React", "Angular", "Vue", "Django", "Flask", "FastAPI", "Spring Boot",
    "Node.js", "Express", "Next.js", "Laravel",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    
    # Cloud & Tools
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Git",
    
    # ... 500+ total keywords
]
```

### Performance Optimization
- Use regex compilation: `re.compile(pattern)` for repeated use
- Limit text processing to first 20KB for section detection (most resumes front-load info)
- Cache TECH_KEYWORDS as frozenset for O(1) lookups
- Use multiprocessing for batch resume parsing (future enhancement)

---

## Definition of Done

- [ ] FileParser class implemented with all methods
- [ ] PDF text extraction works with pdfplumber (<3 seconds)
- [ ] DOCX text extraction works with python-docx (<1 second)
- [ ] Personal info extraction achieves 90%+ accuracy
- [ ] Work experience extraction achieves 80%+ accuracy
- [ ] Education extraction achieves 85%+ accuracy
- [ ] Skills extraction achieves 75%+ accuracy
- [ ] Complete resume parsing orchestrates all extractions
- [ ] Confidence scores calculated correctly
- [ ] Error handling for encrypted, scanned, corrupted files
- [ ] Unit tests written with >75% coverage
- [ ] Integration tests with 10+ real resumes (80%+ accuracy)
- [ ] All 9 acceptance criteria validated
- [ ] Performance targets met
- [ ] Documentation updated with examples

---

## Traceability

**PRD References:**
- FR3: Import existing resume data from PDF, Word (.docx), TXT, and LaTeX formats

**Architecture References:**
- Component: backend/services/data/file_parser.py
- Section: APIs and Interfaces → File Parsing

**Epic Tech Spec:**
- AC4: PDF Resume Parsing Extracts Data
- AC5: DOCX Resume Parsing Extracts Data
- Section: Detailed Design → File Parsing

---

## Notes

- Parsing accuracy depends on resume format consistency
- Consider AI-enhanced parsing in Epic 3 for better accuracy
- OCR support for scanned PDFs deferred (requires tesseract, adds complexity)
- LaTeX resume parsing deferred to Epic 7
- Two-column layouts are harder to parse (text extraction order issues)
- Consider adding parser configuration for custom section keywords
