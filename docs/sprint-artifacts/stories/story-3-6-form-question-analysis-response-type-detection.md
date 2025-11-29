# Story 3.6: Form Question Analysis & Response Type Detection

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.6  
**Story Name:** Form Question Analysis & Response Type Detection  
**Status:** Drafted  
**Effort Estimate:** Medium (2-3 days)  
**Priority:** High  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** system  
**I want** to determine if a question needs extraction (from user data) or generation (via AI)  
**So that** I optimize API usage and response quality (factual = extract, creative = generate)

## Context

This story implements **intelligent field classification** to decide whether to:
1. **Extract** factual data directly from user_profile.json (name, email, phone) - **no AI call**
2. **Generate** creative response via AI (motivation, achievements) - **AI call required**

**Benefits:**
- **Cost savings:** Factual fields don't need expensive AI calls
- **Speed:** Direct extraction <50ms vs AI generation ~2s
- **Accuracy:** User data is authoritative source for facts
- **Consistency:** Same factual data across all applications

**Classification Strategy:**
- **Rule-based patterns:** Regex matching on field labels
- **Confidence scoring:** 0.0-1.0 confidence in classification
- **Fallback:** If uncertain, default to AI generation (safer)

## Acceptance Criteria

### AC1: FormQuestionAnalyzer Classifies Field Types
**Given** field label "Email Address"  
**When** calling `analyzer.analyze_question(field)`  
**Then** returns `QuestionType`:
- `type`: "factual"
- `category`: "email"
- `strategy`: "extract"
- `data_path`: "personal_info.email"
- `confidence`: 0.98

### AC2: Factual Pattern Matching Works
**Given** factual field patterns (name, email, phone, address, date, etc.)  
**When** analyzing field labels:
- "Full Name" → factual, category=name
- "Email" → factual, category=email
- "Phone Number" → factual, category=phone
- "Start Date" → factual, category=date
- "GPA" → factual, category=gpa  
**Then** all classified correctly with confidence >0.9

### AC3: Creative Pattern Matching Works
**Given** creative field patterns  
**When** analyzing:
- "Why do you want this job?" → creative, category=motivation
- "Biggest achievement?" → creative, category=achievement
- "Greatest strength?" → creative, category=strength
- "Describe a challenge you overcame" → creative, category=challenge  
**Then** all classified as `strategy=generate` with confidence >0.8

### AC4: Extraction Strategy Retrieves Data
**Given** factual question (email)  
**When** calling `ResponseGenerator.extract_answer(question_type, user_data)`  
**Then** returns user's email directly from `user_data.personal_info.email`  
**And** no AI API call made  
**And** response time <50ms

### AC5: Generation Strategy Calls AI
**Given** creative question (motivation)  
**When** calling `ResponseGenerator.generate_answer(question, question_type, user_data, job_context)`  
**Then** AI provider called with prompt and context  
**And** returns AI-generated response  
**And** response tailored to question category

### AC6: Unknown Questions Default to Generation
**Given** field label that doesn't match any pattern: "Unusual question?"  
**When** analyzing  
**Then** returns `type=unknown`, `strategy=generate`, `confidence=0.5`  
**And** safely defaults to AI generation (avoids wrong extractions)

### AC7: Confidence Scores Calibrated
**Given** various field labels  
**Then** confidence scores reflect certainty:
- Exact match (e.g., "Email") → 0.98
- Close match (e.g., "E-mail Address") → 0.95
- Partial match (e.g., "Contact Email") → 0.85
- Ambiguous (e.g., "Availability?") → 0.6
- Unknown → 0.5

### AC8: Context Influences Classification
**Given** field label "Position"  
**When** field_type="text" and context="job application"  
**Then** classified as factual, category=job_title (extract from work experience)  
**When** field_type="textarea"  
**Then** classified as creative (describe ideal position) → generate

## Tasks

### Task 1: Define QuestionType Dataclass
- [ ] Create `backend/services/ai/question_analyzer.py`
- [ ] Define `QuestionType` dataclass:
  - `type`: "factual" | "creative" | "unknown"
  - `category`: str (name, email, motivation, achievement, etc.)
  - `strategy`: "extract" | "generate"
  - `data_path`: Optional[str] (path in user_profile.json)
  - `confidence`: float (0.0-1.0)

### Task 2: Define Factual Patterns
- [ ] Create pattern dictionary for factual fields:
  - Name: `r"(first|last|full)\s*name"`
  - Email: `r"e-?mail"`
  - Phone: `r"(phone|mobile|telephone)"`
  - Address: `r"(address|street|city|state|zip)"`
  - Date: `r"(start|end|graduation|completion)\s*date"`
  - GPA: `r"gpa|grade\s*point"`
  - Company: `r"(company|employer|organization)"`

### Task 3: Define Creative Patterns
- [ ] Create pattern dictionary for creative fields:
  - Motivation: `r"why.*interested|why.*apply|why.*us"`
  - Achievement: `r"achievement|accomplishment|proud"`
  - Strength: `r"strength|what.*good.*at"`
  - Challenge: `r"challenge|difficult|overcome"`
  - Goal: `r"goal|aspiration|future"`

### Task 4: Implement FormQuestionAnalyzer
- [ ] Create class `FormQuestionAnalyzer`
- [ ] Method: `analyze_question(field_label, field_type, context) -> QuestionType`
- [ ] Match against factual patterns first (higher priority)
- [ ] If no match, check creative patterns
- [ ] If no match, return unknown (default to generate)
- [ ] Calculate confidence based on match quality

### Task 5: Implement Extraction Strategy
- [ ] In `ResponseGenerator`, add `extract_answer(question_type, user_data) -> str`
- [ ] Use `data_path` to navigate user_data JSON
- [ ] Return value directly (no AI call)
- [ ] Handle missing data gracefully (return empty string or placeholder)

### Task 6: Implement Generation Strategy
- [ ] Add `generate_answer(question, question_type, user_data, job_context) -> str`
- [ ] Call AI provider with prompt + context
- [ ] Use question category to select appropriate prompt template
- [ ] Return AI-generated text

### Task 7: Integrate with ResponseGenerator
- [ ] In `generate_response()` workflow:
  1. Analyze question type
  2. If factual → extract
  3. If creative → generate
  4. Cache result (both extraction and generation)

### Task 8: Write Unit Tests
- [ ] Test: Factual patterns match correctly
- [ ] Test: Creative patterns match correctly
- [ ] Test: Unknown defaults to generate
- [ ] Test: Confidence scores calibrated
- [ ] Test: Extraction retrieves correct data
- [ ] Test: Generation calls AI provider
- [ ] Test: Missing data handled gracefully

### Task 9: Integration Testing
- [ ] Test with real form fields (LinkedIn, Greenhouse)
- [ ] Measure cost savings (factual extractions vs AI calls)
- [ ] Validate response quality (extractions accurate, generations contextual)

## Technical Notes

### FormQuestionAnalyzer Implementation
```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class QuestionType:
    type: str  # "factual", "creative", "unknown"
    category: str
    strategy: str  # "extract", "generate"
    data_path: Optional[str] = None
    confidence: float = 0.0

class FormQuestionAnalyzer:
    FACTUAL_PATTERNS = {
        "name": {
            "patterns": [r"(first|last|full)\s*name", r"^name$"],
            "data_path": "personal_info.name",
            "confidence": 0.98
        },
        "email": {
            "patterns": [r"e-?mail", r"email.*address"],
            "data_path": "personal_info.email",
            "confidence": 0.98
        },
        "phone": {
            "patterns": [r"phone|mobile|telephone|contact.*number"],
            "data_path": "personal_info.phone",
            "confidence": 0.95
        },
        # ... more patterns
    }
    
    CREATIVE_PATTERNS = {
        "motivation": {
            "patterns": [r"why.*interested", r"why.*apply", r"why.*us", r"why.*company"],
            "confidence": 0.9
        },
        "achievement": {
            "patterns": [r"achievement|accomplishment|proud", r"biggest.*success"],
            "confidence": 0.85
        },
        # ... more patterns
    }
    
    def analyze_question(self, field_label: str, field_type: str = "text", context: dict = None) -> QuestionType:
        field_lower = field_label.lower()
        
        # Check factual patterns first
        for category, info in self.FACTUAL_PATTERNS.items():
            for pattern in info["patterns"]:
                if re.search(pattern, field_lower):
                    return QuestionType(
                        type="factual",
                        category=category,
                        strategy="extract",
                        data_path=info["data_path"],
                        confidence=info["confidence"]
                    )
        
        # Check creative patterns
        for category, info in self.CREATIVE_PATTERNS.items():
            for pattern in info["patterns"]:
                if re.search(pattern, field_lower):
                    return QuestionType(
                        type="creative",
                        category=category,
                        strategy="generate",
                        data_path=None,
                        confidence=info["confidence"]
                    )
        
        # Default to creative generation (safer than wrong extraction)
        return QuestionType(
            type="unknown",
            category="general",
            strategy="generate",
            confidence=0.5
        )
```

### ResponseGenerator Integration
```python
class ResponseGenerator:
    def __init__(self, provider_factory, analyzer):
        self.provider_factory = provider_factory
        self.analyzer = analyzer
    
    async def generate_response(self, field, user_data, job_context):
        # Analyze question type
        question_type = self.analyzer.analyze_question(
            field["label"],
            field.get("type", "text")
        )
        
        # Extract or generate
        if question_type.strategy == "extract":
            answer = self.extract_answer(question_type, user_data)
        else:
            provider = self.provider_factory.create("openai")
            answer = await self.generate_answer(
                field["label"],
                question_type,
                user_data,
                job_context,
                provider
            )
        
        return answer
    
    def extract_answer(self, question_type, user_data):
        # Navigate data_path: "personal_info.email" → user_data.personal_info.email
        keys = question_type.data_path.split(".")
        value = user_data
        for key in keys:
            value = getattr(value, key, None) if hasattr(value, key) else value.get(key)
            if value is None:
                return ""
        return str(value)
```

### Performance Impact
- **Without classification:** 100 fields = 100 AI calls = $3-5, ~200s
- **With classification:** 100 fields = 30 extractions (free) + 70 AI calls = $2-3.5, ~140s
- **Savings:** ~30-40% cost reduction, ~30% faster

## Definition of Done

- [x] FormQuestionAnalyzer class created
- [x] Factual and creative pattern dictionaries defined
- [x] analyze_question() method implemented
- [x] Extraction strategy in ResponseGenerator
- [x] Generation strategy in ResponseGenerator
- [x] Unit tests >85% coverage
- [x] Integration tests validate cost savings
- [x] Code review completed

## Traceability

**PRD:** FR32 (analyze form questions), FR34 (extract factual info), FR35 (generate creative responses)  
**Dependencies:** Story 3.5 (Provider Factory), Story 2.1 (Data Schema)  
**Blocks:** Story 3.7, 3.8

---

**Notes:**
- Rule-based classification (no ML for MVP)
- ~30-40% cost savings from factual extraction
- Future: ML classifier for better accuracy
