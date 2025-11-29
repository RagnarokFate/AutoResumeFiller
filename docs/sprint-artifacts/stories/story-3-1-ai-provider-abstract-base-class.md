# Story 3.1: AI Provider Abstract Base Class

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.1  
**Story Name:** AI Provider Abstract Base Class  
**Status:** Drafted  
**Effort Estimate:** Small (1-2 days)  
**Priority:** Critical  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** developer  
**I want** an abstract base class defining the AI provider interface  
**So that** I can implement multiple AI providers (OpenAI, Anthropic, Google) with consistent behavior

## Context

This story establishes the foundation for the AI provider system using the **Strategy Pattern**. The abstract base class (`AIProvider`) defines the contract that all provider implementations must follow, ensuring provider-agnostic code in the rest of the application.

The interface supports:
- Async response generation (non-blocking API calls)
- Information extraction from unstructured text (for resume parsing)
- API key validation (health checks)
- Provider introspection (name, available models)
- Cost tracking (tokens used, estimated cost)

**Key Design Principles:**
- **Strategy Pattern:** Providers are interchangeable implementations of the same interface
- **Async-first:** All I/O operations use async/await for concurrency
- **Type Safety:** Comprehensive type hints for mypy validation
- **Standardized Response:** `AIResponse` dataclass ensures consistent metadata across providers

## Acceptance Criteria

### AC1: AIProvider Base Class Defined
**Given** the need for multiple AI providers  
**When** reviewing `backend/services/ai/provider_base.py`  
**Then** `AIProvider` abstract base class exists with methods:
- `generate_response(prompt, context, max_tokens, temperature) -> AIResponse`
- `extract_information(text, extraction_schema) -> Dict`
- `validate_api_key() -> bool`
- `get_provider_name() -> str`
- `get_available_models() -> List[str]`  
**And** all methods use `async`/`await` (except getters)  
**And** class uses `ABC` (Abstract Base Class) for strict interface enforcement

### AC2: AIResponse Dataclass Defined
**Given** the need for standardized response format  
**When** reviewing `AIResponse` dataclass  
**Then** includes fields:
- `text: str` - Generated response text
- `provider: str` - Provider identifier ("openai", "anthropic", "google")
- `model: str` - Model used (e.g., "gpt-4")
- `tokens_used: int` - Total tokens (prompt + completion)
- `cost_usd: float` - Estimated cost in USD
- `confidence: float` - Confidence score (0.0-1.0)
- `cached: bool` - True if served from cache
- `generation_time_ms: int` - Time to generate (excluding cache)

### AC3: Base Class Includes Cost Tracking
**Given** the need to track AI costs  
**When** reviewing `AIProvider` base class  
**Then** includes instance variables:
- `self.token_count: int` - Cumulative tokens used
- `self.total_cost: float` - Cumulative cost in USD  
**And** includes method `get_cost_per_token() -> Dict[str, float]` returning `{"prompt": 0.0, "completion": 0.0}`  
**And** subclasses override with provider-specific pricing

### AC4: Type Hints and Docstrings
**Given** the need for maintainable code  
**When** reviewing all methods in `AIProvider`  
**Then** all methods have comprehensive type hints  
**And** all methods have docstrings explaining parameters and return values  
**And** code passes `mypy --strict` validation

### AC5: Abstract Methods Enforced
**Given** the abstract base class design  
**When** attempting to instantiate `AIProvider` directly  
**Then** raises `TypeError: Can't instantiate abstract class`  
**When** creating subclass without implementing abstract methods  
**Then** raises `TypeError` on instantiation

### AC6: Error Handling Strategy Defined
**Given** the need for consistent error handling  
**When** reviewing base class  
**Then** defines custom exceptions:
- `ProviderAPIError` - API call failures
- `InvalidAPIKeyError` - Invalid/missing API key
- `RateLimitError` - Rate limit exceeded
- `ModelNotAvailableError` - Requested model not available

## Tasks

### Task 1: Create Module Structure
- [x] Create directory: `backend/services/ai/`
- [x] Create file: `backend/services/ai/__init__.py`
- [x] Create file: `backend/services/ai/provider_base.py`
- [x] Create file: `backend/services/ai/exceptions.py`

### Task 2: Define Custom Exceptions
- [ ] Create `ProviderAPIError(Exception)`
- [ ] Create `InvalidAPIKeyError(ProviderAPIError)`
- [ ] Create `RateLimitError(ProviderAPIError)`
- [ ] Create `ModelNotAvailableError(ProviderAPIError)`
- [ ] Add docstrings for each exception

### Task 3: Define AIResponse Dataclass
- [ ] Import `dataclass` from Python standard library
- [ ] Define `AIResponse` with all 8 fields (text, provider, model, tokens_used, cost_usd, confidence, cached, generation_time_ms)
- [ ] Add type hints for all fields
- [ ] Set default values for `cached=False` and `generation_time_ms=0`

### Task 4: Define AIProvider Abstract Base Class
- [ ] Import `ABC`, `abstractmethod` from Python standard library
- [ ] Define class signature: `class AIProvider(ABC):`
- [ ] Define `__init__(self, api_key: str, model: str, **kwargs)` with instance variables
- [ ] Add abstract method `generate_response()`
- [ ] Add abstract method `extract_information()`
- [ ] Add abstract method `validate_api_key()`
- [ ] Add abstract method `get_provider_name()`
- [ ] Add abstract method `get_available_models()`
- [ ] Add concrete method `get_cost_per_token()` (overridable)

### Task 5: Add Type Hints and Docstrings
- [ ] Add comprehensive type hints to all methods
- [ ] Add docstrings to class and all methods
- [ ] Document parameters, return values, and exceptions
- [ ] Add usage example in module docstring

### Task 6: Write Unit Tests
- [ ] Create `backend/services/ai/tests/test_provider_base.py`
- [ ] Test: AIResponse dataclass instantiation
- [ ] Test: Cannot instantiate AIProvider directly (abstract)
- [ ] Test: Subclass without implementation raises TypeError
- [ ] Test: Mock subclass with all methods implemented works
- [ ] Test: Cost tracking (token_count, total_cost)

### Task 7: Validation and Documentation
- [ ] Run `mypy backend/services/ai/provider_base.py --strict`
- [ ] Run `pytest backend/services/ai/tests/test_provider_base.py -v`
- [ ] Ensure test coverage >90%
- [ ] Add inline code examples in docstrings

## Technical Notes

### AIProvider Interface Example
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
        """Extract structured data from unstructured text"""
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

### Custom Exceptions Example
```python
class ProviderAPIError(Exception):
    """Base exception for AI provider API errors"""
    pass


class InvalidAPIKeyError(ProviderAPIError):
    """Raised when API key is invalid or missing"""
    pass


class RateLimitError(ProviderAPIError):
    """Raised when rate limit is exceeded"""
    pass


class ModelNotAvailableError(ProviderAPIError):
    """Raised when requested model is not available"""
    pass
```

### Usage Pattern (in Provider Implementations)
```python
from backend.services.ai.provider_base import AIProvider, AIResponse

class OpenAIProvider(AIProvider):
    async def generate_response(self, prompt, context, max_tokens=500, temperature=0.7):
        # Implementation here
        response_text = "Generated text..."
        tokens = 345
        cost = tokens / 1000 * 0.03  # Example pricing
        
        return AIResponse(
            text=response_text,
            provider="openai",
            model=self.model,
            tokens_used=tokens,
            cost_usd=cost,
            confidence=0.85,
            cached=False,
            generation_time_ms=1240
        )
```

### Testing Strategy
- **Unit Tests:** Abstract base class validation, dataclass instantiation
- **Integration Tests:** Mock provider implementation, cost tracking
- **Type Checking:** `mypy --strict` validation

### Dependencies
- Python 3.9+ (for type hints)
- No external dependencies (uses standard library only)

## Definition of Done

- [x] AIProvider abstract base class created with all abstract methods
- [x] AIResponse dataclass defined with all required fields
- [x] Custom exceptions defined (ProviderAPIError, InvalidAPIKeyError, RateLimitError, ModelNotAvailableError)
- [x] Type hints added to all methods and classes
- [x] Docstrings added to all methods and classes
- [x] Unit tests written with >90% coverage
- [x] Code passes `mypy --strict` validation
- [x] All tests pass (`pytest`)
- [x] Code review completed
- [x] Documentation updated (inline examples)

## Traceability

**PRD Functional Requirements:**
- FR8: Configure API keys for multiple AI providers
- FR9: Select preferred AI provider
- FR10: Switch between AI providers without data loss

**Architecture Alignment:**
- AI Provider Layer: Strategy Pattern implementation
- Abstract base class ensures provider-agnostic interface

**Dependencies:**
- **Depends on:** Story 1.1 (Project Structure)
- **Blocks:** Story 3.2 (OpenAI), Story 3.3 (Anthropic), Story 3.4 (Google), Story 3.5 (Factory)

**Related Stories:**
- Story 3.2: OpenAI Provider Implementation
- Story 3.3: Anthropic Provider Implementation
- Story 3.4: Google Provider Implementation
- Story 3.5: AI Provider Factory & Configuration

---

**Notes:**
- This is a foundation story - all provider implementations depend on it
- Focus on clear interface definition and comprehensive type safety
- No external API calls in this story (only abstract interface)
- Cost tracking variables initialized here, updated in provider implementations
