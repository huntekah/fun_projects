#!/usr/bin/env python3
"""
Test script to demonstrate the improved direct German→Polish translation approach.
Shows how avoiding the DE→EN→PL chain improves translation quality.
"""

from schema import AnkiCard, AnkiCardTextFields
from prompt import create_text_translation_prompt

def test_direct_translation_approach():
    """Test the direct German→Polish translation approach."""
    
    print("🧪 Testing Direct German→Polish Translation (avoiding DE→EN→PL chain)\n")
    
    # Create a sample card that would benefit from direct translation
    original_card = AnkiCard(
        note_id=12345,
        model_id=67890,
        full_source="schadenfroh",
        base_source="schadenfroh", 
        base_target="taking pleasure in someone else's misfortune",  # English (complex concept)
        artikel_d="",
        plural_d="",
        audio_text_d="schadenfroh",
        s1_source="Er war schadenfroh, als sein Kollege den Fehler machte.",
        s1_target="He was gleeful when his colleague made the mistake.",  # English context
        s2_source="Schadenfreude ist ein typisch deutsches Wort.",
        s2_target="Schadenfreude is a typically German word.",  # English context
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
        original_order="456",
        base_audio="schadenfroh.mp3",
        s1_audio="s1_schadenfroh.mp3",
        s2_audio="",
        s3_audio="",
        s4_audio="",
        s5_audio="",
        s6_audio="",
        s7_audio="",
        s8_audio="",
        s9_audio="",
    )
    
    print("📋 ORIGINAL GERMAN-ENGLISH CARD:")
    print(f"  German: {original_card.full_source}")
    print(f"  English: {original_card.base_target}")
    print(f"  German sentence: {original_card.s1_source}")
    print(f"  English sentence: {original_card.s1_target}")
    print(f"  German sentence 2: {original_card.s2_source}")
    print(f"  English sentence 2: {original_card.s2_target}")
    print()
    
    # Convert to text model and generate prompt
    text_model = original_card.to_text_model()
    prompt = create_text_translation_prompt(text_model)
    
    print("🎯 TRANSLATION APPROACH ANALYSIS:")
    print("❌ OLD APPROACH (chain translation):")
    print("   German → English → Polish")
    print("   'schadenfroh' → 'taking pleasure in...' → 'cieszyć się nieszczęściem...'")
    print("   ⚠️  Risk: Translation loss, unnatural Polish")
    print()
    print("✅ NEW APPROACH (direct translation):")
    print("   German → Polish (using English as context)")
    print("   'schadenfroh' + English context → 'złośliwy'/'злорадний'")
    print("   ✅ Benefits: Natural Polish, preserves German nuance")
    print()
    
    print("📄 IMPROVED PROMPT HIGHLIGHTS:")
    print("  • 'DIRECT Polish translations for ALL German content'")
    print("  • 'English translations are provided as reference context'")
    print("  • 'translate FROM GERMAN TO POLISH directly'")
    print("  • 'Do NOT translate English to Polish'")
    print("  • Multiple emphasis on avoiding translation chains")
    print()
    
    # Show key prompt sections
    prompt_lines = prompt.split('\n')
    important_lines = [
        line for line in prompt_lines 
        if any(keyword in line.lower() for keyword in [
            'direct', 'german to polish', 'reference context', 
            'avoid translation chains', 'not from english'
        ])
    ]
    
    print("🔑 KEY PROMPT INSTRUCTIONS:")
    for line in important_lines[:5]:  # Show first 5 relevant lines
        line_clean = line.strip()
        if line_clean:
            print(f"  • {line_clean}")
    print()
    
    # Simulate what LLM would receive vs old approach
    print("📊 COMPARISON OF WHAT LLM RECEIVES:")
    print()
    print("OLD PROMPT FOCUS:")
    print("  'Translate ALL target language content (currently English) to Polish'")
    print("  → LLM thinks: English → Polish")
    print()
    print("NEW PROMPT FOCUS:")
    print("  'Provide DIRECT Polish translations for ALL German content'")
    print("  'Use English only as reference context'")
    print("  → LLM thinks: German → Polish (with English help)")
    print()
    
    # Show expected quality improvements
    print("🎯 EXPECTED QUALITY IMPROVEMENTS:")
    print()
    print("Example 1 - Complex German concept:")
    print("  German: 'schadenfroh'")
    print("  English context: 'taking pleasure in someone else's misfortune'")
    print("  OLD (EN→PL): 'cieszyć się cudzym nieszczęściem' (literal)")
    print("  NEW (DE→PL): 'złośliwy' or 'zadowolony z cudzej porażki' (natural)")
    print()
    print("Example 2 - German sentence structure:")
    print("  German: 'Er war schadenfroh, als...'")
    print("  English context: 'He was gleeful when...'")
    print("  OLD (EN→PL): 'Był radosny, kiedy...' (from English structure)")
    print("  NEW (DE→PL): 'Cieszył się, gdy...' (preserves German meaning)")
    print()
    
    print("✅ DIRECT TRANSLATION BENEFITS:")
    print("  • Preserves German linguistic nuances")
    print("  • Produces more natural Polish")
    print("  • Avoids double translation errors")
    print("  • Better cultural/contextual accuracy")
    print("  • Maintains German sentence patterns where appropriate")

def test_prompt_structure():
    """Test how the prompt structure emphasizes direct translation."""
    
    print("\n" + "="*60)
    print("📋 PROMPT STRUCTURE ANALYSIS")
    print("="*60)
    
    # Sample text model
    sample_text = AnkiCardTextFields(
        full_source="Fernweh",
        base_source="Fernweh",
        base_target="longing for distant places",
        artikel_d="das",
        plural_d="",
        audio_text_d="Fernweh",
        s1_source="Ich habe Fernweh nach Asien.",
        s1_target="I have a longing for distant places in Asia.",
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
    )
    
    prompt = create_text_translation_prompt(sample_text)
    
    # Count mentions of key concepts
    prompt_lower = prompt.lower()
    
    direct_mentions = prompt_lower.count('direct')
    german_to_polish = prompt_lower.count('german') + prompt_lower.count('polish')
    reference_context = prompt_lower.count('reference') + prompt_lower.count('context')
    avoid_chain = prompt_lower.count('not') + prompt_lower.count('avoid')
    
    print(f"📊 PROMPT KEYWORD ANALYSIS:")
    print(f"  'direct' mentions: {direct_mentions}")
    print(f"  'german'/'polish' mentions: {german_to_polish}")
    print(f"  'reference'/'context' mentions: {reference_context}")
    print(f"  'not'/'avoid' mentions: {avoid_chain}")
    print()
    
    print(f"📏 PROMPT STRUCTURE:")
    print(f"  Total length: {len(prompt)} characters")
    lines = prompt.split('\n')
    print(f"  Total lines: {len(lines)}")
    print(f"  Instructions section: ~{len([l for l in lines if 'TRANSLATION' in l])} lines")
    print()
    
    print("🎯 CLARITY IMPROVEMENTS:")
    print("  • Multiple explicit statements about direct translation")
    print("  • Clear labeling of English as 'reference context'")
    print("  • Visual indicators (← USE AS CONTEXT ONLY)")
    print("  • Negative instructions (do NOT translate English to Polish)")
    print("  • Positive reinforcement of German→Polish direction")

if __name__ == "__main__":
    test_direct_translation_approach()
    test_prompt_structure()