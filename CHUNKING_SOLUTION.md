# 🔧 Context Window Chunking Solution

## Problem Statement

**NOTE: This chunking feature is currently DISABLED as GPT-4.1 has a 1M token context window.**

Originally, when processing 20+ markdown documents (a full month of news), the system was hitting OpenAI's GPT-4o context window limit of 128,000 tokens. Large merged stories with extensive content were causing errors:

```
⚠️ Error generating headline: Error code: 400 - {'error': {'message': "This model's maximum context length is 128000 tokens. However, your messages resulted in 231315 tokens..."}}
```

## Root Cause

1. **NewsMerger.py** combines all related articles across multiple days into single "super-cells"
2. **NewsSummariser.py** passes entire merged stories to GPT-4.1 for headline and summary generation
3. For 20+ days of related news, these merged stories can exceed 230,000+ tokens
4. OpenAI API rejects requests exceeding the 128k token context window

## Solution Architecture

### Smart Chunking System

The solution implements an intelligent chunking mechanism that:
- **Detects** when content will exceed token limits (before API calls)
- **Splits** large stories at natural boundaries (article/paragraph breaks)
- **Processes** each chunk independently with GPT-4.1
- **Recombines** chunk summaries into coherent final output
- **Preserves** chronological order and narrative flow

### Key Components

#### 1. Token Estimation
```python
def estimate_tokens(text):
    """Rough estimation: 1 token ≈ 4 characters"""
    return len(str(text)) // TOKEN_ESTIMATE_RATIO
```

Conservative estimation to prevent context overflow.

#### 2. Intelligent Chunking
```python
def chunk_merged_story(full_story, max_tokens=SAFE_CHUNK_TOKENS):
    """Split story by article boundaries, maintaining coherence"""
```

Features:
- Splits at article boundaries (date markers like "(3 February)")
- Falls back to paragraph splitting for very large articles
- Preserves complete articles within chunks when possible
- Maintains chronological order

#### 3. Chunk Processing
```python
def generate_summary_for_chunk(headlines, chunk_content, dates, chunk_index, total_chunks):
    """Generate summary for individual chunk with context awareness"""
```

Each chunk is summarized with awareness of its position in the larger story.

#### 4. Summary Recombination
```python
def combine_chunk_summaries(headlines, chunk_summaries, dates):
    """Combine multiple chunk summaries into coherent final summary"""
```

Uses GPT-4.1 to merge chunk summaries into a flowing narrative without explicit "part" references.

## Implementation Details

### Token Limits

```python
MAX_CONTEXT_TOKENS = 1000000  # GPT-4.1 context window (1M tokens)
SAFE_CHUNK_TOKENS = 900000    # Safe chunk size with buffer
                              # NOTE: Chunking effectively disabled for GPT-4.1
TOKEN_ESTIMATE_RATIO = 4      # 1 token ≈ 4 characters
```

- **GPT-4.1 Update**: Context window increased from 128k to 1M tokens
- Chunking now effectively disabled (threshold set to 900k tokens)
- Chunking code remains in place for future use or model fallback
- To re-enable chunking: Set `SAFE_CHUNK_TOKENS = 80000`

### Processing Flow

```
1. Estimate total tokens (story + headlines + prompt)
2. If < 80k tokens → Process normally (fast path)
3. If > 80k tokens:
   a. Split story into chunks at article boundaries
   b. Process each chunk: Generate individual summary
   c. Combine chunk summaries: Create unified narrative
   d. Return final combined summary
```

### Headline Generation

For large stories:
1. Create condensed version (first 500 chars of each chunk)
2. Generate headline from condensed overview
3. Fallback: Use first original headline if generation fails

## Files Updated

### Core Implementation
- ✅ `NewsSummariser.py` - Sweden processing (default)
- ✅ `FinlandNewsSummariserThirdPass.py` - Finland processing
- ✅ `PolandNewsSummariserThirdPass.py` - Poland processing

### Changes Applied

1. **Added imports**: `import re` for regex pattern matching
2. **Added constants**: Token limits and estimation ratios
3. **New functions**:
   - `estimate_tokens()` - Token counting
   - `chunk_merged_story()` - Smart chunking
   - `generate_summary_for_chunk()` - Chunk processing
   - `combine_chunk_summaries()` - Summary recombination
4. **Updated functions**:
   - `generate_summary()` - Now chunk-aware
   - `generate_headline()` - Handles large stories

## Benefits

### ✅ Prevents Context Overflow
- No more 400 errors from OpenAI API
- Handles stories of ANY size (20+ days, 30+ days, etc.)

### ✅ Maintains Quality
- Summaries remain coherent and well-structured
- No loss of information from truncation
- Natural narrative flow preserved

### ✅ Performance Optimized
- Fast path for normal stories (< 80k tokens)
- Only chunks when necessary
- Parallel-friendly design

### ✅ Transparent Operation
- Console output shows chunking in progress:
  ```
  📊 Large story detected (~231,315 tokens). Chunking for processing...
  ✂️  Split into 3 chunks
  🔄 Processing chunk 1/3...
  🔄 Processing chunk 2/3...
  🔄 Processing chunk 3/3...
  🔗 Combining 3 chunk summaries...
  ```

## Testing Recommendations

### Test Case 1: Small Story (< 80k tokens)
- Should process normally without chunking
- Single API call for headline and summary

### Test Case 2: Large Story (> 80k tokens)
- Should trigger chunking mechanism
- Multiple API calls with progress indicators
- Final output should be coherent

### Test Case 3: Very Large Story (> 200k tokens)
- Should split into 3+ chunks
- All chunks process successfully
- Combined summary captures full narrative

### Test Case 4: Multi-Country Processing
- Test Sweden, Finland, and Poland variants
- Verify all three implementations work identically

## Future Enhancements

### Potential Optimizations
1. **Parallel chunk processing** - Process chunks concurrently for speed
2. **Adaptive chunk sizing** - Adjust chunk size based on date span
3. **Token caching** - Cache intermediate summaries for repeated processing
4. **Smart boundary detection** - Enhanced article boundary recognition

### Monitoring
- Track chunk statistics (how often chunking is triggered)
- Monitor combined summary quality
- Measure performance impact of chunking

## Rollback Plan

If issues arise, the chunking logic can be disabled by:

```python
# In generate_summary(), change:
if total_estimated_tokens < SAFE_CHUNK_TOKENS:
# To:
if total_estimated_tokens < MAX_CONTEXT_TOKENS:  # Use full 128k limit
```

This reduces chunking frequency while maintaining safety net.

## Current Status (GPT-4.1 Update)

**Chunking is currently DISABLED** due to GPT-4.1's 1M token context window, which is more than sufficient for processing even 30+ days of news content. The chunking logic remains in the codebase as a safety feature and can be re-enabled if:
- A different model with smaller context is used
- Extremely large datasets exceed 900k tokens
- Cost optimization requires smaller context windows

**To re-enable chunking:** Change `SAFE_CHUNK_TOKENS = 80000` in the three Summariser files.

## Conclusion

This solution provides **robust, scalable handling of large news digests** without sacrificing quality or coherence. The system now gracefully handles months of continuous news coverage, automatically adapting to content size while maintaining professional output quality.

---

**Implementation Date**: September 30, 2025  
**Status**: ✅ Deployed and Tested  
**Impact**: Eliminates context window errors for large digests  
**Affected Modules**: All three country variants (Sweden, Finland, Poland)
