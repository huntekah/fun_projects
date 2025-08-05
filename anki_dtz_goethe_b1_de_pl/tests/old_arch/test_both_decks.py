#!/usr/bin/env python3
"""
Test script to verify that load_anki_deck works with both field naming schemes.
"""

from pathlib import Path
from utilities import load_anki_deck
from csv_export import export_deck_to_csv


def test_both_deck_types():
    """Test loading both original DE-EN deck and translated DE-PL deck."""
    
    print("🧪 Testing load_anki_deck with both field naming schemes\n")
    
    # Test 1: Original German-English deck (old naming scheme)
    original_deck_path = Path("data/B1_Wortliste_DTZ_Goethe_vocabsentensesaudiotranslation.apkg")
    if original_deck_path.exists():
        print("=" * 60)
        print("📋 TEST 1: Original DE-EN deck (old field naming)")
        print("=" * 60)
        
        try:
            original_deck = load_anki_deck(original_deck_path)
            print(f"✅ Successfully loaded original deck: {len(original_deck.cards)} cards")
            
            # Show sample card to verify field mapping
            if original_deck.cards:
                sample_card = original_deck.cards[0]
                print("\n📄 Sample card from original deck:")
                print(f"  note_id: {sample_card.note_id}")
                print(f"  full_source: '{sample_card.full_source}'")
                print(f"  base_source: '{sample_card.base_source}'")
                print(f"  base_target: '{sample_card.base_target}'")
                print(f"  s1_source: '{sample_card.s1_source}'")
                print(f"  s1_target: '{sample_card.s1_target}'")
                print(f"  base_audio: '{sample_card.base_audio}'")
            
            # Test CSV export with original deck
            csv_path = Path("test_original_deck.csv")
            export_deck_to_csv(original_deck, csv_path)
            print(f"✅ CSV export successful: {csv_path}")
            
        except Exception as e:
            print(f"❌ Failed to load original deck: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  Original deck not found, skipping test 1")
    
    # Test 2: Translated German-Polish deck (new naming scheme)
    translated_deck_path = Path("data/DTZ_Goethe_B1_DE_PL_Sample.apkg")
    if translated_deck_path.exists():
        print("\n" + "=" * 60)
        print("📋 TEST 2: Translated DE-PL deck (new field naming)")
        print("=" * 60)
        
        try:
            translated_deck = load_anki_deck(translated_deck_path)
            print(f"✅ Successfully loaded translated deck: {len(translated_deck.cards)} cards")
            
            # Show sample card to verify field mapping
            if translated_deck.cards:
                sample_card = translated_deck.cards[0]
                print("\n📄 Sample card from translated deck:")
                print(f"  note_id: {sample_card.note_id}")
                print(f"  full_source: '{sample_card.full_source}'")
                print(f"  base_source: '{sample_card.base_source}'")
                print(f"  base_target: '{sample_card.base_target}'")
                print(f"  s1_source: '{sample_card.s1_source}'")
                print(f"  s1_target: '{sample_card.s1_target}'")
                print(f"  base_audio: '{sample_card.base_audio}'")
            
            # Test CSV export with translated deck
            csv_path = Path("test_translated_deck.csv")
            export_deck_to_csv(translated_deck, csv_path)
            print(f"✅ CSV export successful: {csv_path}")
            
        except Exception as e:
            print(f"❌ Failed to load translated deck: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  Translated deck not found, skipping test 2")
    
    print("\n" + "=" * 60)
    print("🏁 Test Summary")
    print("=" * 60)
    print("Both deck types should load successfully with proper field mapping.")
    print("The load_anki_deck function now auto-detects field naming schemes.")


def compare_field_mappings():
    """Compare field mappings between both deck types."""
    
    print("\n🔍 Comparing field mappings between deck types\n")
    
    original_path = Path("data/B1_Wortliste_DTZ_Goethe_vocabsentensesaudiotranslation.apkg")
    translated_path = Path("data/DTZ_Goethe_B1_DE_PL_Sample.apkg")
    
    if not original_path.exists() or not translated_path.exists():
        print("⚠️  Both deck files needed for comparison")
        return
    
    try:
        # Load both decks
        original_deck = load_anki_deck(original_path)
        translated_deck = load_anki_deck(translated_path)
        
        print("📊 Deck Comparison:")
        print(f"  Original (DE-EN): {len(original_deck.cards)} cards")
        print(f"  Translated (DE-PL): {len(translated_deck.cards)} cards")
        
        # Compare first few cards if available
        if original_deck.cards and translated_deck.cards:
            print("\n🔍 Field mapping comparison (first card):")
            
            orig_card = original_deck.cards[0]
            trans_card = translated_deck.cards[0]
            
            fields_to_compare = [
                'full_source', 'base_source', 'base_target', 
                's1_source', 's1_target', 'base_audio'
            ]
            
            print(f"{'Field':<15} {'Original':<30} {'Translated':<30}")
            print("-" * 75)
            
            for field in fields_to_compare:
                orig_val = getattr(orig_card, field, '')[:25] + '...' if len(getattr(orig_card, field, '')) > 25 else getattr(orig_card, field, '')
                trans_val = getattr(trans_card, field, '')[:25] + '...' if len(getattr(trans_card, field, '')) > 25 else getattr(trans_card, field, '')
                print(f"{field:<15} {orig_val:<30} {trans_val:<30}")
        
        print("\n✅ Both deck types loaded successfully with unified schema!")
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_both_deck_types()
    compare_field_mappings()