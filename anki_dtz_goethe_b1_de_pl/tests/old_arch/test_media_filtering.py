#!/usr/bin/env python3
"""
Test the media filtering functionality to ensure only referenced files are included.
"""

from utilities import _get_referenced_media_files
from schema import AnkiCard, AnkiDeck

def test_media_filtering():
    """Test that only referenced media files are included."""
    
    # Create test cards with specific audio references
    card1 = AnkiCard(
        note_id=1001,
        model_id=1001,
        base_source="Hund",
        base_target="pies", 
        base_audio="[sound:audio1.mp3]",
        base_target_audio="[sound:audio2.mp3]",
        s1_source="Der Hund bellt.",
        s1_target="Pies szczeka.",
        s1_audio="[sound:audio3.mp3]",
        s1_target_audio="[sound:audio4.mp3]"
    )
    
    card2 = AnkiCard(
        note_id=1002,
        model_id=1001,
        base_source="Katze",
        base_target="kot",
        base_audio="[sound:audio5.mp3]",
        base_target_audio="[sound:audio6.mp3]"
    )
    
    test_deck = AnkiDeck(cards=[card1, card2])
    
    # Create available media (more than what's referenced)
    available_media = {
        "audio1.mp3": "/path/to/audio1.mp3",
        "audio2.mp3": "/path/to/audio2.mp3", 
        "audio3.mp3": "/path/to/audio3.mp3",
        "audio4.mp3": "/path/to/audio4.mp3",
        "audio5.mp3": "/path/to/audio5.mp3",
        "audio6.mp3": "/path/to/audio6.mp3",
        "unused1.mp3": "/path/to/unused1.mp3",  # Not referenced
        "unused2.mp3": "/path/to/unused2.mp3",  # Not referenced
    }
    
    # Test the filtering
    referenced = _get_referenced_media_files(test_deck, available_media)
    
    print("📊 Media filtering test results:")
    print(f"   Available media files: {len(available_media)}")
    print(f"   Referenced media files: {len(referenced)}")
    print("   Expected referenced files: 6")
    
    expected_files = {"audio1.mp3", "audio2.mp3", "audio3.mp3", "audio4.mp3", "audio5.mp3", "audio6.mp3"}
    actual_files = set(referenced.keys())
    
    if actual_files == expected_files:
        print("   ✅ PASS: Correct files referenced")
        print(f"   Referenced files: {sorted(actual_files)}")
    else:
        print("   ❌ FAIL: Incorrect files referenced")
        print(f"   Expected: {sorted(expected_files)}")
        print(f"   Actual: {sorted(actual_files)}")
        print(f"   Missing: {expected_files - actual_files}")
        print(f"   Extra: {actual_files - expected_files}")
    
    # Test with missing files
    print("\n📊 Testing missing files warning:")
    available_missing = {
        "audio1.mp3": "/path/to/audio1.mp3",
        # audio2.mp3 missing
        "audio3.mp3": "/path/to/audio3.mp3",
        # Other files missing
    }
    
    referenced_missing = _get_referenced_media_files(test_deck, available_missing)
    print(f"   Found {len(referenced_missing)} of {len(expected_files)} expected files")

if __name__ == "__main__":
    test_media_filtering()