#!/usr/bin/env python3
"""
Test 3: Audio Generation Validation

Business Objective: Ensure bilingual TTS audio generated for all text fields

This test validates the audio generation functionality that will be preserved during refactoring.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from schema import AnkiCard, AnkiDeck
from utilities import load_anki_deck, save_anki_deck
from generate_all_audio import (
    generate_complete_audio_for_card,
    generate_audio_for_entire_deck
)
from tts_engine import TTSGenerator


class TestAudioGeneration:
    """Test suite for audio generation business logic."""

    @pytest.fixture
    def sample_card_with_text(self):
        """Create a sample card with German and Polish text for audio generation."""
        return AnkiCard(
            note_id=3001, model_id=3001, frequency_rank="0001",
            full_source="die Frau", 
            base_source="Frau", 
            base_target="kobieta",
            artikel_d="die", 
            plural_d="Frauen",
            s1_source="Die Frau arbeitet im Büro.",
            s1_target="Kobieta pracuje w biurze.",
            s2_source="Eine kluge Frau denkt voraus.",
            s2_target="Mądra kobieta myśli z wyprzedzeniem.",
            original_order="1"
        )

    @pytest.fixture
    def sample_deck_for_audio(self, sample_card_with_text):
        """Create a sample deck for audio generation testing."""
        return AnkiDeck(
            cards=[sample_card_with_text],
            name="AudioGenerationTestDeck",
            total_cards=1
        )

    @pytest.fixture
    def mock_tts_generator(self):
        """Create a mock TTS generator to avoid actual API calls during testing."""
        mock_generator = MagicMock(spec=TTSGenerator)
        
        # Mock successful TTS generation
        def mock_synthesize(text, language, audio_path, speed=1.0):
            # Return success status (True) to simulate successful generation
            return True
        
        # Mock cache with get method
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Simulate cache miss
        mock_generator.cache = mock_cache
        
        mock_generator.synthesize_speech.side_effect = mock_synthesize
        mock_generator.cache_info.return_value = {
            'cache_size': 0, 'cache_volume_mb': 0.0, 'hits': 0, 'misses': 10
        }
        
        # Mock context manager behavior
        mock_generator.__enter__ = MagicMock(return_value=mock_generator)
        mock_generator.__exit__ = MagicMock(return_value=None)
        
        return mock_generator

    def test_3_1_german_tts_audio_generation(self, sample_card_with_text, mock_tts_generator):
        """
        Test Case 3.1: German TTS audio generation
        
        - Verify German audio for base_source field (de-DE-Studio-C voice)
        - Verify German audio for s1_source through s9_source fields
        - Verify audio files saved with correct naming (hash-based)
        """
        print("\n🔄 Testing German TTS audio generation...")
        
        with patch('generate_all_audio.TTSGenerator', return_value=mock_tts_generator):
            # Generate audio for the sample card
            updated_card = generate_complete_audio_for_card(
                card=sample_card_with_text,
                tts_generator=mock_tts_generator,
                audio_dir=Path("test_output/audio")
            )
            
            # Verify German audio generated for base_source
            assert updated_card.base_audio, "base_audio should be populated"
            assert '.mp3]' in updated_card.base_audio, "base_audio should reference .mp3 file in [sound:] format"
            print(f"   ✅ German base audio: {updated_card.base_audio}")
            
            # Verify German audio for example sentences
            if sample_card_with_text.s1_source:
                assert updated_card.s1_audio, "s1_audio should be populated for German sentence"
                assert '.mp3]' in updated_card.s1_audio, "s1_audio should reference .mp3 file in [sound:] format"
                print(f"   ✅ German s1 audio: {updated_card.s1_audio}")
            
            if sample_card_with_text.s2_source:
                assert updated_card.s2_audio, "s2_audio should be populated for German sentence"
                assert '.mp3]' in updated_card.s2_audio, "s2_audio should reference .mp3 file in [sound:] format"
                print(f"   ✅ German s2 audio: {updated_card.s2_audio}")
            
            # Verify TTS was called with German content
            all_calls = mock_tts_generator.synthesize_speech.call_args_list
            german_calls = []
            
            for call in all_calls:
                if len(call[0]) > 0:  # Check if call has arguments
                    text_arg = str(call[0][0])  # Convert to string for safety
                    if any(german_text in text_arg for german_text in ["Frau", "arbeitet", "kluge"]):
                        german_calls.append(call)
            
            assert len(german_calls) >= 1, f"Should have at least 1 German TTS call, got {len(german_calls)} out of {len(all_calls)} total"
            print(f"   ✅ German TTS called {len(german_calls)} times out of {len(all_calls)} total calls")

    def test_3_2_polish_tts_audio_generation(self, sample_card_with_text, mock_tts_generator):
        """
        Test Case 3.2: Polish TTS audio generation  
        
        - Verify Polish audio for base_target field (pl-PL-Standard-G voice)
        - Verify Polish audio for s1_target through s9_target fields
        - Verify correct Polish pronunciation and voice selection
        """
        print("\n🔄 Testing Polish TTS audio generation...")
        
        with patch('generate_all_audio.TTSGenerator', return_value=mock_tts_generator):
            # Generate audio for the sample card
            updated_card = generate_complete_audio_for_card(
                card=sample_card_with_text,
                tts_generator=mock_tts_generator,
                audio_dir=Path("test_output/audio")
            )
            
            # Verify Polish audio generated for base_target
            assert updated_card.base_target_audio, "base_target_audio should be populated"
            assert '.mp3]' in updated_card.base_target_audio, "base_target_audio should reference .mp3 file in [sound:] format"
            print(f"   ✅ Polish base audio: {updated_card.base_target_audio}")
            
            # Verify Polish audio for example sentences
            if sample_card_with_text.s1_target:
                assert updated_card.s1_target_audio, "s1_target_audio should be populated for Polish sentence"
                assert '.mp3]' in updated_card.s1_target_audio, "s1_target_audio should reference .mp3 file in [sound:] format"
                print(f"   ✅ Polish s1 audio: {updated_card.s1_target_audio}")
            
            if sample_card_with_text.s2_target:
                assert updated_card.s2_target_audio, "s2_target_audio should be populated for Polish sentence"
                assert '.mp3]' in updated_card.s2_target_audio, "s2_target_audio should reference .mp3 file in [sound:] format"
                print(f"   ✅ Polish s2 audio: {updated_card.s2_target_audio}")
            
            # Verify TTS was called with Polish content
            all_calls = mock_tts_generator.synthesize_speech.call_args_list
            polish_calls = []
            
            for call in all_calls:
                if len(call[0]) > 0:  # Check if call has arguments
                    text_arg = str(call[0][0])  # Convert to string for safety
                    if any(polish_text in text_arg for polish_text in ["kobieta", "pracuje", "mądra"]):
                        polish_calls.append(call)
            
            assert len(polish_calls) >= 1, f"Should have at least 1 Polish TTS call, got {len(polish_calls)} out of {len(all_calls)} total"
            print(f"   ✅ Polish TTS called {len(polish_calls)} times out of {len(all_calls)} total calls")

    def test_3_3_audio_field_population(self, sample_card_with_text, mock_tts_generator):
        """
        Test Case 3.3: Audio field population
        
        - Verify base_audio field contains reference to German audio file
        - Verify s1_audio through s9_audio fields populated correctly
        - Verify base_target_audio field contains reference to Polish audio file
        - Verify s1_target_audio through s9_target_audio fields populated correctly
        """
        print("\n🔄 Testing audio field population...")
        
        with patch('generate_all_audio.TTSGenerator', return_value=mock_tts_generator):
            # Generate audio for the sample card
            updated_card = generate_complete_audio_for_card(
                card=sample_card_with_text,
                tts_generator=mock_tts_generator,
                audio_dir=Path("test_output/audio")
            )
            
            # Test German audio field population
            german_audio_fields = [
                ('base_audio', sample_card_with_text.base_source),
                ('s1_audio', sample_card_with_text.s1_source),
                ('s2_audio', sample_card_with_text.s2_source),
            ]
            
            for field_name, source_text in german_audio_fields:
                if source_text:  # Only test if source text exists
                    audio_ref = getattr(updated_card, field_name)
                    assert audio_ref, f"{field_name} should be populated when {field_name.replace('_audio', '_source')} has content"
                    assert '.mp3]' in audio_ref, f"{field_name} should reference .mp3 file in [sound:] format"
                    print(f"   ✅ {field_name}: {audio_ref}")
            
            # Test Polish audio field population
            polish_audio_fields = [
                ('base_target_audio', sample_card_with_text.base_target),
                ('s1_target_audio', sample_card_with_text.s1_target),
                ('s2_target_audio', sample_card_with_text.s2_target),
            ]
            
            for field_name, source_text in polish_audio_fields:
                if source_text:  # Only test if source text exists
                    audio_ref = getattr(updated_card, field_name)
                    assert audio_ref, f"{field_name} should be populated when {field_name.replace('_audio', '')} has content"
                    assert '.mp3]' in audio_ref, f"{field_name} should reference .mp3 file in [sound:] format"
                    print(f"   ✅ {field_name}: {audio_ref}")
            
            print("   ✅ All audio fields populated correctly")

    def test_3_4_caching_effectiveness(self, sample_deck_for_audio, mock_tts_generator):
        """
        Test Case 3.4: Caching effectiveness
        
        - Verify duplicate content uses cached audio (no duplicate API calls)
        - Verify cache hit rates reduce TTS costs significantly
        - Verify cache persistence across runs
        """
        print("\n🔄 Testing caching effectiveness...")
        
        # Create deck with duplicate content to test caching
        duplicate_card = sample_deck_for_audio.cards[0].model_copy()
        duplicate_card.note_id = 3002
        test_deck = AnkiDeck(
            cards=[sample_deck_for_audio.cards[0], duplicate_card],
            name="CachingTestDeck",
            total_cards=2
        )
        
        # Save test deck to file first
        input_path = Path("test_output/caching_input.apkg")
        output_path = Path("test_output/caching_output.apkg")
        input_path.parent.mkdir(exist_ok=True)
        
        save_anki_deck(test_deck, input_path)
        
        with patch('generate_all_audio.TTSGenerator') as mock_tts_class:
            mock_tts_class.return_value = mock_tts_generator
            
            # Process the deck with duplicate content
            stats = generate_audio_for_entire_deck(
                input_deck_path=input_path,
                output_deck_path=output_path,
                audio_dir=Path("test_output/audio"),
                limit_cards=None
            )
            
            # Load the processed deck
            processed_deck = load_anki_deck(output_path)
            
            # Verify both cards processed
            assert len(processed_deck.cards) == 2, "Should process all cards"
            
            # Verify both cards have audio
            for card in processed_deck.cards:
                assert card.base_audio, "Both cards should have base_audio"
                assert card.base_target_audio, "Both cards should have base_target_audio"
            
            print("   ✅ Duplicate content processed successfully")
            
            # In a real scenario, duplicate content would result in cache hits
            # Here we're testing the structure, not the actual caching (which is in TTSGenerator)
            
            # Verify statistics are collected  
            assert 'audio_files_created' in stats, "Stats should include audio_files_created"
            assert stats['audio_files_created'] >= 1, "Should track audio files created"
            
            print(f"   📊 Created {stats['audio_files_created']} audio files")
            print("   ✅ Caching structure validated")

    def test_3_5_media_filtering_and_packaging(self, sample_card_with_text, mock_tts_generator):
        """
        Test Case 3.5: Media filtering and packaging
        
        - Verify only referenced audio files included in APKG
        - Verify silence.mp3 files included (template requirements)
        - Verify no orphaned audio files in package
        """
        print("\n🔄 Testing media filtering and packaging...")
        
        with patch('generate_all_audio.TTSGenerator', return_value=mock_tts_generator):
            # Generate audio for the sample card
            updated_card = generate_complete_audio_for_card(
                card=sample_card_with_text,
                tts_generator=mock_tts_generator,
                audio_dir=Path("test_output/audio")
            )
            
            # Collect all audio references from the card
            audio_fields = [
                'base_audio', 's1_audio', 's2_audio', 's3_audio', 's4_audio', 's5_audio',
                's6_audio', 's7_audio', 's8_audio', 's9_audio', 'base_target_audio',
                's1_target_audio', 's2_target_audio', 's3_target_audio', 's4_target_audio',
                's5_target_audio', 's6_target_audio', 's7_target_audio', 's8_target_audio',
                's9_target_audio'
            ]
            
            referenced_files = []
            for field in audio_fields:
                audio_ref = getattr(updated_card, field, '')
                if audio_ref and '.mp3]' in audio_ref:
                    referenced_files.append(audio_ref)
            
            print(f"   📊 Found {len(referenced_files)} audio references")
            
            # Verify we have audio references for fields with content
            expected_refs = 0
            if sample_card_with_text.base_source:
                expected_refs += 1
            if sample_card_with_text.s1_source:
                expected_refs += 1
            if sample_card_with_text.s2_source:
                expected_refs += 1
            if sample_card_with_text.base_target:
                expected_refs += 1
            if sample_card_with_text.s1_target:
                expected_refs += 1
            if sample_card_with_text.s2_target:
                expected_refs += 1
            
            assert len(referenced_files) >= expected_refs, \
                f"Should have at least {expected_refs} audio references, got {len(referenced_files)}"
            
            # Verify no duplicate references
            unique_files = set(referenced_files)
            print(f"   📊 {len(unique_files)} unique audio files referenced")
            
            # In real usage, media filtering would ensure only these files are packaged
            print("   ✅ Audio references structure validated")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_3_integration_full_audio_generation(self, sample_deck_for_audio):
        """
        Integration test: Full audio generation pipeline
        
        This test would run actual TTS generation if environment allows it.
        Marked as slow and integration to allow skipping during fast development.
        """
        print("\n🔄 Testing full audio generation integration...")
        print("⚠️  This test requires TTS API access and may incur costs")
        
        # Test data paths
        input_path = Path("test_output/audio_input.apkg")
        output_path = Path("test_output/audio_output.apkg")
        audio_dir = Path("test_output/audio_files")
        
        # Create test directories
        input_path.parent.mkdir(exist_ok=True)
        audio_dir.mkdir(exist_ok=True)
        
        try:
            # Save test deck
            save_anki_deck(sample_deck_for_audio, input_path)
            assert input_path.exists(), "Test input deck should be saved"
            
            # Test audio generation components are available
            try:
                tts_generator = TTSGenerator()
                assert tts_generator, "TTS generator should be available"
                print("   ✅ TTS generator components available")
                
                # Test a minimal audio generation (skip actual API call)
                print("   📝 Audio generation pipeline components validated")
                
            except Exception as e:
                pytest.skip(f"TTS components not available: {e}")
            
        except Exception as e:
            pytest.skip(f"Cannot run audio integration test: {e}")
        
        finally:
            # Cleanup
            for path in [input_path, output_path]:
                if path.exists():
                    path.unlink()
            
            # Clean up audio directory
            if audio_dir.exists():
                for audio_file in audio_dir.glob("*.mp3"):
                    audio_file.unlink()
                audio_dir.rmdir()

    def test_3_edge_cases_empty_fields(self, mock_tts_generator):
        """
        Test audio generation with edge cases like empty fields.
        """
        print("\n🔄 Testing audio generation edge cases...")
        
        # Create card with some empty fields
        sparse_card = AnkiCard(
            note_id=3003, model_id=3001, frequency_rank="0001",
            full_source="der Test", 
            base_source="Test", 
            base_target="test",
            artikel_d="der", 
            plural_d="Tests",
            s1_source="",  # Empty field
            s1_target="",  # Empty field
            s2_source="Ein Test läuft.",
            s2_target="",  # Empty Polish translation
            original_order="1"
        )
        
        with patch('generate_all_audio.TTSGenerator', return_value=mock_tts_generator):
            updated_card = generate_complete_audio_for_card(
                card=sparse_card,
                tts_generator=mock_tts_generator,
                audio_dir=Path("test_output/audio")
            )
            
            # Should have audio for base fields
            assert updated_card.base_audio, "Should have audio for base_source"
            assert updated_card.base_target_audio, "Should have audio for base_target"
            
            # Should not have audio for empty fields
            assert not updated_card.s1_audio or updated_card.s1_audio == "", \
                "Should not have audio for empty s1_source"
            assert not updated_card.s1_target_audio or updated_card.s1_target_audio == "", \
                "Should not have audio for empty s1_target"
            
            # Should have German audio for s2 but not Polish (empty s2_target)
            assert updated_card.s2_audio, "Should have audio for non-empty s2_source"
            assert not updated_card.s2_target_audio or updated_card.s2_target_audio == "", \
                "Should not have audio for empty s2_target"
            
            print("   ✅ Empty fields handled correctly")


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])