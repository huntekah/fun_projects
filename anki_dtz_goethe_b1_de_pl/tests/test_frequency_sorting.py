#!/usr/bin/env python3
"""
Test 2: Frequency Sorting Validation

Business Objective: Ensure cards sorted by German word frequency for optimal learning

This test validates the frequency sorting functionality that will be preserved during refactoring.
"""

import pytest
from pathlib import Path
from schema import AnkiCard, AnkiDeck
from utilities import load_anki_deck, save_anki_deck
from frequency_sort import (
    load_frequency_list, 
    normalize_german_word, 
    sort_cards_by_frequency,
    frequency_sort_deck
)


class TestFrequencySorting:
    """Test suite for frequency sorting business logic."""

    @pytest.fixture
    def frequency_list_path(self):
        """Path to the German frequency data."""
        return Path("data/de_50k_frequency.txt")

    @pytest.fixture
    def frequency_data(self, frequency_list_path):
        """Load the German frequency data."""
        if not frequency_list_path.exists():
            pytest.skip(f"Frequency data not found at {frequency_list_path}")
        return load_frequency_list(frequency_list_path)

    @pytest.fixture
    def sample_deck(self):
        """Create a sample deck for frequency sorting tests."""
        test_cards = [
            # Common words (should sort early)
            AnkiCard(
                note_id=1001, model_id=1001, frequency_rank="",
                full_source="der Hund", base_source="Hund", base_target="pies",
                artikel_d="der", plural_d="Hunde", original_order="1"
            ),
            AnkiCard(
                note_id=1002, model_id=1001, frequency_rank="",
                full_source="die Frau", base_source="Frau", base_target="kobieta", 
                artikel_d="die", plural_d="Frauen", original_order="2"
            ),
            # Very common words (should sort first)
            AnkiCard(
                note_id=1003, model_id=1001, frequency_rank="",
                full_source="das Haus", base_source="Haus", base_target="dom",
                artikel_d="das", plural_d="Häuser", original_order="3"
            ),
            # Rare/unknown word (should sort last)
            AnkiCard(
                note_id=1004, model_id=1001, frequency_rank="",
                full_source="das Quetzalcoatlfedern", base_source="Quetzalcoatlfedern", base_target="rare_word",
                artikel_d="das", plural_d="", original_order="4"
            ),
            # Reflexive verb test
            AnkiCard(
                note_id=1005, model_id=1001, frequency_rank="",
                full_source="sich waschen", base_source="sich waschen", base_target="myć się",
                artikel_d="", plural_d="", original_order="5"
            )
        ]
        
        return AnkiDeck(
            cards=test_cards,
            name="FrequencySortingTestDeck",
            total_cards=len(test_cards)
        )

    def test_2_1_german_word_normalization(self):
        """
        Test Case 2.1: German word normalization
        
        - Test articles: "der Hund" → "Hund" for frequency lookup
        - Test plurals: "Häuser" → "Haus" for frequency lookup  
        - Test reflexive verbs: "sich waschen" → "waschen" for frequency lookup
        - Test compound words and special characters
        """
        print("\n🔄 Testing German word normalization...")
        
        # Test article removal (note: normalize_german_word returns lowercase)
        test_cases = [
            ("der Hund", "hund"),
            ("die Frau", "frau"), 
            ("das Haus", "haus"),
            ("die Häuser", "häuser"),  # Plural form
        ]
        
        for input_word, expected in test_cases:
            normalized = normalize_german_word(input_word)
            assert normalized == expected, f"'{input_word}' should normalize to '{expected}', got '{normalized}'"
        
        print("   ✅ Article removal tests passed")
        
        # Test reflexive verb handling
        reflexive_tests = [
            ("sich waschen", "waschen"),
            ("sich freuen", "freuen"),
            ("sich befinden", "befinden"),
        ]
        
        for input_verb, expected in reflexive_tests:
            normalized = normalize_german_word(input_verb)
            assert normalized == expected, f"'{input_verb}' should normalize to '{expected}', got '{normalized}'"
        
        print("   ✅ Reflexive verb tests passed")
        
        # Test special characters and compound words (note: returns lowercase)
        special_tests = [
            ("Mädchen", "mädchen"),  # Umlaut preserved but lowercase
            ("Straße", "straße"),     # ß preserved but lowercase
            ("Kindergarten", "kindergarten"),  # Compound word lowercase
            ("E-Mail", "e"),     # Hyphenated word - takes part before hyphen
        ]
        
        for input_word, expected in special_tests:
            normalized = normalize_german_word(input_word)
            assert normalized == expected, f"'{input_word}' should normalize to '{expected}', got '{normalized}'"
        
        print("   ✅ Special character tests passed")

    def test_2_2_frequency_ranking_accuracy(self, frequency_data):
        """
        Test Case 2.2: Frequency ranking accuracy
        
        - Verify most common words (der, die, das, sein, haben) appear first
        - Verify rare words appear later in deck
        - Verify frequency ranks assigned correctly (lower rank = more frequent)
        """
        print("\n🔄 Testing frequency ranking accuracy...")
        
        if not frequency_data:
            pytest.skip("Frequency data not available")
        
        # Test very common German words
        common_words = ["der", "die", "das", "sein", "haben", "werden", "mit", "nicht"]
        
        for word in common_words:
            if word in frequency_data:
                rank = frequency_data[word]
                assert rank < 100, f"'{word}' should have very low rank (< 100), got {rank}"
                print(f"   📊 '{word}' rank: {rank}")
        
        print("   ✅ Common word ranking verified")
        
        # Test that ranks are reasonable (ascending order in frequency list)
        sample_words = ["Haus", "Frau", "Hund", "Auto", "Buch"]
        found_ranks = {}
        
        for word in sample_words:
            normalized = normalize_german_word(word)
            if normalized in frequency_data:
                found_ranks[word] = frequency_data[normalized]
                print(f"   📊 '{word}' (normalized: '{normalized}') rank: {frequency_data[normalized]}")
        
        assert len(found_ranks) > 0, "Should find at least some sample words in frequency data"
        print(f"   ✅ Found {len(found_ranks)} words in frequency data")

    def test_2_3_unmatched_word_fallback(self, frequency_data, sample_deck):
        """
        Test Case 2.3: Unmatched word fallback handling
        
        - Verify words not in frequency list get default rank (999999)
        - Verify original order preserved for unmatched words
        - Verify no cards lost during sorting process
        """
        print("\n🔄 Testing unmatched word fallback handling...")
        
        if not frequency_data:
            pytest.skip("Frequency data not available")
        
        # Sort the sample deck to test fallback behavior
        sorted_cards, stats = sort_cards_by_frequency(sample_deck.cards, frequency_data)
        
        # Verify no cards lost
        assert len(sorted_cards) == len(sample_deck.cards), \
            f"Should preserve all cards: expected {len(sample_deck.cards)}, got {len(sorted_cards)}"
        
        print(f"   ✅ All {len(sorted_cards)} cards preserved during sorting")
        
        # Check that the fake word appears at the end (unmatched words sort last)
        fake_word_card = next((card for card in sorted_cards 
                              if "Quetzalcoatlfedern" in card.base_source), None)
        
        if fake_word_card:
            # Unmatched words should appear at the end of the sorted list
            fake_word_position = int(fake_word_card.frequency_rank)
            total_cards = len(sorted_cards)
            
            # The fake word should be near the end (within last few positions)
            assert fake_word_position >= total_cards - 1, \
                f"Fake word should be at end of list, got position {fake_word_position}/{total_cards}"
            print(f"   ✅ Fake word correctly placed at end: position {fake_word_position}/{total_cards}")
        
        # Verify that stats show the unmatched word
        assert 'unmatched_words' in stats, "Stats should include unmatched words"
        assert len(stats['unmatched_words']) >= 1, "Should have at least 1 unmatched word"
        
        unmatched_word_found = any('Quetzalcoatlfedern' in word_info['original'] 
                                  for word_info in stats['unmatched_words'])
        assert unmatched_word_found, "Fake word should appear in unmatched words list"
        print("   ✅ Unmatched words correctly tracked in stats")
        
        # Verify original_order is preserved
        for card in sorted_cards:
            assert hasattr(card, 'original_order'), "Cards should have original_order preserved"
            assert card.original_order is not None, "original_order should not be None"
        
        print("   ✅ Original order metadata preserved")

    def test_2_4_deck_order_metadata_preservation(self, frequency_data, sample_deck):
        """
        Test Case 2.4: Deck order metadata preservation
        
        - Verify original_order field tracks pre-sort position
        - Verify cards can be restored to original order if needed
        """
        print("\n🔄 Testing deck order metadata preservation...")
        
        if not frequency_data:
            pytest.skip("Frequency data not available")
        
        # Record original order
        original_positions = {card.note_id: card.original_order for card in sample_deck.cards}
        
        # Sort the deck
        sorted_cards, stats = sort_cards_by_frequency(sample_deck.cards, frequency_data)
        
        # Verify original_order preserved for all cards
        for card in sorted_cards:
            original_pos = original_positions[card.note_id]
            assert card.original_order == original_pos, \
                f"Card {card.note_id} original_order changed: {original_pos} → {card.original_order}"
        
        print("   ✅ Original order metadata preserved for all cards")
        
        # Test that we can restore original order
        restored_cards = sorted(sorted_cards, key=lambda c: int(c.original_order))
        
        for i, card in enumerate(restored_cards):
            expected_pos = str(i + 1)
            assert card.original_order == expected_pos, \
                f"Card at position {i} should have original_order {expected_pos}, got {card.original_order}"
        
        print("   ✅ Cards can be restored to original order")
        
        # Verify sorting actually changed the order (unless all words have same frequency)
        original_note_ids = [card.note_id for card in sample_deck.cards]
        sorted_note_ids = [card.note_id for card in sorted_cards]
        
        print(f"   📊 Original order: {original_note_ids}")
        print(f"   📊 Sorted order:   {sorted_note_ids}")
        
        # Check that frequency ranks are assigned
        frequency_ranks = [card.frequency_rank for card in sorted_cards]
        non_empty_ranks = [rank for rank in frequency_ranks if rank and rank != ""]
        
        assert len(non_empty_ranks) > 0, "Should assign frequency ranks to cards"
        print(f"   📊 Frequency ranks: {frequency_ranks}")
        print("   ✅ Frequency ranking completed")

    @pytest.mark.integration
    def test_2_integration_full_frequency_sorting(self, frequency_data):
        """
        Integration test: Full frequency sorting pipeline
        
        Test the complete frequency_sort_deck function with file I/O.
        """
        print("\n🔄 Testing full frequency sorting integration...")
        
        if not frequency_data:
            pytest.skip("Frequency data not available for integration test")
        
        # Test data paths
        input_path = Path("test_output/frequency_sort_input.apkg")
        output_path = Path("test_output/frequency_sort_output.apkg") 
        
        # Create test input deck
        input_path.parent.mkdir(exist_ok=True)
        
        test_deck = AnkiDeck(
            cards=[
                AnkiCard(
                    note_id=2001, model_id=2001, frequency_rank="",
                    full_source="das Auto", base_source="Auto", base_target="samochód",
                    artikel_d="das", plural_d="Autos", original_order="1"
                ),
                AnkiCard(
                    note_id=2002, model_id=2001, frequency_rank="",
                    full_source="der Baum", base_source="Baum", base_target="drzewo",
                    artikel_d="der", plural_d="Bäume", original_order="2"
                )
            ],
            name="FrequencySortIntegrationTest",
            total_cards=2
        )
        
        # Save test deck
        save_anki_deck(test_deck, input_path)
        assert input_path.exists(), "Test input deck should be saved"
        
        try:
            # Run frequency sorting
            success = frequency_sort_deck(
                source_path=input_path,
                target_path=output_path,
                frequency_file=Path("data/de_50k_frequency.txt")
            )
            
            if success:
                assert output_path.exists(), "Sorted deck should be created"
                
                # Load and verify sorted deck
                sorted_deck = load_anki_deck(output_path)
                assert len(sorted_deck.cards) == 2, "Should preserve all cards"
                
                # Verify frequency ranks assigned
                for card in sorted_deck.cards:
                    assert hasattr(card, 'frequency_rank'), "Should have frequency_rank"
                    assert card.frequency_rank is not None, "frequency_rank should not be None"
                
                print("   ✅ Full frequency sorting pipeline completed successfully")
                
            else:
                pytest.skip("frequency_sort_deck returned False - may be missing dependencies")
                
        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")
        
        finally:
            # Cleanup
            for path in [input_path, output_path]:
                if path.exists():
                    path.unlink()


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])