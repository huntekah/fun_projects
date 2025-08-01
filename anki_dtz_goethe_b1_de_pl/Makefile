.PHONY: check lint format lint-fix lint-fix-unsafe setup translate sort-frequency generate-audio complete-pipeline export-csv import-csv regen-audio test

# === Quality Assurance ===

# Run linting checks
check:
	uv run ruff check .

# Run linting and formatting
lint: check format

# Format code
format:
	uv run ruff format .

# Fix linting issues automatically
lint-fix:
	uv run ruff check . --fix

# Fix linting issues including unsafe fixes
lint-fix-unsafe:
	uv run ruff check . --fix --unsafe-fixes

# === Setup ===

# Initial setup: install dependencies and download frequency data
setup:
	uv sync
	./get_frequency_list
	@echo "✅ Setup complete! Ready to process Anki decks."

# === Core Pipeline ===

# Translate German-English deck to German-Polish
translate:
	uv run main.py
	@echo "✅ Translation complete: data/DTZ_Goethe_B1_DE_PL_Sample.apkg"

# Sort translated deck by German word frequency
sort-frequency:
	uv run frequency_sort.py --source data/DTZ_Goethe_B1_DE_PL_Sample.apkg --target data/DTZ_Goethe_B1_DE_PL_Sample_FrequencySorted.apkg
	@echo "✅ Frequency sorting complete: data/DTZ_Goethe_B1_DE_PL_Sample_FrequencySorted.apkg"

# Generate TTS audio for all fields (requires Google Cloud credentials)
generate-audio:
	uv run generate_all_audio.py --source data/DTZ_Goethe_B1_DE_PL_Sample_FrequencySorted.apkg --target data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg
	@echo "✅ Audio generation complete: data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg"

# Complete pipeline: translate → sort → generate audio
complete-pipeline: translate sort-frequency generate-audio
	@echo "🎉 Complete pipeline finished!"
	@echo "📁 Final deck: data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg"

# === Utilities ===

# Test TTS engine with a single random card
test-tts:
	uv run tts_engine.py
	@echo "✅ TTS test complete: check test_audio/ directory"

# Count characters for cost estimation
count-chars:
	uv run count_characters.py

# Export deck to CSV for community editing
export-csv:
	uv run csv_export.py export --source data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg --target contribution_package/
	@echo "✅ CSV export complete: contribution_package/"

# Import edited CSV back to APKG
import-csv:
	uv run csv_export.py import --source contribution_package/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.csv --target data/DTZ_Goethe_B1_DE_PL_Edited.apkg --media-dir contribution_package/media/
	@echo "✅ CSV import complete: data/DTZ_Goethe_B1_DE_PL_Edited.apkg"

# Regenerate audio for edited deck
regen-audio:
	uv run generate_all_audio.py --source data/DTZ_Goethe_B1_DE_PL_Edited.apkg --target data/DTZ_Goethe_B1_DE_PL_Final.apkg --no-confirm
	@echo "✅ Audio regeneration complete: data/DTZ_Goethe_B1_DE_PL_Final.apkg"

# Test media filtering functionality
test-media:
	uv run test_media_filtering.py

# === Help ===

help:
	@echo "🎯 DTZ Goethe B1 German-Polish Anki Deck Pipeline"
	@echo ""
	@echo "📋 Setup:"
	@echo "  make setup              - Install dependencies and download frequency data"
	@echo ""
	@echo "🔄 Core Pipeline:"
	@echo "  make translate          - Translate DE-EN deck to DE-PL"
	@echo "  make sort-frequency     - Sort cards by German word frequency"
	@echo "  make generate-audio     - Generate TTS audio for all fields"
	@echo "  make complete-pipeline  - Run full pipeline (translate → sort → audio)"
	@echo ""
	@echo "🛠️  Utilities:"
	@echo "  make test-tts          - Test TTS with random card"
	@echo "  make count-chars       - Count characters for cost estimation"
	@echo "  make test-media        - Test media filtering functionality"
	@echo ""
	@echo "🤝 Contribution Workflow:"
	@echo "  make export-csv        - Export deck to CSV for editing"
	@echo "  make import-csv        - Import edited CSV back to APKG"
	@echo "  make regen-audio       - Regenerate audio for edited deck"
	@echo ""
	@echo "✅ Quality:"
	@echo "  make check             - Run linting checks"
	@echo "  make format            - Format code"
	@echo "  make lint-fix               - Fix linting issues automatically"
	@echo "  make lint-fix-unsafe        - Fix linting issues (including unsafe fixes)"
	@echo "  make lint              - Run full linting + formatting"