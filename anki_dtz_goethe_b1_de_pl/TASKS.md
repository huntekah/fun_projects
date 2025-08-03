# Refactoring Tasks - FAANG Architecture Implementation

.
├── configs/
│   ├── main_pipeline.yaml
│   └── subdeck_pipeline.yaml
├── data/
│   ├── de_50k_frequency.txt
│   └── de_full_frequency.txt
├── src/
│   └── anki_deck_factory/
│       ├── __init__.py
│       ├── builders/
│       │   ├── __init__.py
│       │   ├── anki_builder.py        # Logic for creating .apkg files using genanki
│       │   └── templates.py           # Card templates and CSS definitions
│       ├── cli.py                     # Single command-line entry point (using Typer/Click)
│       ├── config/
│       │   ├── __init__.py
│       │   └── models.py              # Pydantic models for loading YAML configs
│       ├── connectors/
│       │   ├── __init__.py
│       │   ├── llm/
│       │   │   ├── __init__.py
│       │   │   ├── base.py            # Abstract base class for translators
│       │   │   └── gemini.py          # Gemini-specific implementation
│       │   └── tts/
│       │       ├── __init__.py
│       │       ├── base.py            # Abstract base class for TTS generators
│       │       └── google.py          # Google Cloud TTS-specific implementation
│       ├── domain/
│       │   └── models.py              # Core data models (AnkiCard, AnkiDeck)
│       ├── io/
│       │   ├── __init__.py
│       │   ├── apkg_handler.py        # For loading/saving .apkg files
│       │   └── csv_handler.py         # For handling CSV import/export
│       ├── processing/
│       │   ├── __init__.py
│       │   ├── audio.py               # Audio generation step logic
│       │   ├── pipeline.py            # The main pipeline runner
│       │   └── sorting.py             # Frequency sorting step logic
│       └── utils.py                     # Genuinely shared, simple utility functions
├── tests/
│   ├── builders/
│   ├── connectors/
│   ├── domain/
│   ├── io/
│   └── processing/
├── .gitignore
├── example.env
├── Makefile
├── pyproject.toml
└── README.md

## Overview
This document breaks down the FAANG principal architect's refactoring manifesto into deliverable business functionality tasks. Each task delivers working functionality while progressing toward the target architecture.

## Progress Tracking
- 🔵 **Not Started**
- 🟡 **In Progress** 
- 🟢 **Completed**
- 🔴 **Blocked**

---

## TASK 001: Foundation Setup 🟢
**Business Value**: Establish the new project structure without breaking existing functionality

### Sub-tasks:
1. **001.1**: Create new directory structure
   - Create `src/anki_deck_factory/` with all subdirectories
   - Create empty `__init__.py` files
   - Create `configs/`, `tests/` directories
   - **Atomic commits**: Single commit with complete directory structure

2. **001.2**: Validate existing functionality still works
   - Run existing scripts to ensure nothing is broken
   - Document current working state
   - **Atomic commits**: Add validation script + documentation

3. **001.3**: Update pyproject.toml for new structure
   - Configure package as `anki_deck_factory`
   - Update import paths and dependencies
   - **Atomic commits**: pyproject.toml updates

**Critical Questions & Clarifications**:
- How do we handle the transition period? Keep old files alongside new structure?
- Should we create a compatibility layer to avoid breaking existing workflows immediately?
- What happens to existing data files and cache directories?

**Acceptance Criteria**: 
- New directory structure exists
- All existing scripts still function
- Package can be imported as `anki_deck_factory`

---

## TASK 002: Core Domain Migration 🔵
**Business Value**: Establish clean data models foundation for all future development

### Sub-tasks:
1. **002.1**: Create domain models
   - Move `schema.py` content to `src/anki_deck_factory/domain/models.py`
   - Ensure no external dependencies in domain models
   - **Atomic commits**: 
     - Create domain/models.py
     - Remove schema.py
     - Update imports in existing files

2. **002.2**: Validate domain models work
   - Update all imports from `schema` to `anki_deck_factory.domain.models`
   - Run existing scripts to ensure compatibility
   - **Atomic commits**: Import updates + validation

**Critical Questions & Clarifications**:
- Are the current Pydantic models truly "domain pure" or do they have hidden dependencies?
- Should we split AnkiCard into separate models (e.g., SourceCard, TranslatedCard, ProcessedCard)?
- How do we handle the audio file paths - are they domain concerns or infrastructure?

**Acceptance Criteria**:
- Clean domain models exist in proper location
- No dependencies on external services in domain layer
- All existing functionality continues to work

---

## TASK 003: Abstract Connector Interfaces 🔵
**Business Value**: Enable future flexibility to swap LLM/TTS providers without code changes

### Sub-tasks:
1. **003.1**: Create LLM connector interface
   - Create `src/anki_deck_factory/connectors/llm/base.py`
   - Define `AbstractTranslator` with `translate()` method
   - **Atomic commits**: LLM base interface

2. **003.2**: Create TTS connector interface  
   - Create `src/anki_deck_factory/connectors/tts/base.py`
   - Define `AbstractTTS` with `synthesize()` method
   - **Atomic commits**: TTS base interface

3. **003.3**: Implement Gemini connector
   - Move `structured_gemini.py` to `src/anki_deck_factory/connectors/llm/gemini.py`
   - Implement `AbstractTranslator` interface
   - **Atomic commits**: 
     - Create gemini.py implementation
     - Remove old structured_gemini.py
     - Update imports

4. **003.4**: Implement Google TTS connector
   - Move `tts_engine.py` to `src/anki_deck_factory/connectors/tts/google.py`
   - Implement `AbstractTTS` interface
   - **Atomic commits**:
     - Create google.py implementation  
     - Remove old tts_engine.py
     - Update imports

**Critical Questions & Clarifications**:
- What's the right abstraction level? Should `translate()` take individual cards or entire decks?
- How do we handle caching in the abstract interface? Is caching implementation-specific or interface-level?
- Should error handling and retry logic be in the interface or implementation?
- How do we handle different LLM input/output schemas (Gemini vs. OpenAI vs. Claude)?
- What about TTS voice selection - interface concern or implementation detail?

**Acceptance Criteria**:
- Abstract interfaces defined for LLM and TTS
- Existing Gemini and Google implementations work through interfaces
- All existing functionality preserved

---

## TASK 004: IO Layer Consolidation 🔵
**Business Value**: Centralized, reusable file handling for all deck operations

### Sub-tasks:
1. **004.1**: Create APKG handler
   - Move deck loading/saving from `utilities.py` to `src/anki_deck_factory/io/apkg_handler.py`
   - Create clean interface for APKG operations
   - **Atomic commits**:
     - Create apkg_handler.py
     - Update utilities.py imports
     - Test APKG operations

2. **004.2**: Create CSV handler
   - Move CSV logic from `csv_export.py` to `src/anki_deck_factory/io/csv_handler.py` 
   - Create clean interface for CSV operations
   - **Atomic commits**:
     - Create csv_handler.py
     - Update csv_export.py to use handler
     - Test CSV operations

3. **004.3**: Update all scripts to use IO handlers
   - Update imports across all scripts
   - Ensure functionality is preserved
   - **Atomic commits**: Script updates + validation

**Critical Questions & Clarifications**:
- How do we handle media files in the IO layer? Are they part of the deck model or separate?
- Should IO handlers be stateful (hold connections) or stateless (pure functions)?
- How do we handle different CSV formats and field mappings?
- What about error handling for corrupted APKG files or malformed CSV?
- Should we support streaming for large decks or keep everything in memory?

**Acceptance Criteria**:
- Centralized APKG and CSV handling
- All scripts use new IO handlers
- No functionality regression

---

## TASK 005: Processing Steps Extraction 🔵
**Business Value**: Reusable, testable processing components for pipeline flexibility

### Sub-tasks:
1. **005.1**: Create frequency sorting processor
   - Move logic from `frequency_sort.py` to `src/anki_deck_factory/processing/sorting.py`
   - Create `FrequencySorter` class with `process()` method
   - **Atomic commits**:
     - Create sorting.py processor
     - Update frequency_sort.py to use processor
     - Test sorting functionality

2. **005.2**: Create audio processing processor
   - Move logic from `generate_all_audio.py` to `src/anki_deck_factory/processing/audio.py`
   - Create `AudioProcessor` class with TTS connector dependency
   - **Atomic commits**:
     - Create audio.py processor  
     - Update generate_all_audio.py to use processor
     - Test audio generation

3. **005.3**: Create translation processor
   - Extract translation logic from `main.py` to `src/anki_deck_factory/processing/translation.py`
   - Create `TranslationProcessor` with LLM connector dependency
   - **Atomic commits**:
     - Create translation.py processor
     - Update main.py to use processor
     - Test translation functionality

**Critical Questions & Clarifications**:
- Should processors be stateful (hold configuration) or receive config on each call?
- How do we handle processor dependencies? Dependency injection or factory pattern?
- What's the right interface? `process(deck) -> deck` or `process(cards) -> cards`?
- How do we handle processor failures? Rollback, partial success, or fail-fast?
- Should processors be async for performance or keep them synchronous?
- How do we handle progress reporting and logging across processors?

**Acceptance Criteria**:
- Reusable processing components exist
- Each processor has single responsibility
- All existing scripts work with new processors

---

## TASK 006: Configuration Models 🔵
**Business Value**: Type-safe configuration handling for pipeline definitions

### Sub-tasks:
1. **006.1**: Create configuration models
   - Create `src/anki_deck_factory/config/models.py`
   - Define Pydantic models for pipeline configuration
   - **Atomic commits**: Configuration models

2. **006.2**: Create sample configuration files
   - Create `configs/main_pipeline.yaml`
   - Create basic pipeline definition
   - **Atomic commits**: Sample configurations

**Critical Questions & Clarifications**:
- How complex should the configuration schema be? Support conditionals, loops, variables?
- Should we use JSON Schema, Pydantic, or custom validation?
- How do we handle environment-specific configs (dev/prod)?
- What about secrets management in configs? API keys, credentials?
- Should configs support inheritance or composition?
- How do we version configuration schemas for backward compatibility?

**Acceptance Criteria**:
- Type-safe configuration models
- Sample YAML configurations validate correctly

---

## TASK 007: Pipeline Runner Implementation 🔵
**Business Value**: Single, flexible pipeline execution system replacing multiple scripts

### Sub-tasks:
1. **007.1**: Create basic pipeline runner
   - Create `src/anki_deck_factory/processing/pipeline.py`
   - Implement YAML loading and step execution
   - **Atomic commits**: Basic pipeline runner

2. **007.2**: Implement step registration system
   - Create dynamic step loading from configuration
   - Map YAML steps to processor classes
   - **Atomic commits**: Step registration system

3. **007.3**: Add dependency injection
   - Implement connector instantiation from config
   - Wire dependencies automatically
   - **Atomic commits**: Dependency injection

4. **007.4**: Create pipeline validation
   - Validate configuration before execution
   - Provide helpful error messages
   - **Atomic commits**: Pipeline validation

**Critical Questions & Clarifications**:
- How do we handle step failures? Retry logic, circuit breakers, graceful degradation?
- Should the pipeline be resumable from any point? How do we handle checkpointing?
- How do we pass data between steps? In-memory, temporary files, or explicit contracts?
- What about parallel execution? Can some steps run concurrently?
- How do we handle dynamic step configuration based on previous step results?
- Should we support conditional execution (if/then logic in YAML)?
- How do we handle resource cleanup if pipeline fails midway?

**Acceptance Criteria**:
- YAML-driven pipeline execution works
- Automatic dependency injection 
- Clear error handling and validation

---

## TASK 008: Unified CLI Interface 🔵
**Business Value**: Single command-line interface replacing multiple scripts

### Sub-tasks:
1. **008.1**: Create CLI framework
   - Create `src/anki_deck_factory/cli.py` using Typer
   - Implement basic command structure
   - **Atomic commits**: CLI framework

2. **008.2**: Implement pipeline command
   - Add `run-pipeline` command
   - Support config file parameter
   - **Atomic commits**: Pipeline command

3. **008.3**: Implement utility commands
   - Add `export-csv`, `import-csv` commands  
   - Migrate existing CLI functionality
   - **Atomic commits**: Utility commands

4. **008.4**: Update package entry point
   - Configure `python -m anki_deck_factory.cli`
   - Update documentation
   - **Atomic commits**: Entry point configuration

**Critical Questions & Clarifications**:
- Should we maintain backward compatibility with existing script interfaces?
- How do we handle complex parameter passing that worked well with argparse?
- What about interactive modes vs. batch modes?
- How do we handle output formatting (JSON, table, plain text)?
- Should we support config file discovery (automatic .anki-deck-factory.yaml)?
- How do we handle logging and verbosity levels?
- What about shell completion and interactive help?

**Acceptance Criteria**:
- Single CLI replaces all existing scripts
- All original functionality accessible through CLI
- Clear help and documentation

---

## TASK 009: Card Template System 🔵
**Business Value**: Flexible card template system supporting multiple deck types

### Sub-tasks:
1. **009.1**: Create template engine
   - Move `card_templates.py` to `src/anki_deck_factory/builders/templates.py`
   - Create template registration system
   - **Atomic commits**: Template engine

2. **009.2**: Create Anki builder
   - Create `src/anki_deck_factory/builders/anki_builder.py`
   - Implement genanki integration with templates
   - **Atomic commits**: Anki builder

3. **009.3**: Define multiple card templates
   - Create recognition, production, listening, translation templates
   - **Atomic commits**: Multiple templates

**Critical Questions & Clarifications**:
- How do we define the 4 different card types? What makes Recognition different from Production?
- Should templates be data-driven (JSON/YAML) or code-based (Python classes)?
- How do we handle template inheritance and composition?
- What about template validation? How do we ensure templates work with different card data?
- Should templates handle their own media file inclusion logic?
- How do we support user-defined custom templates?

**Acceptance Criteria**:
- Flexible template system
- Multiple card types supported
- Clean integration with pipeline

---

## TASK 010: Subdeck Generation Feature 🔵
**Business Value**: Generate 4 specialized Anki subdecks from main deck (THE MAIN DELIVERABLE)

### Sub-tasks:
1. **010.1**: Create subdeck pipeline configuration
   - Create `configs/subdeck_pipeline.yaml`
   - Define 4 subdeck generation steps
   - **Atomic commits**: Subdeck configuration

2. **010.2**: Implement card filtering
   - Add card selection logic for subdecks
   - Support different filtering criteria
   - **Atomic commits**: Card filtering

3. **010.3**: Test subdeck generation
   - Generate all 4 subdecks from main deck
   - Validate each subdeck functions correctly
   - **Atomic commits**: Subdeck testing

4. **010.4**: Create subdeck documentation
   - Document each subdeck purpose and usage
   - Update README with new workflow
   - **Atomic commits**: Documentation

**Critical Questions & Clarifications**:
- **CRITICAL**: What exactly are the 4 subdeck types? We need clear definitions:
  - Recognition: German word → identify Polish translation?
  - Production: Polish word → produce German word?
  - Listening: German audio → identify word/translation?
  - Translation: Full sentence translation exercises?
- Should all subdecks contain the same cards or different subsets?
- How do we handle cards that don't fit certain subdeck types?
- Do subdecks need different scheduling/SRS settings?
- Should subdecks be standalone or have cross-references?
- How do we handle media files across multiple subdeck files?

**Acceptance Criteria**:
- 4 distinct subdecks generated from main deck
- Each subdeck optimized for specific learning mode
- Complete documentation and examples

---

## TASK 011: Migration Validation & Cleanup 🔵
**Business Value**: Ensure refactoring delivers same functionality with improved architecture

### Sub-tasks:
1. **011.1**: Create comprehensive tests
   - Test all migrated functionality
   - Ensure output matches original system
   - **Atomic commits**: Test suite

2. **011.2**: Update documentation
   - Update CLAUDE.md for new architecture
   - Update arch.md with new structure
   - **Atomic commits**: Documentation updates

3. **011.3**: Remove legacy files
   - Remove old script files after validation
   - Clean up obsolete code
   - **Atomic commits**: Legacy cleanup

4. **011.4**: Update Makefile
   - Update commands to use new CLI
   - Maintain backward compatibility where possible
   - **Atomic commits**: Makefile updates

**Acceptance Criteria**:
- All legacy functionality works through new architecture
- Complete documentation reflects new system
- Clean codebase with no obsolete files

---

## Success Metrics

### Technical Metrics:
- [ ] All existing functionality preserved
- [ ] 4 subdecks successfully generated
- [ ] Single CLI interface for all operations
- [ ] Configuration-driven pipeline execution
- [ ] Comprehensive test coverage

### Business Metrics:
- [ ] Subdeck generation feature delivered
- [ ] Team can work on isolated components
- [ ] New features can be added via configuration
- [ ] System is maintainable for 20-person team

**Critical Questions & Clarifications**:
- How do we verify that the refactored system produces identical outputs to the original?
- What's our rollback strategy if the refactoring introduces critical bugs?
- Should we maintain a compatibility layer for existing users?
- How do we handle the transition period where both old and new systems exist?

## Risk Mitigation:
- Each task preserves existing functionality
- Incremental migration reduces integration risk
- Comprehensive testing at each step
- Rollback plan available at any stage

## Most Critical Decisions Required Before Starting:

### 🚨 **TASK 010 - Subdeck Types Definition**
**This is the most critical blocker.** We need to clearly define:
1. What are the 4 subdeck types and their learning objectives?
2. How do card templates differ for each type?
3. What content goes into each subdeck?

### 🚨 **TASK 003 - Interface Abstractions**
**Second most critical.** Need to decide:
1. Interface granularity (card-level vs deck-level operations)
2. Caching strategy (interface vs implementation)
3. Error handling patterns

### 🚨 **TASK 007 - Pipeline Data Flow**
**Third most critical.** Need to decide:
1. How data flows between pipeline steps
2. Failure and recovery strategies
3. State management approach

**Recommendation**: Address these critical questions in separate planning sessions before starting implementation.