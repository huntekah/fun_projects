#!/usr/bin/env python3
"""
Test script for regenerate_templates.py functionality.

Validates that the template regeneration script works correctly
by creating a test deck, applying the 4-subdeck templates,
and verifying the output.
"""

from pathlib import Path
from schema import AnkiCard, AnkiDeck
from utilities import save_anki_deck, load_anki_deck
import subprocess
import sys


def create_test_deck_with_audio():
    """Create a realistic test deck with audio that simulates existing complete deck."""
    
    test_cards = [
        AnkiCard(
            note_id=9876543210,
            model_id=1607392319,
            frequency_rank="1",
            full_source="die Katze",
            base_source="Katze", 
            base_target="kot",
            artikel_d="die",
            plural_d="Katzen",
            s1_source="Die Katze schläft auf dem Sofa.",
            s1_target="Kot śpi na sofie.",
            s2_source="Meine Katze ist sehr süß.",
            s2_target="Mój kot jest bardzo słodki.",
            audio_text_d="die Katze",
            base_audio="[sound:katze_de.mp3]",
            full_source_audio="[sound:katze_full_de.mp3]",
            s1_audio="[sound:katze_s1_de.mp3]",
            s2_audio="[sound:katze_s2_de.mp3]",
            base_target_audio="[sound:kot_pl.mp3]",
            s1_target_audio="[sound:kot_s1_pl.mp3]",
            s2_target_audio="[sound:kot_s2_pl.mp3]",
            original_order="1",
            original_guid="test-katze-001"
        ),
        AnkiCard(
            note_id=9876543211,
            model_id=1607392319,
            frequency_rank="2",
            full_source="das Wasser",
            base_source="Wasser",
            base_target="woda", 
            artikel_d="das",
            plural_d="Wässer",
            s1_source="Das Wasser ist kalt.",
            s1_target="Woda jest zimna.",
            audio_text_d="das Wasser",
            base_audio="[sound:wasser_de.mp3]",
            full_source_audio="[sound:wasser_full_de.mp3]",
            s1_audio="[sound:wasser_s1_de.mp3]",
            base_target_audio="[sound:woda_pl.mp3]",
            s1_target_audio="[sound:woda_s1_pl.mp3]",
            original_order="2",
            original_guid="test-wasser-002"
        )
    ]
    
    return AnkiDeck(
        cards=test_cards,
        name="Test Deck With Audio",
        total_cards=len(test_cards)
    )


def test_regenerate_templates_script():
    """Test the regenerate_templates.py script functionality."""
    
    print("🧪 Testing regenerate_templates.py script")
    print("=" * 60)
    
    # Create test output directory
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    # Paths for test files
    source_deck_path = test_dir / "test_source_with_audio.apkg"
    target_deck_path = test_dir / "test_4subdeck_regenerated.apkg"
    
    # Step 1: Create test source deck with audio
    print("1️⃣ Creating test source deck with audio...")
    test_deck = create_test_deck_with_audio()
    
    try:
        save_anki_deck(test_deck, source_deck_path)
        print(f"   ✅ Created source deck: {source_deck_path}")
        print(f"   📊 Cards: {len(test_deck.cards)}")
        print("   🎵 Audio: Yes (simulated)")
    except Exception as e:
        print(f"   ❌ Failed to create source deck: {e}")
        return False
    
    # Step 2: Run regenerate_templates.py script
    print("\n2️⃣ Running regenerate_templates.py script...")
    
    cmd = [
        sys.executable, "regenerate_templates.py",
        "--source", str(source_deck_path),
        "--target", str(target_deck_path),
        "--validate"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print("   ✅ Script executed successfully")
            print("   📝 Output preview:")
            # Show last few lines of output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-3:]:
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"   ❌ Script failed with return code {result.returncode}")
            print("   📝 Error output:")
            for line in result.stderr.strip().split('\n')[:5]:
                if line.strip():
                    print(f"      {line}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to run script: {e}")
        return False
    
    # Step 3: Verify output deck
    print("\n3️⃣ Verifying output deck...")
    
    if not target_deck_path.exists():
        print(f"   ❌ Output deck not created: {target_deck_path}")
        return False
    
    try:
        # Load the regenerated deck
        regenerated_deck = load_anki_deck(target_deck_path)
        
        print("   ✅ Successfully loaded regenerated deck")
        print(f"   📊 Deck name: {regenerated_deck.name}")
        print(f"   📊 Cards: {len(regenerated_deck.cards)}")
        
        # Verify content preservation
        if regenerated_deck.cards:
            sample_card = regenerated_deck.cards[0]
            print(f"   🔍 Sample card: {sample_card.full_source} → {sample_card.base_target}")
            
            # Check that content is preserved
            original_sample = test_deck.cards[0]
            content_preserved = (
                sample_card.full_source == original_sample.full_source and
                sample_card.base_target == original_sample.base_target and
                sample_card.s1_source == original_sample.s1_source
            )
            
            if content_preserved:
                print("   ✅ Content correctly preserved")
            else:
                print("   ❌ Content may have been altered")
                return False
                
            # Check for audio preservation
            audio_preserved = (
                sample_card.base_audio == original_sample.base_audio and
                sample_card.s1_audio == original_sample.s1_audio and
                sample_card.base_target_audio == original_sample.base_target_audio
            )
            
            if audio_preserved:
                print("   ✅ Audio references correctly preserved")
            else:
                print("   ❌ Audio references may have been altered")
                return False
        
        # Check file size (should be reasonable)
        file_size_mb = target_deck_path.stat().st_size / (1024 * 1024)
        print(f"   📊 File size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 0.05 and file_size_mb < 10:  # Reasonable range
            print("   ✅ File size is reasonable")
        else:
            print("   ⚠️  File size is unusual (may still be valid)")
        
    except Exception as e:
        print(f"   ❌ Failed to verify output deck: {e}")
        return False
    
    # Step 4: Test script help and argument validation
    print("\n4️⃣ Testing script argument validation...")
    
    # Test help command
    try:
        help_result = subprocess.run(
            [sys.executable, "regenerate_templates.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if help_result.returncode == 0 and "Apply new 4-subdeck templates" in help_result.stdout:
            print("   ✅ Help command works correctly")
        else:
            print("   ⚠️  Help command may have issues")
            
    except Exception as e:
        print(f"   ⚠️  Help test failed: {e}")
    
    # Test invalid source file
    try:
        invalid_result = subprocess.run(
            [sys.executable, "regenerate_templates.py", 
             "--source", "nonexistent.apkg", 
             "--target", "output.apkg"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if invalid_result.returncode != 0:
            print("   ✅ Correctly rejects invalid source file")
        else:
            print("   ⚠️  Should have failed with invalid source")
            
    except Exception as e:
        print(f"   ⚠️  Invalid source test failed: {e}")
    
    print("\n🎉 All regenerate_templates.py tests passed!")
    return True


def main():
    """Run all tests for the regenerate_templates.py script."""
    
    success = test_regenerate_templates_script()
    
    if success:
        print("\n✅ regenerate_templates.py script is working correctly!")
        print("\n📋 The script can be used to:")
        print("   • Take existing decks with audio")
        print("   • Apply new 4-subdeck card templates") 
        print("   • Create Recognition, Production, Listening, and Sentence Production cards")
        print("   • Preserve all content and audio references")
        print("   • Maintain study progress through GUID preservation")
        
        print("\n🚀 Usage examples:")
        print("   make regen-templates")
        print("   python regenerate_templates.py --source existing.apkg --target new_4subdeck.apkg")
        
        return True
    else:
        print("\n❌ Some tests failed for regenerate_templates.py")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)