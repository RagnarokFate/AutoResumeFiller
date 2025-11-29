# Story 2.7: Conversational Data Update - Chatbot Backend

**Story ID:** 2.7  
**Epic:** Epic 2 - Local Data Management System  
**Status:** Drafted  
**Created:** 2025-11-29  
**Sprint:** Epic 2 Sprint 3  
**Estimated Effort:** Large (4-5 days)  
**Priority:** Medium  

---

## User Story

**As a** user  
**I want** to update my profile data through natural language conversation  
**So that** I can quickly add information without navigating complex forms

---

## Context

This story implements the chatbot backend for conversational data updates. Users can send messages like "I learned React last month" or "I started a new job at Google as Senior Engineer in January 2025", and the chatbot suggests structured data updates with AI-assisted categorization. Updates require user approval before modifying the profile.

**Current State:**
- Data schemas and storage exist (Stories 2.1, 2.2)
- No natural language interface
- All updates require manual form entry

**Desired State:**
- Chatbot processes natural language messages
- AI suggests data updates with categorization
- User approves/rejects suggestions
- Updates validated and saved to profile
- Completeness validation ensures required fields present

**Note:** This story can be deferred if Epic 3 (AI integration) is prioritized first, as it depends on AI provider functionality.

---

## Dependencies

**Prerequisites:**
- Story 2.1: Data Schema Definition ✅ (Required - validates updates)
- Story 2.2: File System Data Manager ✅ (Required - saves updates)
- **Story 3.2: OpenAI Provider** (Preferred - uses AI for intent detection)

**Optional Dependencies:**
- Epic 6: GUI Chatbot Tab (provides UI for chatbot)

---

## Acceptance Criteria

### AC1: Process Simple Skill Update
**Given** user message: "I learned React last month"  
**When** calling `ChatbotService.process_message(message, user_profile)`  
**Then** bot suggests:
```python
{
  "intent": "add_skill",
  "suggested_update": {
    "section": "skills",
    "action": "append",
    "value": "React"
  },
  "confidence": 0.90,
  "requires_approval": True,
  "bot_response": "I'll add React to your skills. Is this correct?"
}
```

**And** response generated in <2 seconds

### AC2: Process Work Experience Update
**Given** user message: "I started a new job at Google as Senior Engineer in January 2025"  
**When** processing message  
**Then** bot suggests:
```python
{
  "intent": "add_work_experience",
  "suggested_update": {
    "section": "work_experience",
    "action": "append",
    "value": {
      "company": "Google",
      "position": "Senior Engineer",
      "start_date": "2025-01",
      "end_date": None,  # Current job
      "responsibilities": [],  # Prompts user for details
      "achievements": [],
      "technologies": []
    }
  },
  "confidence": 0.85,
  "missing_fields": ["responsibilities"],
  "requires_approval": True,
  "bot_response": "I'll add your new position at Google. What are your main responsibilities?"
}
```

**And** prompts for missing required fields

### AC3: Approve and Apply Update
**Given** suggested update with user approval  
**When** calling `ChatbotService.approve_update(update_id)`  
**Then** UserProfile updated:
- Validation against Pydantic schema
- UserDataManager.save_user_profile() called
- Auto-backup created
- last_updated timestamp updated

**And** confirmation returned:
```python
{
  "success": True,
  "message": "Skills updated successfully",
  "updated_profile": {...}
}
```

### AC4: Reject Update
**Given** suggested update  
**When** calling `ChatbotService.reject_update(update_id)`  
**Then** update discarded  
**And** no data modification  
**And** confirmation returned

### AC5: Multi-Turn Conversation
**Given** incomplete information in message  
**When** chatbot detects missing fields  
**Then** asks clarifying questions:
```
User: "I worked at Microsoft"
Bot: "Great! What was your position at Microsoft?"
User: "Software Engineer"
Bot: "When did you start and end working there?"
User: "June 2020 to December 2023"
Bot: "I'll add this experience. What were your main responsibilities?"
```

**And** maintains conversation context  
**And** stores partial updates until complete

### AC6: Validate Data Completeness
**Given** user profile  
**When** calling `ChatbotService.validate_completeness(user_profile)`  
**Then** returns completeness score and suggestions:
```python
{
  "completeness": 0.75,  # 75% complete
  "missing_sections": [],
  "incomplete_entries": [
    {
      "section": "work_experience",
      "entry_index": 0,
      "missing_fields": ["responsibilities"],
      "suggestion": "Add responsibilities for your Software Engineer role"
    }
  ],
  "suggestions": [
    "Add a professional summary",
    "Add at least 2 certifications"
  ]
}
```

### AC7: Intent Detection Works
**Given** various user messages  
**When** processing with AI  
**Then** intents detected correctly:
- **add_skill:** "I know Python", "Learned React"
- **add_work_experience:** "Started job at...", "Worked at..."
- **add_education:** "Graduated from...", "Got my degree in..."
- **add_project:** "Built a project...", "Created an app..."
- **add_certification:** "Got certified in...", "Passed AWS exam..."
- **update_personal_info:** "Changed my email", "New phone number"
- **delete_entry:** "Remove that skill", "Delete my last job"
- **unknown:** Ambiguous messages prompt for clarification

**And** confidence scores calculated (0.0-1.0)

### AC8: Error Handling
**Given** invalid or ambiguous messages  
**When** processing  
**Then** errors handled gracefully:
- **Ambiguous:** "Which skill would you like to add?"
- **Invalid data:** "That date format is invalid. Use YYYY-MM."
- **AI failure:** "Sorry, I couldn't process that. Can you rephrase?"
- **Validation error:** "That email format is invalid."

**And** no data corruption

---

## Tasks

### Task 1: Create ChatbotService Module
- Create `backend/services/chatbot/chatbot_service.py`
- Implement ChatbotService class
- Add process_message(), approve_update(), reject_update() methods
- Maintain conversation context (session-based)

### Task 2: Implement Intent Detection
- Use AI provider (OpenAI) for intent classification
- Define intent prompts and examples
- Parse AI responses to extract intent and entities
- Calculate confidence scores
- Handle ambiguous intents

### Task 3: Implement Entity Extraction
- Extract company names, job titles, dates, skills, etc.
- Normalize dates (MM/YYYY, "January 2025" → "2025-01")
- Validate extracted entities
- Handle multiple entities per message

### Task 4: Implement Suggested Updates
- Generate Pydantic-compatible update suggestions
- Identify missing required fields
- Prompt user for clarifications
- Validate suggestions against schemas

### Task 5: Implement Update Approval
- Store pending updates (in-memory or database)
- Apply approved updates to UserProfile
- Validate and save with UserDataManager
- Create auto-backup before save
- Return confirmation

### Task 6: Implement Conversation Context
- Maintain session state (conversation history)
- Support multi-turn conversations
- Store partial updates until complete
- Handle conversation timeouts

### Task 7: Implement Completeness Validation
- Calculate profile completeness score
- Identify missing sections
- Find incomplete entries (missing required fields)
- Generate improvement suggestions

### Task 8: Create API Endpoints
- POST /api/chatbot/message (send message)
- POST /api/chatbot/approve-update (approve)
- POST /api/chatbot/reject-update (reject)
- GET /api/chatbot/completeness (validate)
- Handle sessions (JWT or session cookies)

### Task 9: Create Unit Tests
- Test intent detection with sample messages
- Test entity extraction
- Test update suggestion generation
- Test approval/rejection flows
- Test completeness validation
- Mock AI responses for deterministic testing
- Coverage target: >80%

### Task 10: Create Integration Tests
- Test complete conversation flows
- Test multi-turn conversations
- Test error handling
- Test with real AI provider (optional)

---

## Definition of Done

- [ ] ChatbotService implemented with all methods
- [ ] Intent detection works with AI
- [ ] Entity extraction for all data types
- [ ] Update suggestions generated correctly
- [ ] Approve/reject flows work
- [ ] Multi-turn conversations supported
- [ ] Completeness validation implemented
- [ ] API endpoints created
- [ ] Unit tests >80% coverage
- [ ] Integration tests pass
- [ ] All 8 acceptance criteria validated
- [ ] Documentation updated

---

## Traceability

**PRD:** FR56-FR62 (Conversational data updates)  
**Epic Tech Spec:** AC11 (Chatbot Processes Data Updates)

---

## Notes

- **Deferred Implementation:** This story can be deferred until Epic 3 (AI integration) is complete
- Intent detection requires AI provider (OpenAI recommended)
- Consider using LangChain or similar framework for conversation management
- Session state can be stored in Redis for scalability (future enhancement)
- Multi-turn conversations improve UX but add complexity
- Consider voice input integration (future enhancement)
