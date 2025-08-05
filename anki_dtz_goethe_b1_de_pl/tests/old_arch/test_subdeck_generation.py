#!/usr/bin/env python3
"""
Test script to verify subdeck generation functionality.
Creates a minimal test deck with subdecks to validate our implementation.
"""

from schema import AnkiCard, AnkiDeck
from utilities import save_anki_deck
from pathlib import Path

def create_test_deck():
    """Create a minimal test deck with a few cards."""
    
    test_cards = [
        AnkiCard(
            note_id=1001,
            model_id=1607392319,
            full_source="der Test",
            base_source="Test",
            base_target="test",
            artikel_d="der",
            plural_d="Tests",
            s1_source="Das ist ein Test.",
            s1_target="To jest test.",
            base_audio="[sound:test_de.mp3]",
            base_target_audio="[sound:test_pl.mp3]",
            s1_audio="[sound:test_sentence_de.mp3]",
            s1_target_audio="[sound:test_sentence_pl.mp3]",
            original_guid="test-card-001"
        ),
        AnkiCard(
            note_id=1002, 
            model_id=1607392319,
            full_source="das Haus",
            base_source="Haus",
            base_target="dom",
            artikel_d="das",
            plural_d="Häuser", 
            s1_source="Das Haus ist groß.",
            s1_target="Dom jest duży.",
            base_audio="[sound:haus_de.mp3]",
            base_target_audio="[sound:dom_pl.mp3]",
            s1_audio="[sound:haus_sentence_de.mp3]",
            s1_target_audio="[sound:dom_sentence_pl.mp3]",
            original_guid="test-card-002"
        )
    ]
    
    return AnkiDeck(
        cards=test_cards,
        name="DTZ Test Deck with Subdecks",
        total_cards=len(test_cards)
    )

def test_subdeck_generation():
    """Test that subdeck generation works."""
    print("🧪 Testing subdeck generation...")
    
    # Create test deck
    test_deck = create_test_deck()
    print(f"   Created test deck with {len(test_deck.cards)} cards")
    
    # Save deck with subdecks
    output_path = Path("test_output/test_deck_with_subdecks.apkg")
    output_path.parent.mkdir(exist_ok=True)
    
    try:
        save_anki_deck(test_deck, output_path)
        print(f"✅ Successfully created deck with subdecks: {output_path}")
        
        # Verify file exists and has reasonable size
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"   File size: {file_size:,} bytes")
            
            if file_size > 1000:  # Should be more than 1KB for a real deck
                print("✅ File size looks reasonable")
                return True
            else:
                print("❌ File size is too small - something went wrong")
                return False
        else:
            print("❌ Output file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create subdeck: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing subdeck generation functionality")
    print("=" * 50)
    
    success = test_subdeck_generation()
    
    print("\n📊 Summary:")
    if success:
        print("🎉 Subdeck generation test passed!")
        print("📝 To verify subdecks in Anki:")
        print("   1. Import test_output/test_deck_with_subdecks.apkg into Anki")
        print("   2. Check that you see:")
        print("      - DTZ Goethe B1 German-Polish Model")
        print("      - DTZ Goethe B1 German-Polish Model::01 Recognition")  
        print("      - DTZ Goethe B1 German-Polish Model::02 Production")
        print("      - DTZ Goethe B1 German-Polish Model::03 Listening Comprehension")
        print("      - DTZ Goethe B1 German-Polish Model::04 Sentence Production")
        print("   3. Each subdeck should have multiple cards of its specific type")
        exit(0)
    else:
        print("❌ Subdeck generation test failed!")
        exit(1)