# Epic Technical Specification: AI Provider Integration & Processing

Date: 2025-11-28
Author: Ragnar
Epic ID: 3
Status: Draft

---

## Overview

Epic 3 implements the AI Provider Integration layer, enabling AutoResumeFiller to generate intelligent, contextually appropriate responses to job application questions using multiple AI providers (OpenAI GPT-4, Anthropic Claude, Google Gemini). The system provides seamless provider switching, prompt engineering with context management, response caching, and batch processing for performance optimization.

The AI layer uses a Strategy Pattern with abstract base class to ensure provider-agnostic implementation. Users can configure their preferred provider via config.yaml, and the system automatically handles API authentication, rate limiting, retries, and error handling. AI-generated responses consider the user's complete profile, job context, and previous responses to maintain consistency across multi-stage applications.

This epic enables 9 functional requirements (FR8-FR12, FR37-FR40) and serves as the intelligence layer for form filling (Epic 5) and conversational data updates (Epic 2.7, Epic 6.5).

## Objectives and Scope

**In Scope:**
- Abstract AIProvider base class with async interface
- OpenAI provider implementation (GPT-4, GPT-3.5-turbo)
- Anthropic provider implementation (Claude 3 models)
- Google provider implementation (Gemini Pro)
- ProviderFactory for runtime provider selection
- Prompt engineering system with template management
- Form question analysis (factual vs creative, field type classification)
- Response caching with LRU eviction policy
- Batch processing for parallel API calls
- Context management (user profile, job description, previous responses)
- API key management via OS keyring integration
- Cost tracking (tokens used, estimated cost per provider)

**Out of Scope:**
- Custom fine-tuned models (use provider defaults)
- Offline AI models (internet required)
- Real-time streaming responses (deferred to Epic 7)
- Multi-modal AI (images, PDFs as input - text only)
- Chatbot conversational UI (Epic 6)

**Success Criteria:**
- Users can switch AI providers without application restart
- Response generation completes in <3 seconds for 95% of requests
- Cached responses retrieved in <50ms
- API key validation works for all three providers
- Cost tracking accurate within 5% of actual provider billing
- Batch processing achieves 80%+ parallelization efficiency

## System Architecture Alignment

Epic 3 implements the **AI Provider Layer** from the architecture:

**Provider Strategy Pattern:**
```
┌─────────────────────────────────────────────┐
│         AIProvider (Abstract Base)          │
│  - generate_response(prompt, context)       │
│  - extract_information(text, schema)        │
│  - validate_api_key()                       │
│  - get_available_models()                   │
└─────────────────────────────────────────────┘
                    ▲
                    │ implements
        ┌───────────┼───────────┐
        │           │           │
┌───────┴────┐ ┌────┴─────┐ ┌──┴────────┐
│  OpenAI    │ │ Anthropic│ │  Google   │
│  Provider  │ │ Provider │ │ Provider  │
└────────────┘ └──────────┘ └───────────┘
```

**Request Flow:**
```
Extension content script detects form field
    ↓
POST /api/generate-response
    {
      "field_type": "text",
      "field_label": "Why do you want this job?",
      "field_name": "motivation",
      "job_context": {...}
    }
    ↓
Backend: ResponseGenerator.analyze_field()
    ↓
Decision: Is it factual extraction?
    │
    ├─YES→ Direct data extraction from user_profile.json
    │      Return: "John Doe" (no AI call)
    │
    └─NO──→ Creative generation needed
            ↓
      Check response cache (field_label hash)
            │
            ├─HIT→ Return cached response (<50ms)
            │
            └─MISS→ ProviderFactory.create(provider_name)
                    ↓
              Load AI Provider (OpenAI/Anthropic/Google)
                    ↓
              Build prompt with context:
                - User's work experience
                - User's skills
                - Job description (if available)
                - Previous responses (for consistency)
                - Field question
                    ↓
              Call provider.generate_response()
                    ↓
              Cache response (TTL: 1 hour)
                    ↓
              Log tokens used, cost
                    ↓
              Return generated text + metadata
```

**Configuration Integration:**
- API keys stored in OS keyring (Windows Credential Manager, macOS Keychain)
- Provider configuration in config.yaml (default model, max_tokens, temperature)
- Settings class (Epic 1) loads AI provider settings

**Error Handling Strategy:**
```
API Call → Retry Logic (exponential backoff, max 3 attempts)
    ↓
    ├─Success→ Return response
    ├─Rate Limit (429)→ Wait + Retry
    ├─Invalid Key (401)→ Return error, prompt user to reconfigure
    ├─Model Not Available (404)→ Fallback to default model
    └─Timeout (504)→ Retry, then return generic error
```

## Detailed Design

### Services and Modules

| Module | Responsibility | Key Interfaces | Owner |
|--------|---------------|----------------|-------|
| **backend/services/ai/provider_base.py** | Abstract base class defining AI provider interface | `AIProvider` (ABC), `generate_response()`, `extract_information()`, `validate_api_key()` | Backend |
| **backend/services/ai/openai_provider.py** | OpenAI GPT implementation | `OpenAIProvider(AIProvider)`, uses `AsyncOpenAI` client | Backend |
| **backend/services/ai/anthropic_provider.py** | Anthropic Claude implementation | `AnthropicProvider(AIProvider)`, uses `AsyncAnthropic` client | Backend |
| **backend/services/ai/google_provider.py** | Google Gemini implementation | `GoogleProvider(AIProvider)`, uses `google.generativeai` async client | Backend |
| **backend/services/ai/provider_factory.py** | Factory pattern for provider instantiation | `ProviderFactory.create(provider_name)`, `get_available_providers()` | Backend |
| **backend/services/ai/prompt_manager.py** | Prompt templates and context building | `build_prompt(field_type, context)`, `PROMPT_TEMPLATES` dict | Backend |
| **backend/services/ai/response_cache.py** | LRU cache for AI responses | `get(key)`, `set(key, value, ttl)`, `clear()` | Backend |
| **backend/services/response_generator.py** | Orchestrates AI calls, caching, batch processing | `generate_response(field)`, `batch_generate(fields)`, `analyze_field_type()` | Backend |
| **backend/utils/keyring_manager.py** | API key storage/retrieval via OS keyring | `store_api_key(provider, key)`, `retrieve_api_key(provider)` | Backend |

### Data Models and Contracts

**AIProvider Interface (backend/services/ai/provider_base.py):**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class AIResponse:
    """Standard response format from all providers"""
    text: str                       # Generated response text
    provider: str                   # "openai", "anthropic", "google"
    model: str                      # Model used (e.g., "gpt-4")
    tokens_used: int                # Total tokens (prompt + completion)
    cost_usd: float                 # Estimated cost in USD
    confidence: float               # 0.0-1.0, based on temperature/logprobs
    cached: bool = False            # True if served from cache
    generation_time_ms: int = 0     # Time to generate (excluding cache)

class AIProvider(ABC):
    """Abstract base class for all AI providers"""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self.token_count = 0            # Track total tokens used
        self.total_cost = 0.0           # Track cumulative cost
        
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AIResponse:
        """Generate text response from prompt and context"""
        pass
        
    @abstractmethod
    async def extract_information(
        self,
        text: str,
        extraction_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract structured data from unstructured text (for resume parsing)"""
        pass
        
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate API key with provider (health check)"""
        pass
        
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider identifier: openai, anthropic, google"""
        pass
        
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of models available for this provider"""
        pass
        
    def get_cost_per_token(self) -> Dict[str, float]:
        """Return cost per 1K tokens for prompt and completion"""
        # Subclasses override with provider-specific pricing
        return {"prompt": 0.0, "completion": 0.0}
```

**Prompt Templates (backend/services/ai/prompt_manager.py):**
```python
PROMPT_TEMPLATES = {
    "motivation": """
You are an expert job application assistant. Generate a professional, genuine response.

CANDIDATE PROFILE:
{user_summary}

JOB POSTING:
{job_description}

QUESTION: {question}

INSTRUCTIONS:
- Write 2-3 sentences maximum
- Highlight 1-2 relevant experiences from the candidate's profile
- Show specific interest in this role/company
- Be authentic and enthusiastic without hyperbole
- Use first-person voice ("I", not "the candidate")

RESPONSE:
""",
    
    "challenge_overcome": """
You are an expert at STAR-method interview responses (Situation, Task, Action, Result).

CANDIDATE'S WORK EXPERIENCE:
{work_experience}

QUESTION: {question}

INSTRUCTIONS:
- Describe one specific challenge from the candidate's experience
- Use STAR format: Situation (1 sentence), Task (what was needed), Action (what they did), Result (measurable outcome)
- Be concrete with numbers/metrics where available
- 3-4 sentences total

RESPONSE:
""",
    
    "technical_skills": """
You are a technical recruiter assessing skills.

CANDIDATE'S SKILLS:
{skills_list}

CANDIDATE'S PROJECTS:
{projects}

QUESTION: {question}

INSTRUCTIONS:
- List specific technologies the candidate has used
- Mention concrete projects demonstrating those skills
- If the question asks for proficiency level, be honest based on project complexity
- Bullet points acceptable if listing multiple skills

RESPONSE:
""",
    
    "work_authorization": """
Direct factual answer based on candidate data.

CANDIDATE PERSONAL INFO:
{personal_info}

QUESTION: {question}

INSTRUCTIONS:
- Answer with factual information only (Yes/No if asked)
- Include relevant details (e.g., "US Citizen" or "Work authorization via H1B valid until 2026")
- One sentence maximum

RESPONSE:
""",
    
    "general": """
You are a professional job application assistant.

FULL CANDIDATE PROFILE:
{full_profile}

JOB CONTEXT (if available):
{job_description}

QUESTION: {question}

INSTRUCTIONS:
- Provide a professional, accurate answer based on the candidate's data
- If the question is unclear, make reasonable assumptions
- Keep response concise (2-4 sentences)
- Use first-person voice

RESPONSE:
"""
}
```

**Response Cache Schema:**
```python
from cachetools import TTLCache
import hashlib

class ResponseCache:
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):  # 1 hour TTL
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        
    def _generate_key(self, field_label: str, context_hash: str) -> str:
        """Generate cache key from field label and context"""
        combined = f"{field_label}:{context_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()
        
    def get(self, field_label: str, context: Dict) -> Optional[AIResponse]:
        context_hash = hashlib.sha256(str(context).encode()).hexdigest()
        key = self._generate_key(field_label, context_hash)
        return self.cache.get(key)
        
    def set(self, field_label: str, context: Dict, response: AIResponse) -> None:
        context_hash = hashlib.sha256(str(context).encode()).hexdigest()
        key = self._generate_key(field_label, context_hash)
        self.cache[key] = response
```

### APIs and Interfaces

**Backend REST API Endpoints:**

**1. Generate Single Response:**
```
POST   /api/generate-response

Request:
{
  "field_type": "text",                      # text, textarea, select, etc.
  "field_label": "Why do you want this job?",
  "field_name": "motivation",
  "field_context": {                         # Optional metadata
    "max_length": 500,
    "required": true,
    "page_title": "Google - Software Engineer Application"
  },
  "job_context": {                           # Optional
    "job_title": "Senior Software Engineer",
    "company": "Google",
    "description": "..."
  },
  "previous_responses": {                    # For consistency
    "company_interest": "I'm drawn to Google's innovative culture..."
  }
}

Response (200 OK):
{
  "success": true,
  "response": "I'm excited about this role because my 5 years of backend development align perfectly with Google's infrastructure challenges...",
  "metadata": {
    "provider": "openai",
    "model": "gpt-4",
    "tokens_used": 345,
    "cost_usd": 0.0124,
    "confidence": 0.85,
    "cached": false,
    "generation_time_ms": 1240
  }
}
```

**2. Batch Generate (Parallel Processing):**
```
POST   /api/generate-batch

Request:
{
  "fields": [
    {"field_label": "Why Google?", "field_type": "textarea", ...},
    {"field_label": "Biggest achievement?", "field_type": "textarea", ...},
    {"field_label": "Technical skills?", "field_type": "text", ...}
  ],
  "job_context": {...},
  "max_parallel": 5                          # Limit concurrent API calls
}

Response (200 OK):
{
  "success": true,
  "responses": [
    {"field_label": "Why Google?", "response": "...", "metadata": {...}},
    {"field_label": "Biggest achievement?", "response": "...", "metadata": {...}},
    ...
  ],
  "summary": {
    "total_fields": 3,
    "total_tokens": 1024,
    "total_cost_usd": 0.037,
    "cached_count": 0,
    "total_time_ms": 2100
  }
}
```

**3. AI Provider Management:**
```
GET    /api/ai-providers                    # List available providers
GET    /api/ai-providers/{name}/models      # List models for provider
POST   /api/ai-providers/validate           # Validate API key
PUT    /api/ai-providers/config             # Update provider configuration

Response (GET /api/ai-providers):
{
  "providers": [
    {
      "name": "openai",
      "display_name": "OpenAI (ChatGPT)",
      "models": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
      "default_model": "gpt-4",
      "enabled": true,
      "api_key_configured": true
    },
    {
      "name": "anthropic",
      "display_name": "Anthropic (Claude)",
      "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
      "default_model": "claude-3-sonnet-20240229",
      "enabled": false,
      "api_key_configured": false
    },
    {
      "name": "google",
      "display_name": "Google (Gemini)",
      "models": ["gemini-pro"],
      "default_model": "gemini-pro",
      "enabled": false,
      "api_key_configured": false
    }
  ],
  "active_provider": "openai"
}

Request (POST /api/ai-providers/validate):
{
  "provider": "openai",
  "api_key": "sk-..."
}

Response (200 OK):
{
  "valid": true,
  "models_available": ["gpt-4", "gpt-3.5-turbo"],
  "account_credits": 15.50,                  # If available from provider
  "rate_limit": {
    "requests_per_minute": 3500,
    "tokens_per_minute": 90000
  }
}
```

**4. Response Cache Management:**
```
GET    /api/cache/stats                     # Cache hit rate, size
DELETE /api/cache/clear                     # Clear all cached responses

Response (GET /api/cache/stats):
{
  "size": 234,
  "maxsize": 1000,
  "hit_rate": 0.42,                          # 42% cache hit rate
  "hits": 156,
  "misses": 214,
  "ttl_seconds": 3600
}
```

**5. Cost Tracking:**
```
GET    /api/ai-usage/stats                  # Token/cost statistics
GET    /api/ai-usage/history                # Usage over time

Response (GET /api/ai-usage/stats):
{
  "total_tokens_used": 125340,
  "total_cost_usd": 4.52,
  "by_provider": {
    "openai": {
      "tokens": 100000,
      "cost_usd": 3.60,
      "requests": 145
    },
    "anthropic": {
      "tokens": 25340,
      "cost_usd": 0.92,
      "requests": 23
    }
  },
  "period": "last_30_days"
}
```

### Workflows and Sequencing

**Single Response Generation Workflow:**
1. Extension content script detects field: "Why do you want this job?"
2. Content script sends `POST /api/generate-response` with field metadata
3. Backend: ResponseGenerator.analyze_field_type()
   - Checks if factual (name, email, phone) → extract from user_profile.json, return immediately
   - Checks if creative (motivation, challenge) → continue to step 4
4. ResponseGenerator checks cache: hash(field_label + context)
   - Cache HIT → return cached response (<50ms)
   - Cache MISS → continue to step 5
5. Load AI provider configuration from config.yaml
6. ProviderFactory.create("openai") → returns OpenAIProvider instance
7. PromptManager.build_prompt("motivation", context)
   - Selects appropriate template
   - Injects user_summary, job_description, question
   - Returns complete prompt string
8. OpenAIProvider.generate_response(prompt, context)
   - Calls AsyncOpenAI.chat.completions.create()
   - Handles rate limiting (exponential backoff if 429)
   - Tracks tokens used, calculates cost
9. Response returned: AIResponse object
10. ResponseCache.set(field_label, context, response) → cache for 1 hour
11. Log to AI usage tracker (tokens, cost, provider, timestamp)
12. Return response to extension: `{"response": "...", "metadata": {...}}`
13. Extension displays in preview panel, awaits user approval

**Batch Generation Workflow (Multi-Field Form):**
1. Extension detects 10 fields on application page
2. Content script sends `POST /api/generate-batch` with all fields
3. Backend: ResponseGenerator.batch_generate(fields, max_parallel=5)
4. Separate fields into:
   - Factual fields (extract from user_profile.json immediately)
   - Creative fields (require AI generation)
5. For creative fields:
   - Check cache for each field (may have some cached from previous application)
   - Identify cache MISS fields (e.g., 6 out of 10)
6. Create asyncio tasks for 6 fields (max_parallel=5 → process in batches of 5)
7. asyncio.gather() runs first 5 in parallel:
   - Field 1: "Why Google?" → OpenAI API call
   - Field 2: "Biggest achievement?" → OpenAI API call
   - Field 3: "Technical skills?" → OpenAI API call
   - Field 4: "Salary expectations?" → OpenAI API call
   - Field 5: "Availability?" → OpenAI API call
8. Wait for batch 1 completion (~2 seconds)
9. Process Field 6 in batch 2
10. Combine all results: factual extractions + cached responses + new generations
11. Update cache with new responses
12. Return complete batch response with summary (total tokens, cost, time)
13. Extension populates all fields in preview panel

**Provider Switching Workflow:**
1. User opens GUI Configuration Tab
2. User changes "Preferred AI Provider" from OpenAI to Anthropic
3. GUI sends `PUT /api/ai-providers/config` with `{"preferred_provider": "anthropic"}`
4. Backend updates config.yaml: `preferred_provider: "anthropic"`
5. Backend clears response cache (responses are provider-specific)
6. Backend validates Anthropic API key from keyring
   - If invalid or missing → return error, prompt user to configure
7. Next API call to `/api/generate-response` uses AnthropicProvider
8. No application restart required

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Single response generation | <3 seconds (95th percentile) | Time from API request to response |
| Cached response retrieval | <50ms | Cache lookup + serialization |
| Batch generation (10 fields, 5 parallel) | <5 seconds | Total time for all responses |
| API key validation | <2 seconds | Provider health check |
| Provider switching | <1 second | Config update + cache clear |

**Rationale:** Users expect near-instant autofill. 3-second response time allows AI generation while maintaining acceptable UX. Caching reduces repeat costs and improves performance.

### Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| API keys stored securely | OS keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service) | Architecture |
| API keys never logged | Redact keys in logs (show last 4 chars only: `sk-...xyz`) | Security best practice |
| API keys never in config.yaml | config.yaml stores provider settings only; keys in keyring | Data architecture |
| HTTPS for API calls | All provider SDKs use HTTPS (OpenAI, Anthropic, Google) | Provider requirement |
| Rate limit handling | Exponential backoff, max 3 retries, respect provider rate limits | Prevent account suspension |

**Threat Model (Epic 3 scope):**
- ✅ **Mitigated:** API key theft from config files (keys in keyring only)
- ✅ **Mitigated:** API key exposure in logs (redacted logging)
- ✅ **Mitigated:** Rate limit violations (exponential backoff)
- ❌ **Out of scope:** Keyring compromise (OS-level threat)
- ❌ **Out of scope:** Man-in-the-middle attacks (provider SDK responsibility)

### Reliability/Availability

| Requirement | Implementation |
|-------------|----------------|
| Provider failover | If primary provider fails (invalid key, outage), fallback to secondary provider (configured in GUI) |
| Retry logic | Exponential backoff: 1s, 2s, 4s (max 3 attempts) |
| Timeout handling | 30-second timeout per API call; return error if exceeded |
| Graceful degradation | If all AI providers fail, return empty response with error message; user can manually fill field |
| Cache persistence | Cache stored in memory (TTLCache); cleared on application restart |

**Availability Target:** 99% successful response generation (measured over 1000 requests, excluding user-caused errors like invalid API keys).

### Cost Management

| Cost Control | Implementation |
|--------------|----------------|
| Cost tracking | Log tokens + cost per request; display cumulative cost in GUI |
| Cost alerts | Warn user if monthly cost exceeds configurable threshold (default: $50 USD) |
| Model selection | Use GPT-3.5-turbo for simple extractions (5x cheaper), GPT-4 for complex reasoning |
| Cache optimization | 1-hour TTL reduces redundant API calls for repeated questions |

**Estimated Costs (per 100 applications):**
- GPT-3.5-turbo: $1.50 (avg 10 fields/app, 150 tokens/field)
- GPT-4: $4.50 (same workload)
- Claude 3 Sonnet: $3.00
- Gemini Pro: $2.00

### Observability

| Component | Logging Strategy | Output |
|-----------|-----------------|--------|
| AI Provider | Log all API calls: provider, model, tokens, cost, latency, errors | Structured JSON logs |
| Response Cache | Log cache hits/misses, eviction events | Performance metrics |
| ProviderFactory | Log provider selection, configuration changes | Debug logs |
| Prompt Manager | Log prompt template selection (NOT full prompt text to avoid PII) | Debug logs |

**Log Example (ai_provider.log):**
```json
{
  "timestamp": "2025-11-28T10:00:00.123Z",
  "level": "INFO",
  "event": "ai_response_generated",
  "provider": "openai",
  "model": "gpt-4",
  "field_type": "textarea",
  "field_label_hash": "a3f5b2...",
  "tokens_prompt": 245,
  "tokens_completion": 100,
  "tokens_total": 345,
  "cost_usd": 0.0124,
  "latency_ms": 1240,
  "cached": false,
  "error": null
}
```

## Dependencies and Integrations

### Python Dependencies (backend/requirements.txt additions)

```
# AI Providers
openai>=1.6.0               # OpenAI GPT-4, GPT-3.5-turbo
anthropic>=0.8.0            # Anthropic Claude 3 models
google-generativeai>=0.3.0  # Google Gemini Pro

# HTTP Client
httpx>=0.25.0               # Async HTTP client (used by providers)

# Caching
cachetools>=5.3.0           # LRU cache with TTL

# Utilities
tenacity>=8.2.0             # Retry logic with exponential backoff
```

### System Requirements

| Requirement | Notes |
|-------------|-------|
| Internet connection | Required for AI API calls (no offline mode) |
| OS Keyring | Windows: Credential Manager (built-in), macOS: Keychain (built-in), Linux: Secret Service |

### Integration Points

| Epic | Integration | Data Flow |
|------|------------|-----------|
| Epic 1 | Uses Settings for provider configuration | config.yaml → Settings → ProviderFactory |
| Epic 2 | Reads user_profile.json for context | UserDataManager → ResponseGenerator → AI Provider |
| Epic 2.7 | Chatbot uses AI for natural language understanding | ChatbotService → AI Provider (intent detection, entity extraction) |
| Epic 5 | Form filling calls AI for creative responses | Form Filler → `/api/generate-response` → AI Provider |
| Epic 6 | GUI displays cost tracking, provider configuration | GUI Config Tab → `/api/ai-providers` → ProviderFactory |

## Acceptance Criteria (Authoritative)

### AC1: AIProvider Base Class Defined
**Given** the need for multiple AI providers  
**When** reviewing backend/services/ai/provider_base.py  
**Then** AIProvider abstract base class exists with methods:
- `generate_response(prompt, context, max_tokens, temperature) -> AIResponse`
- `extract_information(text, extraction_schema) -> Dict`
- `validate_api_key() -> bool`
- `get_provider_name() -> str`
- `get_available_models() -> List[str]`  
**And** AIResponse dataclass includes: text, provider, model, tokens_used, cost_usd, confidence, cached, generation_time_ms  
**And** all methods use async/await (except getters)

### AC2: OpenAI Provider Implemented
**Given** valid OpenAI API key in OS keyring  
**When** calling `OpenAIProvider.generate_response("Why Google?", context)`  
**Then** response generated using `gpt-4` model (or configured model)  
**And** response completes in <3 seconds  
**And** AIResponse includes accurate token count and cost  
**And** API key validation works: `validate_api_key()` returns True  
**And** available models listed: `["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]`  
**And** handles rate limiting (429) with exponential backoff

### AC3: Anthropic Provider Implemented
**Given** valid Anthropic API key in OS keyring  
**When** calling `AnthropicProvider.generate_response("Biggest achievement?", context)`  
**Then** response generated using `claude-3-sonnet-20240229` (or configured model)  
**And** response completes in <3 seconds  
**And** AIResponse includes token count and cost (Anthropic pricing)  
**And** API key validation works  
**And** available models listed: `["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]`

### AC4: Google Provider Implemented
**Given** valid Google AI API key in OS keyring  
**When** calling `GoogleProvider.generate_response("Technical skills?", context)`  
**Then** response generated using `gemini-pro` model  
**And** response completes in <3 seconds  
**And** AIResponse includes token count and cost  
**And** API key validation works  
**And** available models listed: `["gemini-pro"]`

### AC5: ProviderFactory Works
**Given** config.yaml specifies `preferred_provider: "openai"`  
**When** calling `ProviderFactory.create("openai")`  
**Then** returns OpenAIProvider instance with API key loaded from keyring  
**And** provider configured with model from config.yaml  
**When** calling `ProviderFactory.get_available_providers()`  
**Then** returns list: `["openai", "anthropic", "google"]`  
**When** provider name invalid (e.g., "invalid_provider")  
**Then** raises ValueError with message "Unknown provider: invalid_provider"

### AC6: Prompt Manager Builds Context
**Given** field question "Why do you want this job?"  
**When** calling `PromptManager.build_prompt("motivation", context)`  
**Then** returns complete prompt string using "motivation" template  
**And** prompt includes:
- User's work experience summary
- Job description (if available)
- Field question
- Instructions for response format  
**And** context variables replaced: `{user_summary}`, `{job_description}`, `{question}`  
**When** field type "work_authorization"  
**Then** uses "work_authorization" template (factual, concise)

### AC7: Field Type Analysis Works
**Given** field label "Email Address"  
**When** calling `ResponseGenerator.analyze_field_type(field)`  
**Then** returns `{"type": "factual", "extraction_key": "personal_info.email"}`  
**And** no AI call made (direct extraction from user_profile.json)  
**Given** field label "Why do you want this job?"  
**When** calling `ResponseGenerator.analyze_field_type(field)`  
**Then** returns `{"type": "creative", "template": "motivation"}`  
**And** AI call required

### AC8: Response Caching Works
**Given** field question "Why Google?" with specific context  
**When** calling `generate_response()` first time  
**Then** AI provider called (cache MISS)  
**And** response cached with TTL=3600 seconds  
**When** calling `generate_response()` again with same field + context within 1 hour  
**Then** cached response returned (cache HIT)  
**And** response.cached = True  
**And** retrieval time <50ms  
**When** context changes (different job description)  
**Then** cache MISS (different context hash)

### AC9: Batch Processing Parallelizes
**Given** 10 creative fields requiring AI generation  
**When** calling `ResponseGenerator.batch_generate(fields, max_parallel=5)`  
**Then** first 5 fields processed in parallel (asyncio.gather)  
**And** next 5 fields processed after first batch completes  
**And** total time <5 seconds (not 10x single request time)  
**And** batch response includes summary: total_tokens, total_cost_usd, cached_count

### AC10: Cost Tracking Accurate
**Given** OpenAI provider with GPT-4 ($0.03/1K prompt tokens, $0.06/1K completion tokens)  
**When** generating response with 200 prompt tokens, 100 completion tokens  
**Then** calculated cost = (200/1000 * $0.03) + (100/1000 * $0.06) = $0.012  
**And** AIResponse.cost_usd = 0.012  
**And** cost logged to usage tracker  
**When** calling `/api/ai-usage/stats`  
**Then** cumulative cost accurate within 5% of actual provider billing

### AC11: API Key Management Works
**Given** no API key configured for OpenAI  
**When** calling `OpenAIProvider.validate_api_key()`  
**Then** returns False  
**And** error message: "API key not found in keyring"  
**When** user provides API key via GUI  
**Then** key stored in OS keyring: `keyring.set_password("AutoResumeFiller", "openai_api_key", key)`  
**And** key never written to config.yaml or logs  
**When** calling `OpenAIProvider.generate_response()`  
**Then** key retrieved from keyring automatically

### AC12: Provider Switching Works
**Given** current provider "openai"  
**When** user changes to "anthropic" via `/api/ai-providers/config`  
**Then** config.yaml updated: `preferred_provider: "anthropic"`  
**And** response cache cleared (provider-specific responses)  
**And** next `/api/generate-response` call uses AnthropicProvider  
**And** no application restart required

## Traceability Mapping

| Acceptance Criteria | Spec Section(s) | Component(s) | Test Idea |
|---------------------|----------------|--------------|-----------|
| AC1: Base Class Defined | Data Models → AIProvider Interface | provider_base.py | `test_ai_provider_interface()` |
| AC2: OpenAI Works | Detailed Design → Services | openai_provider.py | `test_openai_generate_response()` |
| AC3: Anthropic Works | Detailed Design → Services | anthropic_provider.py | `test_anthropic_generate_response()` |
| AC4: Google Works | Detailed Design → Services | google_provider.py | `test_google_generate_response()` |
| AC5: Factory Works | Data Models → ProviderFactory | provider_factory.py | `test_provider_factory_create()` |
| AC6: Prompts Build | Data Models → Prompt Templates | prompt_manager.py | `test_build_prompt_motivation()` |
| AC7: Field Analysis | Workflows → Single Response | response_generator.py | `test_analyze_field_type()` |
| AC8: Caching Works | Data Models → Response Cache | response_cache.py | `test_cache_hit_miss()` |
| AC9: Batch Processing | Workflows → Batch Generation | response_generator.py | `test_batch_generate_parallel()` |
| AC10: Cost Tracking | NFR → Cost Management | All providers | `test_cost_calculation_accuracy()` |
| AC11: API Key Mgmt | APIs → AI Provider Management | keyring_manager.py | `test_store_retrieve_api_key()` |
| AC12: Provider Switch | Workflows → Provider Switching | provider_factory.py | `test_switch_provider_at_runtime()` |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **R1: AI provider API changes break integration** | High | Use official provider SDKs (auto-updated); version pin with upper bound; monitor provider changelogs |
| **R2: API costs exceed user budget** | Medium | Implement cost tracking + alerts; default to cheaper models (GPT-3.5-turbo) for simple tasks; cache aggressively |
| **R3: Rate limits hit during batch processing** | Medium | Implement exponential backoff; limit max_parallel (default 5); add user-configurable rate limit buffer |
| **R4: AI responses inappropriate or biased** | High | Use temperature=0.7 (balance creativity/determinism); add profanity filter; log all responses for review; allow manual override |
| **R5: Prompt injection attacks** | Low | Sanitize user input; use structured prompts; validate AI responses against schema |

### Assumptions

| Assumption | Validation | Impact if Wrong |
|------------|-----------|-----------------|
| **A1: Users have internet connection** | Required for AI API calls | Offline mode not supported; document requirement in README |
| **A2: Provider APIs stable (<1% downtime)** | Monitor provider status pages | Implement failover to secondary provider |
| **A3: Response generation <3s acceptable UX** | User testing in Epic 5 | If too slow, add progress indicators or reduce max_tokens |
| **A4: Cache hit rate >30% for repeat applications** | Measure in production | If lower, increase TTL or add persistent cache (Redis/SQLite) |
| **A5: Cost <$5/month for average user (50 apps)** | Track actual costs | If higher, optimize model selection or add cost limits |

### Open Questions

| Question | Owner | Resolution Target |
|----------|-------|------------------|
| **Q1: Should we support custom fine-tuned models?** | Architect | Deferred to Epic 7; requires provider-specific model IDs |
| **Q2: How to handle multi-language resumes?** | PM | MVP supports English only; detect language and warn user if non-English |
| **Q3: Should cache persist across application restarts?** | Architect | No for MVP (in-memory TTLCache); consider Redis/SQLite in Epic 7 if needed |
| **Q4: What if user has no preferred provider configured?** | PM | Default to OpenAI; prompt user to configure API key on first run |
| **Q5: How to handle provider-specific features (e.g., Claude's 100K context)?** | Architect | Use provider-agnostic interface; expose advanced features via provider config |

## Test Strategy Summary

### Test Levels

**Unit Tests (85%+ coverage target):**
- AIProvider base class (abstract methods enforce implementation)
- OpenAI, Anthropic, Google providers: generate_response, extract_information, validate_api_key
- ProviderFactory: create, get_available_providers
- PromptManager: build_prompt (all templates), context variable replacement
- ResponseCache: get, set, TTL expiration, cache eviction
- ResponseGenerator: analyze_field_type, batch_generate, cost tracking

**Integration Tests:**
- Complete response generation workflow (field → analyze → cache check → AI call → cache set → return)
- Batch processing with mixed factual/creative fields
- Provider switching at runtime (config update → provider change)
- API key validation with real provider endpoints (use test API keys)

**End-to-End Tests (Epic 5):**
- Extension requests response → backend calls AI → response returned → field filled

### Testing Frameworks

| Component | Framework | Rationale |
|-----------|-----------|-----------|
| AI Providers | pytest + pytest-asyncio | Async test support |
| API mocking | pytest-httpx | Mock OpenAI/Anthropic/Google API calls |
| Caching | pytest + freezegun | Test TTL expiration by advancing time |
| Cost tracking | pytest | Validate cost calculations against known provider pricing |

### Test Execution

**Local Development:**
```bash
# Run Epic 3 tests with coverage
pytest backend/services/ai/tests/ --cov=backend/services/ai --cov-report=html

# Test specific provider
pytest backend/services/ai/tests/test_openai_provider.py

# Test with real API calls (requires valid API keys in keyring)
pytest backend/services/ai/tests/ --use-real-api
```

**CI/CD (GitHub Actions):**
```yaml
- name: Test AI providers (mocked)
  run: pytest backend/services/ai/tests/ --cov=backend/services/ai --cov-fail-under=85
  env:
    TEST_MODE: mock  # Use httpx mocking, not real API calls
```

### Coverage Goals

| Module | Target Coverage | Rationale |
|--------|----------------|-----------|
| provider_base.py | 90% | Critical interface definition |
| openai_provider.py | 85% | Production provider |
| anthropic_provider.py | 85% | Production provider |
| google_provider.py | 80% | Lower priority (fewer users) |
| provider_factory.py | 90% | Simple logic, high impact |
| prompt_manager.py | 80% | Template-based, partial coverage acceptable |
| response_cache.py | 90% | Performance-critical |
| response_generator.py | 85% | Core orchestration logic |

### Edge Cases and Negative Tests

**AI Providers:**
- ✅ Invalid API key (401) → return error, prompt reconfiguration
- ✅ Rate limit exceeded (429) → exponential backoff, max 3 retries
- ✅ Network timeout (30s) → return error, suggest retry
- ✅ Model not available (404) → fallback to default model
- ✅ Empty response from API → log warning, return generic error

**Prompt Manager:**
- ✅ Missing context variable (e.g., `{job_description}` not provided) → replace with "[Not provided]"
- ✅ User data empty (no work experience) → use generic prompt

**Response Cache:**
- ✅ Cache eviction (LRU, maxsize=1000) → oldest entry removed
- ✅ TTL expiration (after 1 hour) → cache MISS, regenerate

**Batch Processing:**
- ✅ One field fails in batch → return partial results + error for failed field
- ✅ All fields fail → return error summary

---

## Summary

Epic 3 delivers a flexible, provider-agnostic AI integration layer with:
- ✅ Abstract AIProvider interface (OpenAI, Anthropic, Google)
- ✅ Runtime provider switching (no restart required)
- ✅ Prompt engineering with context-aware templates
- ✅ Response caching (LRU, 1-hour TTL)
- ✅ Batch processing with parallelization
- ✅ Cost tracking and budget alerts
- ✅ API key management via OS keyring
- ✅ Comprehensive error handling and retry logic

**Next Epic:** Epic 4 (Form Detection & Field Analysis) uses the AI provider layer for advanced field classification and platform-specific adapters (WorkDay, Greenhouse, Lever).

**Status:** Ready for implementation. All acceptance criteria are testable, dependencies are specified, and integration points are clearly defined.
