#!/usr/bin/env python3
"""
Test script to demonstrate the copy_non_translation_fields_from_original function.
Shows how it fixes LLM hallucinations like 'string' in audio fields.
"""

from schema import AnkiCard
from utilities import copy_non_translation_fields_from_original

def test_cleaning_function():
    """Test the cleaning function with example data from your output."""
    
    print("🧪 Testing LLM output cleaning function\n")
    
    # Original card (what we loaded from .apkg)
    original_card = AnkiCard(
        note_id=12345,
        model_id=67890,
        full_source="je … desto",
        base_source="je desto", 
        base_target="",  # This was English, will be overwritten
        artikel_d="",
        plural_d="",
        audio_text_d="je desto",
        s1_source="Je schneller wir arbeiten, desto früher sind wir zu Hause.",
        s1_target="The faster we work, the sooner we are home.",  # English
        s2_source="",
        s2_target="",
        s3_source="",
        s3_target="",
        s4_source="",
        s4_target="",
        s5_source="",
        s5_target="",
        s6_source="",
        s6_target="",
        s7_source="",
        s7_target="",
        s8_source="",
        s8_target="",
        s9_source="",
        s9_target="",
        original_order="123",
        base_audio="audio_file_1.mp3",  # Real audio file
        s1_audio="audio_file_2.mp3",   # Real audio file
        s2_audio="",
        s3_audio="",
        s4_audio="",
        s5_audio="",
        s6_audio="",
        s7_audio="",
        s8_audio="",
        s9_audio="",
    )
    
    # Translated card (what LLM returned with hallucinations)
    translated_card = AnkiCard(
        note_id=123,  # LLM changed this incorrectly
        model_id=123,  # LLM changed this incorrectly
        full_source="je … desto",  # Should stay same
        base_source="je desto",   # Should stay same
        base_target="im ..., tym...",  # Polish translation - correct!
        artikel_d="",
        plural_d="",
        audio_text_d="je desto",
        s1_source="Je schneller wir arbeiten, desto früher sind wir zu Hause.",
        s1_target="Im szybciej pracujemy, tym szybciej jesteśmy w domu.",  # Polish - correct!
        s2_source="",
        s2_target="",
        s3_source="",
        s3_target="",
        s4_source="",
        s4_target="",
        s5_source="",
        s5_target="",
        s6_source="",
        s6_target="",
        s7_source="",
        s7_target="",
        s8_source="",
        s8_target="",
        s9_source="",
        s9_target="",
        original_order="string",  # LLM hallucination!
        base_audio="string",      # LLM hallucination!
        s1_audio="string",        # LLM hallucination!
        s2_audio="string",        # LLM hallucination!
        s3_audio="string",        # LLM hallucination!
        s4_audio="string",        # LLM hallucination!
        s5_audio="string",        # LLM hallucination!
        s6_audio="string",        # LLM hallucination!
        s7_audio="string",        # LLM hallucination!
        s8_audio="string",        # LLM hallucination!
        s9_audio="string",        # LLM hallucination!
    )
    
    print("📋 BEFORE CLEANING:")
    print(f"  original_order: '{translated_card.original_order}'")
    print(f"  base_audio: '{translated_card.base_audio}'")
    print(f"  s1_audio: '{translated_card.s1_audio}'")
    print(f"  note_id: {translated_card.note_id}")
    print(f"  base_target: '{translated_card.base_target}' ✅ (this should stay)")
    print()
    
    # Clean the card
    cleaned_card, issues_fixed = copy_non_translation_fields_from_original(translated_card, original_card)
    
    print("\n📋 AFTER CLEANING:")
    print(f"  original_order: '{cleaned_card.original_order}'")
    print(f"  base_audio: '{cleaned_card.base_audio}'")
    print(f"  s1_audio: '{cleaned_card.s1_audio}'")
    print(f"  note_id: {cleaned_card.note_id}")
    print(f"  base_target: '{cleaned_card.base_target}' ✅ (translation preserved)")
    print()
    
    # Verify the cleaning worked
    assert cleaned_card.original_order == "123", "original_order should be restored"
    assert cleaned_card.base_audio == "audio_file_1.mp3", "base_audio should be restored"
    assert cleaned_card.s1_audio == "audio_file_2.mp3", "s1_audio should be restored"
    assert cleaned_card.note_id == 12345, "note_id should be restored"
    assert cleaned_card.base_target == "im ..., tym...", "translation should be preserved"
    assert cleaned_card.s1_target == "Im szybciej pracujemy, tym szybciej jesteśmy w domu.", "translation should be preserved"
    
    print("✅ All tests passed! The cleaning function works correctly.")
    print(f"🎯 LLM hallucinations fixed: {issues_fixed} issues, translations preserved!")

if __name__ == "__main__":
    test_cleaning_function()