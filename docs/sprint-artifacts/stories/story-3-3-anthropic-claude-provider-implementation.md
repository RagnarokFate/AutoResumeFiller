# Story 3.3: Anthropic (Claude) Provider Implementation

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.3  
**Story Name:** Anthropic (Claude) Provider Implementation  
**Status:** Drafted  
**Effort Estimate:** Medium (2-3 days)  
**Priority:** High  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** user  
**I want** to use Anthropic's Claude models as an alternative to OpenAI  
**So that** I have provider choice, redundancy, and can leverage Claude's strengths (long context, safety)

## Context

This story implements the **Anthropic provider** for Claude 3 models (Opus, Sonnet, Haiku). Claude offers:
- **100K context window** (vs GPT-4's 8K/32K)
- **Strong safety features** (constitutional AI)
- **Competitive pricing** (Sonnet: ~$15/million tokens vs GPT-4: $30-60/million)
- **Provider redundancy** (if OpenAI down/rate-limited, fall back to Claude)

**Claude 3 Model Tiers:**
- **Opus:** Most capable, best for complex reasoning ($15/$75 per million tokens)
- **Sonnet:** Balanced performance/cost ($3/$15 per million tokens) - **recommended default**
- **Haiku:** Fastest/cheapest ($0.25/$1.25 per million tokens)

## Acceptance Criteria

### AC1: AnthropicProvider Class Implements AIProvider Interface
**Given** the AIProvider base class from Story 3.1  
**When** reviewing `backend/services/ai/anthropic_provider.py`  
**Then** `AnthropicProvider` class inherits from `AIProvider`  
**And** implements all abstract methods

### AC2: Async Response Generation Works
**Given** valid Anthropic API key  
**When** calling `await provider.generate_response("Biggest achievement?", context)`  
**Then** returns `AIResponse` with:
- `provider`: "anthropic"
- `model`: "claude-3-sonnet-20240229" (or configured)
- Response completes in <3 seconds
- Contextually appropriate response

### AC3: Information Extraction Works
**Given** resume text and extraction schema  
**When** calling `await provider.extract_information(text, schema)`  
**Then** returns structured dictionary using Claude's tool use feature

### AC4: API Key Validation Works
**Given** Anthropic provider  
**When** calling `await provider.validate_api_key()`  
**Then** returns True if valid, False if invalid  
**And** validates with minimal test message

### AC5: Cost Tracking Accurate
**Given** Claude 3 Sonnet pricing: $3/million input, $15/million output  
**When** generating response with 200 input tokens, 100 output tokens  
**Then** `AIResponse.cost_usd` = (200/1M * $3) + (100/1M * $15) = $0.0021

### AC6: Available Models Listed
**Given** Anthropic provider  
**When** calling `provider.get_available_models()`  
**Then** returns: `["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]`

### AC7: Rate Limiting Handled
**Given** Anthropic rate limit exceeded  
**When** making API call  
**Then** retries with exponential backoff (same as OpenAI)

### AC8: Error Handling
**Given** various API errors  
**Then** handles: 401 (auth), 429 (rate limit), 500 (server), timeout

### AC9: System Prompt Configured
**Given** response generation  
**Then** uses system parameter (Claude's native system prompt format, not messages role)

## Tasks

### Task 1: Setup Anthropic Client
- [ ] Add `anthropic>=0.8.0` to `backend/requirements.txt`
- [ ] Create `backend/services/ai/anthropic_provider.py`
- [ ] Import `AsyncAnthropic` from anthropic library

### Task 2: Implement AnthropicProvider Constructor
- [ ] Define `__init__(api_key, model="claude-3-sonnet-20240229", **kwargs)`
- [ ] Initialize `self.client = AsyncAnthropic(api_key=api_key)`

### Task 3: Implement generate_response()
- [ ] Build system prompt for job applications
- [ ] Call `await self.client.messages.create()` with:
  - `model=self.model`
  - `system=system_prompt`
  - `messages=[{"role": "user", "content": prompt_with_context}]`
  - `max_tokens=max_tokens`
  - `temperature=temperature`
- [ ] Extract text from `message.content[0].text`
- [ ] Calculate cost using Claude pricing
- [ ] Return AIResponse

### Task 4: Implement extract_information()
- [ ] Use Claude's tool use feature for structured extraction
- [ ] Define extraction tool with schema
- [ ] Parse tool use response

### Task 5: Implement validate_api_key()
- [ ] Send minimal test message
- [ ] Return True on success, False on exception

### Task 6: Implement Rate Limiting
- [ ] Use tenacity retry decorator (same as OpenAI)
- [ ] Catch `anthropic.RateLimitError`

### Task 7: Implement Cost Tracking
- [ ] Define `get_cost_per_token()` with Claude pricing:
  - Opus: `{"prompt": 15.0, "completion": 75.0}` (per 1M tokens)
  - Sonnet: `{"prompt": 3.0, "completion": 15.0}`
  - Haiku: `{"prompt": 0.25, "completion": 1.25}`
- [ ] Calculate cost with input/output tokens

### Task 8: Implement Getters
- [ ] `get_provider_name()` returns "anthropic"
- [ ] `get_available_models()` returns Claude 3 models list

### Task 9: Write Unit Tests
- [ ] Test generate_response with mocked API
- [ ] Test extract_information
- [ ] Test validate_api_key
- [ ] Test cost calculation
- [ ] Test rate limiting

### Task 10: Integration Testing
- [ ] Test with real Anthropic API key
- [ ] Test Claude 3 Sonnet (default)
- [ ] Test response quality comparison with OpenAI
- [ ] Measure response time

## Technical Notes

### AnthropicProvider Implementation
```python
from anthropic import AsyncAnthropic
from backend.services.ai.provider_base import AIProvider, AIResponse
import time

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)
        
    async def generate_response(self, prompt, context, max_tokens=500, temperature=0.7):
        start_time = time.time()
        
        system_prompt = """You are an expert at filling job applications.
        Generate professional, accurate responses based on the user's data."""
        
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Question: {prompt}\n\nContext: {json.dumps(context)}\n\nResponse:"
            }]
        )
        
        text = message.content[0].text
        tokens = message.usage.input_tokens + message.usage.output_tokens
        
        # Calculate cost (per million tokens)
        cost_rates = self.get_cost_per_token()
        cost = (message.usage.input_tokens / 1_000_000 * cost_rates["prompt"] +
               message.usage.output_tokens / 1_000_000 * cost_rates["completion"])
        
        self.token_count += tokens
        self.total_cost += cost
        
        return AIResponse(
            text=text,
            provider="anthropic",
            model=self.model,
            tokens_used=tokens,
            cost_usd=round(cost, 4),
            confidence=0.85,
            cached=False,
            generation_time_ms=int((time.time() - start_time) * 1000)
        )
        
    async def validate_api_key(self):
        try:
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except:
            return False
            
    def get_provider_name(self):
        return "anthropic"
        
    def get_available_models(self):
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def get_cost_per_token(self):
        if "opus" in self.model:
            return {"prompt": 15.0, "completion": 75.0}
        elif "sonnet" in self.model:
            return {"prompt": 3.0, "completion": 15.0}
        else:  # haiku
            return {"prompt": 0.25, "completion": 1.25}
```

### Claude Advantages
- **100K context:** Can include entire resume + job description + previous responses
- **Safety:** Constitutional AI reduces inappropriate content
- **Pricing:** Sonnet cheaper than GPT-4, similar quality

## Definition of Done

- [x] AnthropicProvider class created
- [x] All abstract methods implemented
- [x] Rate limiting and error handling
- [x] Cost tracking with Claude pricing
- [x] Unit tests >85% coverage
- [x] Integration tests pass
- [x] Response time <3s validated
- [x] Code review completed

## Traceability

**PRD:** FR8-FR10 (multi-provider AI)  
**Dependencies:** Story 3.1 (AIProvider base class)  
**Blocks:** Story 3.5 (Provider Factory)

---

**Notes:**
- Claude 3 Sonnet recommended default (best price/performance)
- 100K context window allows full resume inclusion
- Provider redundancy if OpenAI unavailable
