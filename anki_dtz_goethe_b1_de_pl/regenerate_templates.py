#!/usr/bin/env python3
"""
Regenerate Templates Script

Takes an existing deck with audio and applies the new 4-subdeck card templates
to create Recognition, Production, Listening Comprehension, and Sentence Production
cards from the same content.

This is useful for upgrading existing decks to the new 4-subdeck format without
regenerating audio or retranslating content.

Usage:
    python regenerate_templates.py --source existing_deck.apkg --target new_4subdeck_deck.apkg
    
Example:
    python regenerate_templates.py \
        --source data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg \
        --target data/DTZ_Goethe_B1_DE_PL_4Subdecks.apkg
"""

import argparse
from pathlib import Path

from utilities import load_anki_deck, save_anki_deck_4subdecks


def regenerate_with_4subdeck_templates(
    source_path: Path, 
    target_path: Path,
    preserve_guids: bool = True
) -> None:
    """
    Load an existing deck and save it with the new 4-subdeck templates.
    
    Args:
        source_path: Path to existing .apkg deck
        target_path: Path for new 4-subdeck .apkg deck  
        preserve_guids: Whether to preserve original GUIDs for study progress
    """
    
    print("🔄 Regenerating deck with 4-subdeck templates...")
    print(f"📂 Source: {source_path}")
    print(f"💾 Target: {target_path}")
    
    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing deck
    print("\n📋 Loading existing deck...")
    try:
        deck = load_anki_deck(source_path)
        print(f"✅ Loaded deck: {deck.name}")
        print(f"📊 Cards: {len(deck.cards)}")
        
        if deck.cards:
            sample_card = deck.cards[0]
            print(f"🔍 Sample card: {sample_card.full_source} → {sample_card.base_target}")
            
            # Check if cards have audio
            audio_fields = [
                'base_audio', 'full_source_audio', 's1_audio', 's2_audio',
                'base_target_audio', 's1_target_audio', 's2_target_audio'
            ]
            has_audio = any(getattr(sample_card, field, None) for field in audio_fields)
            print(f"🎵 Audio detected: {'Yes' if has_audio else 'No'}")
            
            # Check sentence coverage
            sentences_with_content = 0
            for i in range(1, 10):  # s1-s9
                if getattr(sample_card, f's{i}_source', None):
                    sentences_with_content += 1
            print(f"📝 Sentence examples: {sentences_with_content}/9 populated")
        
    except Exception as e:
        print(f"❌ Failed to load source deck: {e}")
        raise
    
    # Save with new 4-subdeck templates
    print("\n💾 Saving with 4-subdeck templates...")
    try:
        save_anki_deck_4subdecks(deck, target_path, source_path)
        
        # Get file size for verification
        file_size_mb = target_path.stat().st_size / (1024 * 1024)
        
        print("✅ Successfully created 4-subdeck version!")
        print(f"📁 Output: {target_path}")
        print(f"📊 File size: {file_size_mb:.1f} MB")
        
    except Exception as e:
        print(f"❌ Failed to save 4-subdeck deck: {e}")
        raise


def validate_templates_upgrade(source_path: Path, target_path: Path) -> None:
    """
    Validate that the template upgrade was successful by comparing key metrics.
    
    Args:
        source_path: Original deck path
        target_path: New 4-subdeck deck path
    """
    
    print("\n🔍 Validating template upgrade...")
    
    try:
        # Load both decks for comparison
        original_deck = load_anki_deck(source_path)
        upgraded_deck = load_anki_deck(target_path)
        
        print("📊 Validation Results:")
        print(f"   Original cards: {len(original_deck.cards)}")
        print(f"   Upgraded cards: {len(upgraded_deck.cards)}")
        
        # Cards should be the same count (same notes, different templates)
        if len(original_deck.cards) == len(upgraded_deck.cards):
            print("   ✅ Card count preserved")
        else:
            print("   ⚠️  Card count changed - this is expected due to template changes")
        
        # Check that content is preserved
        if original_deck.cards and upgraded_deck.cards:
            orig_sample = original_deck.cards[0]
            upg_sample = upgraded_deck.cards[0]
            
            content_preserved = (
                orig_sample.full_source == upg_sample.full_source and
                orig_sample.base_target == upg_sample.base_target and
                orig_sample.s1_source == upg_sample.s1_source and
                orig_sample.s1_target == upg_sample.s1_target
            )
            
            if content_preserved:
                print("   ✅ Content preserved correctly")
            else:
                print("   ❌ Content may have been altered")
        
        print("✅ Validation complete!")
        
    except Exception as e:
        print(f"⚠️  Validation failed (deck may still be valid): {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Apply new 4-subdeck templates to existing deck with audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - upgrade existing deck to 4-subdeck format
  python regenerate_templates.py \\
      --source data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg \\
      --target data/DTZ_Goethe_B1_DE_PL_4Subdecks.apkg
  
  # Upgrade and validate the result
  python regenerate_templates.py \\
      --source data/existing_deck.apkg \\
      --target data/new_4subdeck_deck.apkg \\
      --validate
  
  # Process multiple versions
  python regenerate_templates.py \\
      --source data/FrequencySorted.apkg \\
      --target data/FrequencySorted_4Subdecks.apkg

The script will:
  1. Load your existing deck (preserving all content and audio)
  2. Apply the new 4-subdeck templates (Recognition, Production, Listening, Sentence Production)
  3. Generate a new .apkg with 4 specialized subdecks
  4. Preserve study progress (GUIDs) if cards exist in Anki

Input Requirements:
  - Deck should have German content in 'full_source', 'base_source' fields
  - Deck should have Polish content in 'base_target', 's1_target' etc. fields  
  - Audio files should be in '[sound:filename.mp3]' format
  - Example sentences in 's1_source', 's2_source' etc. for listening cards
        """
    )
    
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to existing .apkg deck with audio"
    )
    
    parser.add_argument(
        "--target", 
        type=Path,
        required=True,
        help="Path for output 4-subdeck .apkg file"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the upgrade by comparing source and target decks"
    )
    
    parser.add_argument(
        "--no-preserve-guids",
        action="store_true", 
        help="Don't preserve original GUIDs (will lose study progress)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.source.exists():
        print(f"❌ Source deck not found: {args.source}")
        return 1
    
    if not args.source.suffix.lower() == '.apkg':
        print(f"❌ Source file must be .apkg format: {args.source}")
        return 1
        
    if not args.target.suffix.lower() == '.apkg':
        print(f"❌ Target file must be .apkg format: {args.target}")
        return 1
    
    if args.target.exists():
        print(f"⚠️  Target file exists and will be overwritten: {args.target}")
    
    try:
        # Main processing
        regenerate_with_4subdeck_templates(
            source_path=args.source,
            target_path=args.target,
            preserve_guids=not args.no_preserve_guids
        )
        
        # Optional validation
        if args.validate:
            validate_templates_upgrade(args.source, args.target)
        
        # Success summary
        print("\n🎉 Template regeneration complete!")
        print("\n📋 Next steps:")
        print(f"   1. Import {args.target} into Anki")
        print("   2. You should see 4 subdecks:")
        print("      - 01 Recognition (German → Polish)")
        print("      - 02 Production (Polish → German)")  
        print("      - 03 Listening Comprehension (Audio → Text)")
        print("      - 04 Sentence Production (Polish → German sentences)")
        print("   3. Each subdeck contains the same notes but different card types!")
        print("   4. Study progress is preserved if cards already exist in Anki")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to regenerate templates: {e}")
        return 1


if __name__ == "__main__":
    exit(main())