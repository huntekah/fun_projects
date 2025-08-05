#!/usr/bin/env python3
"""
Test script to demonstrate the new AnkiCardTextFields approach.
Shows how it improves efficiency by only sending text fields to LLM.
"""

from schema import AnkiCard, AnkiCardTextFields
from prompt import create_text_translation_prompt

def test_text_model_conversion():
    """Test the text model conversion and prompt generation."""
    
    print("🧪 Testing AnkiCardTextFields approach\n")
    
    # Create a sample AnkiCard with full metadata
    original_card = AnkiCard(
        note_id=12345,
        model_id=67890,
        full_source="je … desto",
        base_source="je desto", 
        base_target="the … the",  # English translation
        artikel_d="",
        plural_d="",
        audio_text_d="je desto",
        s1_source="Je schneller wir arbeiten, desto früher sind wir zu Hause.",
        s1_target="The faster we work, the sooner we are home.",  # English
        s2_source="Je mehr ich lerne, desto besser verstehe ich.",
        s2_target="The more I learn, the better I understand.",  # English
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
        base_audio="audio_file_1.mp3",  # Audio metadata
        s1_audio="audio_file_2.mp3",   # Audio metadata
        s2_audio="audio_file_3.mp3",   # Audio metadata
        s3_audio="",
        s4_audio="",
        s5_audio="",
        s6_audio="",
        s7_audio="",
        s8_audio="",
        s9_audio="",
    )
    
    print("📋 ORIGINAL FULL CARD:")
    print(f"  note_id: {original_card.note_id}")
    print(f"  model_id: {original_card.model_id}")
    print(f"  base_target: '{original_card.base_target}'")
    print(f"  base_audio: '{original_card.base_audio}'")
    print(f"  original_order: '{original_card.original_order}'")
    print()
    
    # Convert to text-only model
    text_model = original_card.to_text_model()
    
    print("📝 TEXT-ONLY MODEL (sent to LLM):")
    print(f"  base_target: '{text_model.base_target}'")
    print(f"  s1_target: '{text_model.s1_target}'")
    print(f"  s2_target: '{text_model.s2_target}'")
    print("  ✅ No metadata fields (note_id, model_id, original_order)")
    print("  ✅ No audio fields (base_audio, s1_audio, etc.)")
    print()
    
    # Generate prompt for text model
    prompt = create_text_translation_prompt(text_model)
    print(f"📄 PROMPT LENGTH: {len(prompt)} characters")
    print("   (More focused, excludes metadata and audio fields)")
    print()
    
    # Simulate LLM translation result
    translated_text_model = AnkiCardTextFields(
        full_source="je … desto",  # German unchanged
        base_source="je desto",   # German unchanged
        base_target="im ..., tym...",  # Polish translation
        artikel_d="",
        plural_d="",
        audio_text_d="je desto",  # German unchanged
        s1_source="Je schneller wir arbeiten, desto früher sind wir zu Hause.",  # German unchanged
        s1_target="Im szybciej pracujemy, tym szybciej jesteśmy w domu.",  # Polish translation
        s2_source="Je mehr ich lerne, desto besser verstehe ich.",  # German unchanged
        s2_target="Im więcej się uczę, tym lepiej rozumiem.",  # Polish translation
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
    )
    
    print("🇵🇱 TRANSLATED TEXT MODEL (from LLM):")
    print(f"  base_target: '{translated_text_model.base_target}' (Polish)")
    print(f"  s1_target: '{translated_text_model.s1_target}' (Polish)")
    print(f"  s2_target: '{translated_text_model.s2_target}' (Polish)")
    print()
    
    # Convert back to full AnkiCard
    final_card = original_card.from_text_model(translated_text_model)
    
    print("📋 FINAL CARD (text translations + preserved metadata):")
    print(f"  note_id: {final_card.note_id} ✅ (preserved)")
    print(f"  model_id: {final_card.model_id} ✅ (preserved)")
    print(f"  base_target: '{final_card.base_target}' ✅ (translated)")
    print(f"  s1_target: '{final_card.s1_target}' ✅ (translated)")
    print(f"  s2_target: '{final_card.s2_target}' ✅ (translated)")
    print(f"  base_audio: '{final_card.base_audio}' ✅ (preserved)")
    print(f"  s1_audio: '{final_card.s1_audio}' ✅ (preserved)")
    print(f"  s2_audio: '{final_card.s2_audio}' ✅ (preserved)")
    print(f"  original_order: '{final_card.original_order}' ✅ (preserved)")
    print()
    
    # Verify metadata was preserved
    assert final_card.note_id == 12345, "note_id should be preserved"
    assert final_card.model_id == 67890, "model_id should be preserved"
    assert final_card.original_order == "123", "original_order should be preserved"
    assert final_card.base_audio == "audio_file_1.mp3", "base_audio should be preserved"
    assert final_card.s1_audio == "audio_file_2.mp3", "s1_audio should be preserved"
    assert final_card.s2_audio == "audio_file_3.mp3", "s2_audio should be preserved"
    
    # Verify translations were applied
    assert final_card.base_target == "im ..., tym...", "translation should be applied"
    assert final_card.s1_target == "Im szybciej pracujemy, tym szybciej jesteśmy w domu.", "translation should be applied"
    assert final_card.s2_target == "Im więcej się uczę, tym lepiej rozumiem.", "translation should be applied"
    
    print("✅ All tests passed!")
    print()
    print("🎯 BENEFITS:")
    print("  • Faster: LLM processes fewer fields")
    print("  • Cheaper: Smaller prompts and responses")
    print("  • More accurate: No LLM hallucinations in metadata")
    print("  • 100% metadata preservation: Audio files, IDs, etc. never corrupted")
    print("  • Cleaner prompts: LLM focuses only on translation task")

def compare_old_vs_new_approach():
    """Compare the old full-card approach vs new text-only approach."""
    
    print("\n" + "="*60)
    print("📊 OLD vs NEW APPROACH COMPARISON")
    print("="*60)
    
    sample_card = AnkiCard(
        note_id=12345,
        model_id=67890,
        full_source="je … desto",
        base_source="je desto", 
        base_target="the … the",
        artikel_d="",
        plural_d="",
        audio_text_d="je desto",
        s1_source="Je schneller wir arbeiten, desto früher sind wir zu Hause.",
        s1_target="The faster we work, the sooner we are home.",
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
        base_audio="audio_file_1.mp3",
        s1_audio="audio_file_2.mp3",
        s2_audio="",
        s3_audio="",
        s4_audio="",
        s5_audio="",
        s6_audio="",
        s7_audio="",
        s8_audio="",
        s9_audio="",
    )
    
    # Old approach: Full card
    old_fields = len([field for field in sample_card.model_fields.keys()])
    
    # New approach: Text-only model
    text_model = sample_card.to_text_model()
    new_fields = len([field for field in text_model.model_fields.keys()])
    
    print("🔢 FIELD COUNT:")
    print(f"  Old approach (full AnkiCard): {old_fields} fields")
    print(f"  New approach (AnkiCardTextFields): {new_fields} fields")
    print(f"  Reduction: {old_fields - new_fields} fields ({((old_fields - new_fields) / old_fields * 100):.1f}%)")
    print()
    
    print("🎯 ELIMINATED FIELDS (no longer sent to LLM):")
    eliminated_fields = set(sample_card.model_fields.keys()) - set(text_model.model_fields.keys())
    for field in sorted(eliminated_fields):
        print(f"  • {field}")
    print()
    
    print("💰 EFFICIENCY BENEFITS:")
    print("  • Smaller prompts = lower token costs")
    print("  • Faster processing = reduced latency")
    print("  • No metadata corruption = 100% reliability")
    print("  • Focused translation = better quality")

if __name__ == "__main__":
    test_text_model_conversion()
    compare_old_vs_new_approach()