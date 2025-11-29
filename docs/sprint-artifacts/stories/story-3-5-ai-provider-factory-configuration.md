# Story 3.5: AI Provider Factory & Configuration

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.5  
**Story Name:** AI Provider Factory & Configuration  
**Status:** Drafted  
**Effort Estimate:** Small (1-2 days)  
**Priority:** Critical  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** user  
**I want** to select my preferred AI provider and switch between providers seamlessly  
**So that** I can use the provider that best fits my needs without reconfiguring the application

## Context

This story implements the **ProviderFactory** using the Factory design pattern to instantiate AI providers dynamically based on configuration. The factory:
- Reads `config.yaml` for preferred provider
- Loads API keys from OS keyring (secure storage)
- Validates provider configuration
- Returns provider instance ready for use
- Supports runtime provider switching (no restart required)

**Factory Benefits:**
- Centralized provider instantiation
- Configuration-driven provider selection
- Decouples business logic from provider specifics
- Easy to add new providers in future

## Acceptance Criteria

### AC1: ProviderFactory Creates Providers
**Given** config.yaml specifies `preferred_provider: "openai"`  
**When** calling `ProviderFactory.create("openai")`  
**Then** returns `OpenAIProvider` instance  
**And** API key loaded from OS keyring  
**And** model loaded from config  
**When** `preferred_provider: "anthropic"`  
**Then** returns `AnthropicProvider` instance  
**When** `preferred_provider: "google"`  
**Then** returns `GoogleProvider` instance

### AC2: Factory Lists Available Providers
**When** calling `ProviderFactory.get_available_providers()`  
**Then** returns: `["openai", "anthropic", "google"]`  
**And** each provider includes:
- `name`: "openai"
- `display_name`: "OpenAI (GPT)"
- `enabled`: True if API key configured
- `default_model`: "gpt-4"

### AC3: Invalid Provider Raises Error
**Given** config specifies `preferred_provider: "invalid"`  
**When** calling `ProviderFactory.create("invalid")`  
**Then** raises `ValueError` with message "Unknown provider: invalid"

### AC4: Missing API Key Raises Error
**Given** OpenAI selected but no API key in keyring  
**When** calling `ProviderFactory.create("openai")`  
**Then** raises `InvalidAPIKeyError` with message "OpenAI API key not found in keyring"

### AC5: Provider Configuration Loaded
**Given** config.yaml contains:
```yaml
ai_providers:
  openai:
    model: "gpt-3.5-turbo"
    max_tokens: 300
    temperature: 0.8
```
**When** creating OpenAI provider  
**Then** provider initialized with model="gpt-3.5-turbo", temperature=0.8

### AC6: Runtime Provider Switching
**Given** current provider is "openai"  
**When** user changes to "anthropic" via GUI  
**Then** config.yaml updated  
**And** next `ProviderFactory.create()` returns AnthropicProvider  
**And** no application restart required

## Tasks

### Task 1: Create ProviderFactory Module
- [ ] Create `backend/services/ai/provider_factory.py`
- [ ] Import all provider classes (OpenAI, Anthropic, Google)
- [ ] Import keyring manager
- [ ] Import config manager

### Task 2: Implement ProviderFactory.create()
- [ ] Define static method `create(provider_name: str, config: Dict) -> AIProvider`
- [ ] Load API key from keyring: `keyring_manager.retrieve_api_key(provider_name)`
- [ ] Map provider name to class:
  - "openai" → OpenAIProvider
  - "anthropic" → AnthropicProvider
  - "google" → GoogleProvider
- [ ] Extract provider config from config.yaml
- [ ] Instantiate provider with API key, model, config
- [ ] Validate API key before returning
- [ ] Return provider instance

### Task 3: Implement get_available_providers()
- [ ] Define static method returning list of provider metadata
- [ ] Check API key availability in keyring
- [ ] Return list with name, display_name, enabled, default_model

### Task 4: Implement Error Handling
- [ ] Raise `ValueError` for unknown provider
- [ ] Raise `InvalidAPIKeyError` for missing API key
- [ ] Log all factory operations

### Task 5: Integrate with ConfigManager
- [ ] Load `preferred_provider` from config.yaml
- [ ] Load provider-specific config (model, max_tokens, temperature)
- [ ] Support default values if not in config

### Task 6: Integrate with KeyringManager
- [ ] Retrieve API key: `retrieve_api_key(provider_name)`
- [ ] Handle case where keyring not available
- [ ] Redact API key in logs (show last 4 chars only)

### Task 7: Write Unit Tests
- [ ] Test: create() returns correct provider class
- [ ] Test: create() with invalid name raises ValueError
- [ ] Test: create() with missing API key raises error
- [ ] Test: get_available_providers() returns correct list
- [ ] Test: provider configuration loaded correctly
- [ ] Test: runtime provider switching

### Task 8: Integration Testing
- [ ] Test factory with real config.yaml
- [ ] Test provider switching end-to-end
- [ ] Test with all three providers

## Technical Notes

### ProviderFactory Implementation
```python
from backend.services.ai.openai_provider import OpenAIProvider
from backend.services.ai.anthropic_provider import AnthropicProvider
from backend.services.ai.google_provider import GoogleProvider
from backend.services.ai.exceptions import InvalidAPIKeyError
from backend.utils.keyring_manager import KeyringManager
from backend.config.config_manager import ConfigManager

class ProviderFactory:
    PROVIDERS = {
        "openai": {
            "class": OpenAIProvider,
            "display_name": "OpenAI (GPT)",
            "default_model": "gpt-4"
        },
        "anthropic": {
            "class": AnthropicProvider,
            "display_name": "Anthropic (Claude)",
            "default_model": "claude-3-sonnet-20240229"
        },
        "google": {
            "class": GoogleProvider,
            "display_name": "Google (Gemini)",
            "default_model": "gemini-pro"
        }
    }
    
    @staticmethod
    def create(provider_name: str, config_manager: ConfigManager = None) -> AIProvider:
        """Create AI provider instance from name and configuration"""
        if provider_name not in ProviderFactory.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_info = ProviderFactory.PROVIDERS[provider_name]
        
        # Load API key from keyring
        keyring_mgr = KeyringManager()
        api_key = keyring_mgr.retrieve_api_key(provider_name)
        if not api_key:
            raise InvalidAPIKeyError(f"{provider_info['display_name']} API key not found in keyring")
        
        # Load provider config
        if config_manager:
            provider_config = config_manager.get_setting(f"ai_providers.{provider_name}", {})
            model = provider_config.get("model", provider_info["default_model"])
            kwargs = {
                "max_tokens": provider_config.get("max_tokens", 500),
                "temperature": provider_config.get("temperature", 0.7)
            }
        else:
            model = provider_info["default_model"]
            kwargs = {}
        
        # Instantiate provider
        provider_class = provider_info["class"]
        provider = provider_class(api_key=api_key, model=model, **kwargs)
        
        return provider
    
    @staticmethod
    def get_available_providers(keyring_mgr: KeyringManager = None) -> list:
        """List all available providers with status"""
        if not keyring_mgr:
            keyring_mgr = KeyringManager()
        
        providers = []
        for name, info in ProviderFactory.PROVIDERS.items():
            api_key_configured = keyring_mgr.has_api_key(name)
            providers.append({
                "name": name,
                "display_name": info["display_name"],
                "default_model": info["default_model"],
                "enabled": api_key_configured
            })
        
        return providers
```

### Usage Example
```python
# In backend/services/response_generator.py
from backend.services.ai.provider_factory import ProviderFactory
from backend.config.config_manager import ConfigManager

class ResponseGenerator:
    def __init__(self):
        self.config = ConfigManager()
        self.provider = None
    
    def initialize_provider(self):
        preferred = self.config.get_setting("preferred_provider", "openai")
        self.provider = ProviderFactory.create(preferred, self.config)
    
    async def generate_response(self, prompt, context):
        if not self.provider:
            self.initialize_provider()
        
        return await self.provider.generate_response(prompt, context)
```

### Config.yaml Structure
```yaml
preferred_provider: "openai"

ai_providers:
  openai:
    model: "gpt-4"
    max_tokens: 500
    temperature: 0.7
  anthropic:
    model: "claude-3-sonnet-20240229"
    max_tokens: 500
    temperature: 0.7
  google:
    model: "gemini-pro"
    max_tokens: 500
    temperature: 0.7
```

## Definition of Done

- [x] ProviderFactory class created
- [x] create() method implemented
- [x] get_available_providers() implemented
- [x] Integration with ConfigManager
- [x] Integration with KeyringManager
- [x] Error handling (invalid provider, missing API key)
- [x] Unit tests >90% coverage
- [x] Integration tests pass
- [x] Code review completed

## Traceability

**PRD:** FR9 (select preferred provider), FR10 (switch providers)  
**Dependencies:** Story 3.1, 3.2, 3.3, 3.4, Story 2.6 (ConfigManager), Story 2.8 (KeyringManager)  
**Blocks:** Story 3.6, 3.7, 3.8

---

**Notes:**
- Factory pattern simplifies provider management
- Runtime switching requires cache clear (responses provider-specific)
- API keys never logged (only last 4 chars for debugging)
