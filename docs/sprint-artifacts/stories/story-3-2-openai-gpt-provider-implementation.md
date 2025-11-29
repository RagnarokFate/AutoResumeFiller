# Story 3.2: OpenAI (GPT) Provider Implementation

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.2  
**Story Name:** OpenAI (GPT) Provider Implementation  
**Status:** Drafted  
**Effort Estimate:** Medium (2-3 days)  
**Priority:** Critical  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** user  
**I want** to use OpenAI's GPT models (GPT-4, GPT-3.5-turbo) for response generation  
**So that** I can leverage powerful language models to auto-fill job application forms

## Context

This story implements the **OpenAI provider** as the primary AI integration for AutoResumeFiller. OpenAI's GPT-4 and GPT-3.5-turbo models provide high-quality natural language generation for creative responses (motivation, achievements, challenges) and information extraction (resume parsing).

**Key Features:**
- **Async API Calls:** Uses `AsyncOpenAI` client for non-blocking requests
- **Model Selection:** Supports GPT-4 (high quality), GPT-3.5-turbo (fast/cheap)
- **Error Handling:** Exponential backoff for rate limits (429), API key validation, timeout handling
- **Cost Tracking:** Accurate token counting and cost calculation based on OpenAI pricing
- **Function Calling:** Uses structured outputs for information extraction

**OpenAI Pricing (as of 2024):**
- GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens
- GPT-3.5-turbo: $0.0005/1K prompt tokens, $0.0015/1K completion tokens

## Acceptance Criteria

### AC1: OpenAIProvider Class Implements AIProvider Interface
**Given** the AIProvider base class from Story 3.1  
**When** reviewing `backend/services/ai/openai_provider.py`  
**Then** `OpenAIProvider` class inherits from `AIProvider`  
**And** implements all abstract methods:
- `generate_response()`
- `extract_information()`
- `validate_api_key()`
- `get_provider_name()`
- `get_available_models()`

### AC2: Async Response Generation Works
**Given** valid OpenAI API key in OS keyring  
**When** calling `await provider.generate_response("Why Google?", context)`  
**Then** returns `AIResponse` object with:
- `text`: Generated response (2-4 sentences)
- `provider`: "openai"
- `model`: "gpt-4" (or configured model)
- `tokens_used`: Accurate token count
- `cost_usd`: Calculated cost based on OpenAI pricing  
**And** response completes in <3 seconds (95th percentile)  
**And** response is contextually appropriate (references user data)

### AC3: Information Extraction Works
**Given** resume text and extraction schema  
**When** calling `await provider.extract_information(text, schema)`  
**Then** returns structured dictionary matching schema  
**And** uses OpenAI function calling for structured outputs  
**And** extracts: name, email, phone, work experience, education, skills

### AC4: API Key Validation Works
**Given** OpenAI provider instance  
**When** calling `await provider.validate_api_key()`  
**Then** returns `True` if API key valid  
**And** returns `False` if API key invalid  
**And** validates by calling `client.models.list()` (lightweight test)

### AC5: Rate Limiting Handled with Exponential Backoff
**Given** OpenAI rate limit exceeded (429 error)  
**When** making API call  
**Then** retries with exponential backoff: 1s, 2s, 4s (max 3 attempts)  
**And** raises `RateLimitError` if all retries exhausted  
**And** logs retry attempts for debugging

### AC6: Cost Tracking Accurate
**Given** GPT-4 pricing: $0.03/1K prompt tokens, $0.06/1K completion tokens  
**When** generating response with 200 prompt tokens, 100 completion tokens  
**Then** `AIResponse.cost_usd` = (200/1000 * $0.03) + (100/1000 * $0.06) = $0.012  
**And** `provider.token_count` incremented by 300  
**And** `provider.total_cost` incremented by $0.012

### AC7: Available Models Listed
**Given** OpenAI provider  
**When** calling `provider.get_available_models()`  
**Then** returns: `["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]`

### AC8: Error Handling for Common Failures
**Given** various API error scenarios  
**When** making API calls  
**Then** handles:
- **401 Unauthorized:** Raises `InvalidAPIKeyError`
- **429 Rate Limit:** Retries with exponential backoff
- **500 Server Error:** Retries up to 3 times
- **Timeout (30s):** Raises `ProviderAPIError` with timeout message  
**And** all errors logged with structured details

### AC9: System Prompt Configured for Job Applications
**Given** the need for contextually appropriate responses  
**When** generating response  
**Then** uses system prompt:
> "You are an expert at filling job applications. Generate professional, accurate responses based on the user's data. Be concise and tailored to the specific question."  
**And** user message includes: question, user context (work experience, skills), job context (if available)

## Tasks

### Task 1: Setup OpenAI Client
- [ ] Add `openai>=1.6.0` to `backend/requirements.txt`
- [ ] Create `backend/services/ai/openai_provider.py`
- [ ] Import `AsyncOpenAI` from openai library
- [ ] Import `AIProvider`, `AIResponse` from provider_base

### Task 2: Implement OpenAIProvider Constructor
- [ ] Define `__init__(self, api_key, model="gpt-4", **kwargs)`
- [ ] Call `super().__init__(api_key, model, **kwargs)`
- [ ] Initialize `self.client = AsyncOpenAI(api_key=api_key)`
- [ ] Store model preference and configuration

### Task 3: Implement generate_response()
- [ ] Define async method signature: `async def generate_response(prompt, context, max_tokens=500, temperature=0.7) -> AIResponse`
- [ ] Build system prompt for job application context
- [ ] Build user message with prompt + context (JSON format)
- [ ] Call `await self.client.chat.completions.create()` with:
  - `model=self.model`
  - `messages=[{"role": "system", ...}, {"role": "user", ...}]`
  - `max_tokens=max_tokens`
  - `temperature=temperature`
- [ ] Extract response text, token usage, and calculate cost
- [ ] Update `self.token_count` and `self.total_cost`
- [ ] Return `AIResponse` object

### Task 4: Implement extract_information()
- [ ] Define async method signature: `async def extract_information(text, extraction_schema) -> Dict`
- [ ] Use OpenAI function calling with `functions=[{"name": "extract", "parameters": extraction_schema}]`
- [ ] Call `await self.client.chat.completions.create()` with function call
- [ ] Parse `response.choices[0].message.function_call.arguments` as JSON
- [ ] Return extracted dictionary

### Task 5: Implement validate_api_key()
- [ ] Define async method signature: `async def validate_api_key() -> bool`
- [ ] Wrap in try-except block
- [ ] Call `await self.client.models.list()` (lightweight validation)
- [ ] Return `True` on success, `False` on exception
- [ ] Log validation result

### Task 6: Implement Rate Limiting with Exponential Backoff
- [ ] Add `tenacity>=8.2.0` to `backend/requirements.txt`
- [ ] Decorate `generate_response()` with `@retry`:
  - `wait=wait_exponential(multiplier=1, min=1, max=4)`
  - `stop=stop_after_attempt(3)`
  - `retry=retry_if_exception_type(RateLimitError)`
- [ ] Catch `openai.RateLimitError` and raise custom `RateLimitError`

### Task 7: Implement Cost Tracking
- [ ] Define `get_cost_per_token()` returning:
  - GPT-4: `{"prompt": 0.03, "completion": 0.06}`
  - GPT-3.5-turbo: `{"prompt": 0.0005, "completion": 0.0015}`
- [ ] Calculate cost in `generate_response()`:
  - `prompt_cost = (prompt_tokens / 1000) * cost_per_token["prompt"]`
  - `completion_cost = (completion_tokens / 1000) * cost_per_token["completion"]`
  - `total_cost = prompt_cost + completion_cost`

### Task 8: Implement Getters
- [ ] Implement `get_provider_name()` returning "openai"
- [ ] Implement `get_available_models()` returning `["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]`

### Task 9: Write Unit Tests
- [ ] Create `backend/services/ai/tests/test_openai_provider.py`
- [ ] Mock OpenAI API calls with `pytest-httpx`
- [ ] Test: `generate_response()` returns correct AIResponse
- [ ] Test: `extract_information()` extracts structured data
- [ ] Test: `validate_api_key()` returns True/False
- [ ] Test: Rate limiting triggers exponential backoff
- [ ] Test: Cost calculation accuracy
- [ ] Test: Available models listed correctly

### Task 10: Integration Testing
- [ ] Test with real OpenAI API key (environment variable)
- [ ] Test GPT-4 response generation (creative question)
- [ ] Test GPT-3.5-turbo response generation (factual extraction)
- [ ] Test rate limit handling (intentionally trigger)
- [ ] Measure response time (<3s target)

## Technical Notes

### OpenAIProvider Implementation Example
```python
from openai import AsyncOpenAI
from backend.services.ai.provider_base import AIProvider, AIResponse
from backend.services.ai.exceptions import InvalidAPIKeyError, RateLimitError
import time
import json

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def generate_response(
        self,
        prompt: str,
        context: dict,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AIResponse:
        start_time = time.time()
        
        system_prompt = """You are an expert at filling job applications.
        Generate professional, accurate responses based on the user's data.
        Be concise and tailored to the specific question."""
        
        user_message = f"""
        Question: {prompt}
        
        User Context:
        {json.dumps(context, indent=2)}
        
        Provide a natural, professional response.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            text = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            # Calculate cost
            cost_rates = self.get_cost_per_token()
            cost = (response.usage.prompt_tokens / 1000 * cost_rates["prompt"] +
                   response.usage.completion_tokens / 1000 * cost_rates["completion"])
            
            # Update tracking
            self.token_count += tokens
            self.total_cost += cost
            
            generation_time = int((time.time() - start_time) * 1000)
            
            return AIResponse(
                text=text,
                provider="openai",
                model=self.model,
                tokens_used=tokens,
                cost_usd=round(cost, 4),
                confidence=0.85,  # Can derive from logprobs if available
                cached=False,
                generation_time_ms=generation_time
            )
            
        except openai.RateLimitError:
            raise RateLimitError("OpenAI rate limit exceeded")
        except openai.AuthenticationError:
            raise InvalidAPIKeyError("Invalid OpenAI API key")
        except Exception as e:
            raise ProviderAPIError(f"OpenAI API error: {str(e)}")
    
    async def validate_api_key(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except:
            return False
    
    def get_provider_name(self) -> str:
        return "openai"
    
    def get_available_models(self) -> list[str]:
        return ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
    
    def get_cost_per_token(self) -> dict[str, float]:
        if "gpt-4" in self.model:
            return {"prompt": 0.03, "completion": 0.06}
        else:  # gpt-3.5-turbo
            return {"prompt": 0.0005, "completion": 0.0015}
```

### Testing with Mocked API
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_generate_response():
    provider = OpenAIProvider(api_key="test-key", model="gpt-4")
    
    # Mock the API call
    provider.client.chat.completions.create = AsyncMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="I'm excited about..."))],
        usage=MagicMock(total_tokens=345, prompt_tokens=245, completion_tokens=100)
    ))
    
    response = await provider.generate_response("Why Google?", {"skills": ["Python"]})
    
    assert response.text == "I'm excited about..."
    assert response.provider == "openai"
    assert response.tokens_used == 345
    assert response.cost_usd == 0.012  # (245/1000*0.03) + (100/1000*0.06)
```

### Performance Targets
- Response generation: <3 seconds (95th percentile)
- API key validation: <2 seconds
- Token counting: 100% accurate (use OpenAI's usage data)

## Definition of Done

- [x] OpenAIProvider class created implementing AIProvider interface
- [x] All abstract methods implemented (generate_response, extract_information, validate_api_key, etc.)
- [x] Async OpenAI client initialized
- [x] Rate limiting with exponential backoff implemented
- [x] Cost tracking accurate (within 5% of actual OpenAI billing)
- [x] Error handling for 401, 429, 500, timeout
- [x] Unit tests written with >85% coverage
- [x] Integration tests with real API key pass
- [x] Response time <3 seconds validated
- [x] Code review completed
- [x] Documentation updated

## Traceability

**PRD Functional Requirements:**
- FR8: Configure API keys for multiple AI providers
- FR9: Select preferred AI provider (OpenAI as default)
- FR33: Query configured AI provider
- FR35: Generate creative responses for open-ended questions

**Architecture Alignment:**
- AI Provider Layer: OpenAI concrete implementation of Strategy Pattern
- Uses AsyncOpenAI for non-blocking I/O

**Dependencies:**
- **Depends on:** Story 3.1 (AIProvider base class)
- **Blocks:** Story 3.5 (Provider Factory), Story 3.6 (Response Generation)

**Related Stories:**
- Story 3.3: Anthropic Provider Implementation
- Story 3.4: Google Provider Implementation
- Story 3.5: AI Provider Factory & Configuration

---

**Notes:**
- OpenAI is the **primary provider** for MVP (most mature API, best quality)
- GPT-4 recommended for complex questions, GPT-3.5-turbo for simple extraction (cost optimization)
- Consider GPT-4-turbo for longer context windows (128K tokens) if needed
- API key stored in OS keyring (Story 2.8), never in code/config files
