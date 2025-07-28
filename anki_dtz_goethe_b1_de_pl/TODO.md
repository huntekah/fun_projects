# TODO - Known Issues and Improvements

## jotted ideas:

 - ✅ use 5000 deutsch frequency book to order flashcards by frequency (or other method)
 - IMPLEMENTED: frequency_sort.py with German frequency list (50k + full list support)
 

## Current Issues

### 1. Translation Method Improvements
- **Issue**: Some cards fail to translate properly (LLM returns original English instead of Polish)
- **Root Cause**: Structured output occasionally fails, rate limiting (429 errors)
- **Solutions Needed**:
  - Add retry logic with exponential backoff
  - Implement fallback translation methods
  - Better error handling for rate limits
  - Consider batch translation for efficiency

### 2. Media Files (Audio) Issues
- **Issue**: Audio files not consistently preserved in translated decks
- **Current State**: Only first card had audio, only for main word (not example sentences)
- **Root Cause**: Media file extraction/mapping not working correctly
- **Solutions Needed**:
  - Fix media file ID mapping between original and translated cards
  - Ensure all audio references (`base_a`, `s1a`, `s2a`, etc.) are preserved
  - Debug genanki media file handling
  - Test audio playback in Anki after import

### 3. Translation Quality
- **Issue**: Some translations need improvement
- **Examples**: 
  - "speichern" should be "zapisywać" not kept as English
  - Need consistent Polish grammatical forms
- **Solutions Needed**:
  - Improve prompts with more specific Polish language guidelines
  - Add translation validation
  - Consider post-processing translation checks

## Future Enhancements

### 4. Batch Processing
- Implement full deck translation (all 2632 cards)
- Progress tracking and resumable translation
- Cost estimation and monitoring

### 5. Translation Validation
- Add human review interface
- Implement translation quality scoring
- Compare against reference dictionaries

### 6. Configuration Management
- Make LLM model configurable
- Add translation settings (formality level, dialect)
- Environment-based configuration

### 7. Frequency Sorting Improvements (Future)
- **Fallback Strategy 1**: Levenshtein distance matching for unmatched words
  - Find closest word in frequency list using edit distance
  - Risk: Random words might get unusually high/low scores
  - Implementation: Use `python-Levenshtein` library for fast matching
- **Fallback Strategy 2**: SentenceTransformers semantic similarity
  - Use embedding similarity to place unmatched words near semantically similar words
  - More accurate for meaning-based placement
  - Implementation: Use `sentence-transformers` with German model
  - Could use models like `distilbert-base-german-cased` or `paraphrase-multilingual-MiniLM-L12-v2`

## Testing Needs
- Unit tests for core functions
- Integration tests for full pipeline
- Media file preservation tests
- Translation quality benchmarks