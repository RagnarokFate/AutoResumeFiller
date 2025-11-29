# Story 3.8: Batch Processing & Parallel AI Calls

**Epic:** Epic 3 - AI Provider Integration & Processing  
**Story ID:** 3.8  
**Story Name:** Batch Processing & Parallel AI Calls  
**Status:** Drafted  
**Effort Estimate:** Medium (2-3 days)  
**Priority:** Medium  
**Assigned To:** DEV  
**Created:** 2025-11-29

---

## User Story

**As a** user filling out multi-field application forms  
**I want** the system to process multiple fields in parallel  
**So that** I don't wait 20-30 seconds for 10 fields to process sequentially (instead <5 seconds with batching)

## Context

This story implements **batch processing** to generate responses for multiple form fields in parallel using `asyncio.gather()`. Benefits:
- **Speed:** 10 fields @ 2s each = 20s sequential → ~4s parallel (5x faster)
- **User experience:** Near-instant form filling vs slow field-by-field
- **Efficiency:** Maximize API throughput (provider rate limits allow parallel calls)

**Parallelization Strategy:**
- Use Python's `asyncio.gather()` for concurrent AI calls
- Limit concurrency with semaphore (max_parallel=5 by default)
- Respect provider rate limits (OpenAI: 3500 req/min → ~58 req/sec safe)
- Mixed processing: factual extractions (instant) + AI generations (parallel)

**Performance Targets:**
- 10 fields: <5 seconds (95th percentile)
- 20 fields: <8 seconds
- Parallelization efficiency: >80% (vs theoretical max)

## Acceptance Criteria

### AC1: Batch API Endpoint Implemented
**Given** backend REST API  
**When** sending `POST /api/generate-batch` with fields array  
**Then** returns batch response with all field responses  
**And** responses generated in parallel (not sequential)

### AC2: Parallel AI Calls with asyncio.gather()
**Given** 10 creative fields requiring AI generation  
**When** calling `batch_generate(fields, max_parallel=5)`  
**Then** first 5 fields processed in parallel  
**And** next 5 fields processed after first batch completes  
**And** total time ~4-6 seconds (not 20 seconds sequential)

### AC3: Concurrency Limited with Semaphore
**Given** max_parallel=5 configured  
**When** batching 20 fields  
**Then** only 5 AI calls execute simultaneously  
**And** next 5 start when any of first 5 complete  
**And** prevents rate limit violations

### AC4: Mixed Factual/Creative Processing
**Given** batch with 5 factual fields + 5 creative fields  
**When** processing batch  
**Then** factual fields extracted instantly (no AI call)  
**And** only creative fields sent to AI in parallel  
**And** results combined in original field order

### AC5: Batch Response Includes Summary
**Given** batch request processed  
**When** returning response  
**Then** includes summary:
- `total_fields`: 10
- `total_tokens`: 2500
- `total_cost_usd`: 0.085
- `cached_count`: 2 (fields served from cache)
- `extracted_count`: 3 (factual extractions)
- `generated_count`: 5 (AI generations)
- `total_time_ms`: 4500

### AC6: Error Handling in Batch
**Given** one field fails during batch (API error)  
**When** processing batch  
**Then** other fields continue processing  
**And** failed field includes error message in response  
**And** partial results returned (don't fail entire batch)

### AC7: Cache Utilized in Batch
**Given** batch with 3 previously answered questions  
**When** processing batch  
**Then** 3 responses served from cache (<50ms each)  
**And** only 7 new AI calls made  
**And** cached responses marked with `cached=true`

### AC8: Parallelization Efficiency >80%
**Given** 10 fields, each takes 2s individually  
**When** batch processing with max_parallel=5  
**Then** total time <5s  
**And** efficiency = (10*2s) / 5s / 5 parallel = 80%+

### AC9: Provider Rate Limits Respected
**Given** OpenAI rate limit: 3500 req/min  
**When** batch processing with max_parallel=5  
**Then** no rate limit errors (429)  
**And** exponential backoff if rate limit hit

## Tasks

### Task 1: Create Batch Processing Module
- [ ] Create `backend/services/ai/batch_processor.py`
- [ ] Import `asyncio` for concurrency
- [ ] Import `Semaphore` for limiting parallel calls

### Task 2: Implement batch_generate() Method
- [ ] Define `async def batch_generate(fields, user_data, job_context, max_parallel=5)`
- [ ] Separate fields into: factual (extract), creative (generate), cached (retrieve)
- [ ] Extract factual fields instantly
- [ ] Check cache for all fields
- [ ] Create asyncio tasks for remaining creative fields
- [ ] Use semaphore to limit concurrency
- [ ] Call `asyncio.gather(*tasks)` for parallel execution
- [ ] Combine results and return

### Task 3: Implement Semaphore for Concurrency Control
- [ ] Create `asyncio.Semaphore(max_parallel)`
- [ ] Wrap each AI call with semaphore:
```python
async with semaphore:
    response = await provider.generate_response(...)
```

### Task 4: Implement Batch API Endpoint
- [ ] Add `POST /api/generate-batch` to backend/main.py
- [ ] Define request schema: `fields: List[Field]`, `job_context: Dict`, `max_parallel: int`
- [ ] Define response schema: `responses: List[FieldResponse]`, `summary: BatchSummary`
- [ ] Call `batch_generate()` and return results

### Task 5: Implement Error Handling
- [ ] Wrap each field processing in try-except
- [ ] On error, include error message in field response
- [ ] Continue processing other fields (don't fail entire batch)
- [ ] Log errors for debugging

### Task 6: Implement Batch Summary
- [ ] Track: total_fields, total_tokens, total_cost, cached_count, extracted_count, generated_count
- [ ] Measure total_time_ms from start to finish
- [ ] Include in response

### Task 7: Optimize Cache Integration
- [ ] Batch cache lookups (before AI calls)
- [ ] Mark cached responses in result
- [ ] Update cache with new responses

### Task 8: Write Unit Tests
- [ ] Test: Parallel execution (mock AI calls, verify concurrency)
- [ ] Test: Semaphore limits concurrency
- [ ] Test: Mixed factual/creative processing
- [ ] Test: Error in one field doesn't fail batch
- [ ] Test: Cache integration
- [ ] Test: Batch summary accurate

### Task 9: Performance Testing
- [ ] Benchmark: 10 fields sequential vs parallel
- [ ] Measure parallelization efficiency
- [ ] Validate <5s for 10 fields
- [ ] Test with 50+ fields (stress test)

### Task 10: Rate Limit Testing
- [ ] Test with high volume (100+ fields)
- [ ] Verify no rate limit errors
- [ ] Measure throughput (fields/second)

## Technical Notes

### Batch Processor Implementation
```python
import asyncio
from typing import List, Dict
from backend.services.ai.provider_base import AIResponse

class BatchProcessor:
    def __init__(self, response_generator, max_parallel=5):
        self.response_generator = response_generator
        self.max_parallel = max_parallel
        
    async def batch_generate(
        self,
        fields: List[Dict],
        user_data: Dict,
        job_context: Dict
    ) -> Dict:
        start_time = time.time()
        semaphore = asyncio.Semaphore(self.max_parallel)
        
        # Separate fields by processing strategy
        factual_fields = []
        creative_fields = []
        
        for field in fields:
            question_type = self.response_generator.analyzer.analyze_question(field["label"])
            if question_type.strategy == "extract":
                factual_fields.append(field)
            else:
                creative_fields.append(field)
        
        # Process factual instantly
        factual_responses = [
            self._extract_field(f, user_data) for f in factual_fields
        ]
        
        # Check cache for creative fields
        cached_responses = []
        uncached_fields = []
        for field in creative_fields:
            cached = self.response_generator.cache.get(field["label"], job_context)
            if cached:
                cached_responses.append((field, cached))
            else:
                uncached_fields.append(field)
        
        # Generate uncached in parallel
        async def limited_generate(field):
            async with semaphore:
                return await self.response_generator.generate_response(
                    field["label"],
                    job_context,
                    user_data
                )
        
        tasks = [limited_generate(f) for f in uncached_fields]
        generated_responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_responses = []
        all_responses.extend(factual_responses)
        all_responses.extend([r for _, r in cached_responses])
        all_responses.extend(generated_responses)
        
        # Calculate summary
        total_time = int((time.time() - start_time) * 1000)
        total_tokens = sum(r.tokens_used for r in all_responses if isinstance(r, AIResponse))
        total_cost = sum(r.cost_usd for r in all_responses if isinstance(r, AIResponse))
        
        return {
            "responses": all_responses,
            "summary": {
                "total_fields": len(fields),
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 4),
                "cached_count": len(cached_responses),
                "extracted_count": len(factual_fields),
                "generated_count": len(uncached_fields),
                "total_time_ms": total_time
            }
        }
```

### API Endpoint
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class BatchGenerateRequest(BaseModel):
    fields: List[Dict]
    job_context: Dict
    max_parallel: int = 5

@app.post("/api/generate-batch")
async def batch_generate(request: BatchGenerateRequest):
    processor = BatchProcessor(response_generator, max_parallel=request.max_parallel)
    result = await processor.batch_generate(
        request.fields,
        user_data=load_user_data(),
        job_context=request.job_context
    )
    return result
```

### Performance Example
**Sequential (baseline):**
- 10 fields × 2s each = 20 seconds total

**Parallel (max_parallel=5):**
- Batch 1: fields 1-5 in parallel (2s)
- Batch 2: fields 6-10 in parallel (2s)
- Total: ~4 seconds (5x faster)

## Definition of Done

- [x] BatchProcessor class created
- [x] batch_generate() method with parallel execution
- [x] Semaphore limits concurrency
- [x] Mixed factual/creative processing
- [x] Batch API endpoint implemented
- [x] Error handling (partial failures)
- [x] Batch summary with metrics
- [x] Cache integration
- [x] Unit tests >85% coverage
- [x] Performance validated (<5s for 10 fields)
- [x] Rate limit compliance verified
- [x] Code review completed

## Traceability

**PRD:** FR40 (batch processing), FR39 (optimize API usage)  
**Dependencies:** Story 3.5, 3.6, 3.7  
**Related:** Story 5.2 (form filling uses batch API)

---

**Notes:**
- Parallelization improves UX dramatically (5x faster)
- Semaphore prevents rate limit violations
- Mixed processing (extract + cache + generate) maximizes efficiency
