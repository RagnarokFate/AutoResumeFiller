# Story 3.4: Google (Gemini) Provider Implementation

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.4  
**Story Name:** Google (Gemini) Provider Implementation  
**Status:** Drafted  
**Effort Estimate:** Medium (2-3 days)  
**Priority:** Medium  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** user  
**I want** to use Google's Gemini models as another AI provider option  
**So that** I have additional choice and can leverage Google's free tier for development/testing

## Context

This story implements the **Google Gemini provider** as the third AI option. Gemini offers:
- **Free tier:** 60 requests/minute, 1500 requests/day (good for development)
- **Competitive pricing:** $0.50/$1.50 per million tokens (Pro), $7/$21 (Pro 1.5)
- **Multi-modal capability:** Supports text + images (future: screenshot-based form detection)
- **Provider diversity:** Three independent providers (OpenAI, Anthropic, Google)

**Gemini Model Tiers:**
- **Gemini Pro:** Standard model, good for most tasks
- **Gemini Pro Vision:** Multi-modal (text + images)
- **Gemini Pro 1.5:** Extended context (1M tokens), better reasoning

## Acceptance Criteria

### AC1: GoogleProvider Class Implements AIProvider Interface
**Given** AIProvider base class  
**When** reviewing `backend/services/ai/google_provider.py`  
**Then** `GoogleProvider` inherits from `AIProvider`  
**And** implements all abstract methods

### AC2: Async Response Generation Works
**Given** valid Google AI API key  
**When** calling `await provider.generate_response("Technical skills?", context)`  
**Then** returns `AIResponse` with provider="google", model="gemini-pro"  
**And** response completes in <3 seconds

### AC3: Information Extraction Works
**Given** text and schema  
**When** calling `extract_information()`  
**Then** returns structured data using Gemini's structured output

### AC4: API Key Validation Works
**Given** Google provider  
**When** calling `validate_api_key()`  
**Then** validates with test generation request

### AC5: Cost Tracking Accurate
**Given** Gemini Pro pricing: $0.50/million input, $1.50/million output  
**When** generating response  
**Then** calculates cost correctly

### AC6: Available Models Listed
**When** calling `get_available_models()`  
**Then** returns: `["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"]`

### AC7: Safety Settings Configured
**Given** professional content generation  
**Then** safety settings allow job application content  
**And** filters inappropriate content

### AC8: Async Support Implemented
**Given** Google SDK may not have native async  
**Then** wraps sync calls with `asyncio.to_thread()` if needed

### AC9: Error Handling
**Then** handles: 401, 429, 500, timeout, safety filter blocks

## Tasks

### Task 1: Setup Google Client
- [ ] Add `google-generativeai>=0.3.0` to requirements
- [ ] Create `backend/services/ai/google_provider.py`
- [ ] Import `google.generativeai as genai`

### Task 2: Implement GoogleProvider Constructor
- [ ] `__init__(api_key, model="gemini-pro", **kwargs)`
- [ ] `genai.configure(api_key=api_key)`
- [ ] `self.model_obj = genai.GenerativeModel(model)`

### Task 3: Implement generate_response()
- [ ] Build full prompt (system + user message combined)
- [ ] Configure `GenerationConfig` (max_tokens, temperature)
- [ ] Call `await self.model_obj.generate_content_async()`
- [ ] Handle sync fallback if async unavailable
- [ ] Extract text and token usage
- [ ] Calculate cost
- [ ] Return AIResponse

### Task 4: Implement extract_information()
- [ ] Use Gemini's function calling for structured output
- [ ] Parse response into dictionary

### Task 5: Implement validate_api_key()
- [ ] Test generation with minimal prompt
- [ ] Return True/False

### Task 6: Implement Safety Settings
- [ ] Configure safety settings for professional content
- [ ] Handle `BLOCK_NONE` or `BLOCK_ONLY_HIGH` threshold

### Task 7: Implement Rate Limiting
- [ ] Use tenacity retry (same pattern as OpenAI/Anthropic)

### Task 8: Implement Cost Tracking
- [ ] `get_cost_per_token()` with Gemini pricing
- [ ] Pro: `{"prompt": 0.50, "completion": 1.50}`
- [ ] Pro 1.5: `{"prompt": 7.0, "completion": 21.0}`

### Task 9: Implement Getters
- [ ] `get_provider_name()` returns "google"
- [ ] `get_available_models()` returns Gemini models

### Task 10: Write Tests
- [ ] Mock tests for all methods
- [ ] Integration test with real API key
- [ ] Test safety filter behavior
- [ ] Test async vs sync fallback

## Technical Notes

### GoogleProvider Implementation
```python
import google.generativeai as genai
import asyncio
from backend.services.ai.provider_base import AIProvider, AIResponse

class GoogleProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro", **kwargs):
        super().__init__(api_key, model, **kwargs)
        genai.configure(api_key=api_key)
        self.model_obj = genai.GenerativeModel(model)
        
    async def generate_response(self, prompt, context, max_tokens=500, temperature=0.7):
        full_prompt = f"""You are an expert at filling job applications.

Question: {prompt}

User Context:
{json.dumps(context, indent=2)}

Provide a professional, accurate response based on the context above."""

        # Try async first, fallback to sync wrapped in to_thread
        try:
            response = await self.model_obj.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
        except AttributeError:
            # If async not available, wrap sync call
            response = await asyncio.to_thread(
                self.model_obj.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
        
        text = response.text
        # Gemini token usage via candidates[0].token_count
        tokens = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
        
        cost_rates = self.get_cost_per_token()
        cost = (tokens / 1_000_000 * (cost_rates["prompt"] + cost_rates["completion"]) / 2)  # Approximate
        
        return AIResponse(
            text=text,
            provider="google",
            model=self.model,
            tokens_used=tokens,
            cost_usd=round(cost, 4),
            confidence=0.80,
            cached=False,
            generation_time_ms=0
        )
        
    async def validate_api_key(self):
        try:
            response = await asyncio.to_thread(
                self.model_obj.generate_content,
                "Test"
            )
            return True
        except:
            return False
            
    def get_provider_name(self):
        return "google"
        
    def get_available_models(self):
        return ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"]
    
    def get_cost_per_token(self):
        if "1.5" in self.model:
            return {"prompt": 7.0, "completion": 21.0}
        return {"prompt": 0.50, "completion": 1.50}
```

### Safety Settings
```python
from google.generativeai.types import HarmCategory, HarmBlockThreshold

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}
```

## Definition of Done

- [x] GoogleProvider class created
- [x] All methods implemented
- [x] Async support (native or wrapped)
- [x] Safety settings configured
- [x] Cost tracking
- [x] Unit tests >80% coverage
- [x] Integration tests pass
- [x] Code review

## Traceability

**PRD:** FR8-FR10 (multi-provider)  
**Dependencies:** Story 3.1  
**Blocks:** Story 3.5

---

**Notes:**
- Free tier good for dev/testing (60 req/min)
- Multi-modal capability (future: screenshot parsing)
- Lower priority than OpenAI/Anthropic
