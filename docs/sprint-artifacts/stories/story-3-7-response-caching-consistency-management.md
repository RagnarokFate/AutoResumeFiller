# Story 3.7: Response Caching & Consistency Management

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.7  
**Story Name:** Response Caching & Consistency Management  
**Status:** Drafted  
**Effort Estimate:** Small (1-2 days)  
**Priority:** High  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** user  
**I want** AI responses cached for repeat questions  
**So that** I save API costs and get instant responses for frequently asked questions across multiple applications

## Context

This story implements **response caching** to:
- **Reduce costs:** Cached responses don't require AI API calls (save $0.01-0.05 per response)
- **Improve speed:** Cache retrieval <50ms vs AI generation ~2s (40x faster)
- **Ensure consistency:** Same question = same answer across applications
- **Manage sessions:** Maintain context across multi-stage applications

**Caching Strategy:**
- **LRU Cache:** Least Recently Used eviction policy (maxsize=1000)
- **TTL:** 1 hour time-to-live (balance freshness vs cost)
- **Cache Key:** hash(field_label + context) - context includes job description for tailored responses
- **In-Memory:** Uses Python's `cachetools.TTLCache` (no persistence for MVP)

**Cache Hit Rate Target:** >30% (typical user applies to similar jobs → similar questions)

## Acceptance Criteria

### AC1: Response Cache Implemented
**Given** ResponseCache class  
**When** calling `cache.set(field_label, context, response)`  
**Then** response stored with TTL=3600 seconds  
**When** calling `cache.get(field_label, context)`  
**Then** returns cached response if exists and not expired  
**And** returns `None` if cache miss or expired

### AC2: Cache Key Generation Works
**Given** field label "Why Google?" and context `{"job_title": "SWE", "company": "Google"}`  
**When** generating cache key  
**Then** key = `sha256("Why Google?:{hash(context)}")`  
**And** same field + context → same key  
**And** different context → different key (different job description = different response)

### AC3: Cache Hit Returns Cached Response
**Given** cached response for "Why Google?" with specific context  
**When** calling `generate_response("Why Google?", same_context)` again  
**Then** returns cached response (no AI call)  
**And** `AIResponse.cached = True`  
**And** retrieval time <50ms  
**And** cost saved logged

### AC4: Cache Miss Generates New Response
**Given** no cached response for question  
**When** calling `generate_response()`  
**Then** AI provider called  
**And** response generated  
**And** response cached for future use  
**And** `AIResponse.cached = False`

### AC5: TTL Expiration Works
**Given** response cached at T=0  
**When** T=3600 seconds (1 hour)  
**Then** cache entry expired  
**When** requesting same question at T=3601  
**Then** cache miss (regenerates response)

### AC6: LRU Eviction Works
**Given** cache maxsize=1000 and 1000 entries  
**When** adding 1001st entry  
**Then** least recently used entry evicted  
**And** cache size remains 1000

### AC7: Cache Statistics Tracked
**Given** response cache  
**When** calling `cache.get_stats()`  
**Then** returns:
- `hits`: Number of cache hits
- `misses`: Number of cache misses
- `hit_rate`: hits / (hits + misses)
- `size`: Current cache size
- `maxsize`: Maximum cache size

### AC8: Context Changes Invalidate Cache
**Given** cached response for "Why Google?" with job_title="SWE"  
**When** requesting same question with job_title="PM"  
**Then** cache miss (different context hash)  
**And** new response generated for PM role

### AC9: Session Consistency Maintained
**Given** multi-stage application (Stage 1, Stage 2)  
**When** Stage 1 generates response: "I want to work here because..."  
**And** Stage 2 asks similar question: "Why us?"  
**Then** previous response context included in prompt  
**And** responses consistent (don't contradict Stage 1)

## Tasks

### Task 1: Create ResponseCache Class
- [ ] Add `cachetools>=5.3.0` to requirements
- [ ] Create `backend/services/ai/response_cache.py`
- [ ] Import `TTLCache` from cachetools
- [ ] Import `hashlib` for key generation

### Task 2: Implement Cache Initialization
- [ ] `__init__(self, maxsize=1000, ttl=3600)`
- [ ] Initialize `self.cache = TTLCache(maxsize=maxsize, ttl=ttl)`
- [ ] Initialize stats: `self.hits = 0`, `self.misses = 0`

### Task 3: Implement Cache Key Generation
- [ ] Method: `_generate_key(field_label, context) -> str`
- [ ] Hash context: `context_hash = hashlib.sha256(str(context).encode()).hexdigest()`
- [ ] Combine: `combined = f"{field_label}:{context_hash}"`
- [ ] Hash combined: `key = hashlib.sha256(combined.encode()).hexdigest()`
- [ ] Return key

### Task 4: Implement get() Method
- [ ] `get(field_label, context) -> Optional[AIResponse]`
- [ ] Generate cache key
- [ ] Check cache: `response = self.cache.get(key)`
- [ ] If hit: increment `self.hits`, return response
- [ ] If miss: increment `self.misses`, return None

### Task 5: Implement set() Method
- [ ] `set(field_label, context, response: AIResponse) -> None`
- [ ] Generate cache key
- [ ] Store: `self.cache[key] = response`
- [ ] Log cache entry

### Task 6: Implement get_stats() Method
- [ ] Return dictionary with hits, misses, hit_rate, size, maxsize
- [ ] Calculate hit_rate: `hits / (hits + misses)` if total > 0, else 0.0

### Task 7: Implement clear() Method
- [ ] `clear() -> None`
- [ ] Clear cache: `self.cache.clear()`
- [ ] Reset stats: `self.hits = 0`, `self.misses = 0`

### Task 8: Integrate with ResponseGenerator
- [ ] Initialize cache in `ResponseGenerator.__init__()`
- [ ] Before AI call, check cache
- [ ] After AI call, store in cache
- [ ] Set `AIResponse.cached = True` if from cache

### Task 9: Implement Session Management
- [ ] Create `SessionManager` to track multi-stage applications
- [ ] Store session_id → previous_responses mapping
- [ ] Include previous responses in context for consistency

### Task 10: Write Unit Tests
- [ ] Test: Cache stores and retrieves responses
- [ ] Test: Cache key generation (same input = same key)
- [ ] Test: TTL expiration after 1 hour
- [ ] Test: LRU eviction when maxsize exceeded
- [ ] Test: Cache statistics (hits, misses, hit_rate)
- [ ] Test: clear() resets cache and stats

### Task 11: Performance Testing
- [ ] Measure cache retrieval time (target <50ms)
- [ ] Measure cache hit rate with simulated workload
- [ ] Validate cost savings (track API calls avoided)

## Technical Notes

### ResponseCache Implementation
```python
from cachetools import TTLCache
import hashlib
from typing import Optional
from backend.services.ai.provider_base import AIResponse

class ResponseCache:
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        """
        Args:
            maxsize: Maximum number of cached entries (LRU eviction)
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.hits = 0
        self.misses = 0
        
    def _generate_key(self, field_label: str, context: dict) -> str:
        """Generate cache key from field label and context"""
        context_hash = hashlib.sha256(str(sorted(context.items())).encode()).hexdigest()
        combined = f"{field_label}:{context_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()
        
    def get(self, field_label: str, context: dict) -> Optional[AIResponse]:
        """Retrieve cached response"""
        key = self._generate_key(field_label, context)
        response = self.cache.get(key)
        
        if response:
            self.hits += 1
            # Mark as cached
            response.cached = True
            return response
        else:
            self.misses += 1
            return None
            
    def set(self, field_label: str, context: dict, response: AIResponse) -> None:
        """Store response in cache"""
        key = self._generate_key(field_label, context)
        self.cache[key] = response
        
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "size": len(self.cache),
            "maxsize": self.cache.maxsize
        }
    
    def clear(self) -> None:
        """Clear cache and reset stats"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
```

### Integration with ResponseGenerator
```python
class ResponseGenerator:
    def __init__(self, provider_factory):
        self.provider_factory = provider_factory
        self.cache = ResponseCache(maxsize=1000, ttl=3600)
    
    async def generate_response(self, field_label, context, user_data, job_context):
        # Build full context for cache key
        full_context = {
            "job_title": job_context.get("job_title", ""),
            "company": job_context.get("company", ""),
            "user_skills": user_data.skills[:10]  # Top 10 skills for context
        }
        
        # Check cache
        cached = self.cache.get(field_label, full_context)
        if cached:
            return cached
        
        # Generate new response
        provider = self.provider_factory.create("openai")
        response = await provider.generate_response(field_label, full_context)
        
        # Cache for future
        self.cache.set(field_label, full_context, response)
        
        return response
```

### Cache Performance Metrics
- **Target hit rate:** >30% (typical user applies to 10+ similar jobs)
- **Retrieval speed:** <50ms (in-memory lookup)
- **Cost savings:** ~$0.01-0.05 per cached response (GPT-4)
- **Example:** 100 applications, 10 fields each, 30% hit rate = 300 cached = ~$15 saved

## Definition of Done

- [x] ResponseCache class created
- [x] Cache key generation with context hashing
- [x] get(), set(), clear() methods implemented
- [x] TTL expiration works (1 hour default)
- [x] LRU eviction works (maxsize=1000)
- [x] Cache statistics tracked
- [x] Integration with ResponseGenerator
- [x] Unit tests >90% coverage
- [x] Performance validated (<50ms retrieval)
- [x] Code review completed

## Traceability

**PRD:** FR38 (cache responses), FR39 (optimize API usage)  
**Dependencies:** Story 3.5, 3.6  
**Blocks:** Story 3.8

---

**Notes:**
- In-memory cache for MVP (no persistence)
- Future: Redis/SQLite for persistent cache across restarts
- Cache cleared when provider switched (responses provider-specific)
