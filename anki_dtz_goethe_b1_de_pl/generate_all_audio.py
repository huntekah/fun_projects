#!/usr/bin/env python3
"""
Generate TTS audio for ALL fields in the frequency-sorted Anki deck.
Creates audio for both German and Polish text across all cards.
Supports parameterized source/target languages for contribution workflow.
"""

import argparse
from pathlib import Path
from typing import Dict
from tts_engine import TTSGenerator
from utilities import load_anki_deck, save_anki_deck
from schema import AnkiCard, AnkiDeck


def generate_complete_audio_for_card(card: AnkiCard, tts_generator: TTSGenerator, audio_dir: Path, source_lang: str = "german", target_lang: str = "polish") -> AnkiCard:
    """
    Generate TTS audio for ALL text fields in an Anki card.
    
    Args:
        card: AnkiCard to generate audio for
        tts_generator: TTSGenerator instance with caching
        audio_dir: Directory to save audio files
        
    Returns:
        Updated AnkiCard with audio file references
    """
    # Create a copy of the card to modify
    updated_card = card.model_copy()
    
    # Define all text fields that need audio generation with variable speeds
    audio_fields = [
        # Source language fields -> source audio (slow for learning, normal for examples)
        ('audio_text_d', source_lang, 'full_source_audio', 1.00),
        ('base_source', source_lang, 'base_audio', 0.95),
        ('s1_source', source_lang, 's1_audio', 1.07),
        ('s2_source', source_lang, 's2_audio', 1.08),
        ('s3_source', source_lang, 's3_audio', 1.08),
        ('s4_source', source_lang, 's4_audio', 1.08),
        ('s5_source', source_lang, 's5_audio', 1.12),
        ('s6_source', source_lang, 's6_audio', 1.12),
        ('s7_source', source_lang, 's7_audio', 1.15),
        ('s8_source', source_lang, 's8_audio', 1.15),
        ('s9_source', source_lang, 's9_audio', 1.15),
        
        # Target language fields -> target audio (slow for translation, quick for examples)
        ('base_target', target_lang, 'base_target_audio', 1.00),
        ('s1_target', target_lang, 's1_target_audio', 1.25),
        ('s2_target', target_lang, 's2_target_audio', 1.20),
        ('s3_target', target_lang, 's3_target_audio', 1.20),
        ('s4_target', target_lang, 's4_target_audio', 1.20),
        ('s5_target', target_lang, 's5_target_audio', 1.25),
        ('s6_target', target_lang, 's6_target_audio', 1.25),
        ('s7_target', target_lang, 's7_target_audio', 1.30),
        ('s8_target', target_lang, 's8_target_audio', 1.30),
        ('s9_target', target_lang, 's9_target_audio', 1.30),
    ]
    
    generated_count = 0
    cached_count = 0
    
    for text_field, language, audio_field, speed in audio_fields:
        # Get text content
        text_content = getattr(card, text_field, "")
        
        if not text_content or not text_content.strip():
            # Set empty audio field for empty text
            setattr(updated_card, audio_field, "")
            continue
        
        # Generate filename based on content hash (for consistency)
        import hashlib
        content_hash = hashlib.md5(f"{text_content}_{language}".encode()).hexdigest()[:12]
        audio_filename = f"{content_hash}.mp3"
        audio_path = audio_dir / audio_filename
        
        # Check if this is a cache hit by looking at TTS generator cache
        cache_key = tts_generator._generate_cache_key(text_content, language, speed)
        is_cached = tts_generator.cache.get(cache_key) is not None
        
        # Generate audio with variable speed
        success = tts_generator.synthesize_speech(text_content, language, audio_path, speed)
        
        if success:
            # Set audio field reference in Anki format
            setattr(updated_card, audio_field, f"[sound:{audio_filename}]")
            if is_cached:
                cached_count += 1
            else:
                generated_count += 1
        else:
            # Set empty if generation failed
            setattr(updated_card, audio_field, "")
    
    if generated_count > 0 or cached_count > 0:
        print(f"   ✅ Generated: {generated_count}, Cached: {cached_count} audio files")
    
    return updated_card


def generate_audio_for_entire_deck(
    input_deck_path: Path, 
    output_deck_path: Path,
    audio_dir: Path |None = None,
    limit_cards: int|None = None,
    source_lang: str = "german",
    target_lang: str = "polish"
) -> Dict:
    """
    Generate TTS audio for an entire Anki deck.
    
    Args:
        input_deck_path: Path to input .apkg file
        output_deck_path: Path to save output .apkg file  
        audio_dir: Directory to save audio files (default: audio_files/)
        limit_cards: Optional limit for testing (None = all cards)
        
    Returns:
        Statistics dictionary
    """
    if audio_dir is None:
        audio_dir = Path("audio_files")
    
    audio_dir.mkdir(exist_ok=True)
    
    print("🎵 Generating complete TTS audio for deck")
    print(f"   Input: {input_deck_path}")
    print(f"   Output: {output_deck_path}")
    print(f"   Audio directory: {audio_dir}")
    
    # Load the frequency-sorted deck
    print("\n📂 Loading deck...")
    deck = load_anki_deck(input_deck_path)
    print(f"   Loaded {len(deck.cards)} cards")
    
    # Limit cards for testing if specified
    cards_to_process = deck.cards
    if limit_cards:
        cards_to_process = deck.cards[:limit_cards]
        print(f"   Limited to first {len(cards_to_process)} cards for testing")
    
    # Initialize TTS generator with caching
    with TTSGenerator() as tts:
        # Show initial cache info
        cache_info = tts.cache_info()
        print("\n💾 Cache info (before):")
        print(f"   Cached items: {cache_info['cache_size']}")
        print(f"   Cache size: {cache_info['cache_volume_mb']:.2f} MB")
        
        # Process all cards
        processed_cards = []
        
        for i, card in enumerate(cards_to_process, 1):
            print(f"\n🎤 Processing card {i}/{len(cards_to_process)}: {card.base_source}")
            
            updated_card = generate_complete_audio_for_card(card, tts, audio_dir, source_lang, target_lang)
            processed_cards.append(updated_card)
            
            # Show progress every 50 cards
            if i % 50 == 0:
                cache_info = tts.cache_info()
                print(f"   📊 Progress: {i}/{len(cards_to_process)} cards processed")
                print(f"   💾 Cache: {cache_info['cache_size']} items, {cache_info['cache_volume_mb']:.1f} MB")
        
        # Final cache info
        cache_info = tts.cache_info()
        print("\n💾 Cache info (after):")
        print(f"   Cached items: {cache_info['cache_size']}")
        print(f"   Cache size: {cache_info['cache_volume_mb']:.2f} MB")
    
    # Create new deck with audio
    audio_deck = AnkiDeck(
        cards=processed_cards,
        name=f"{deck.name}_WithAudio",
        total_cards=len(processed_cards)
    )
    
    # Save the deck with audio
    print("\n💾 Saving deck with audio...")
    save_anki_deck(audio_deck, output_deck_path, input_deck_path, audio_dir)
    
    # Count audio files generated
    audio_files = list(audio_dir.glob("*.mp3"))
    
    stats = {
        'input_cards': len(deck.cards),
        'processed_cards': len(processed_cards),
        'audio_files_created': len(audio_files),
        'cache_items': cache_info['cache_size'],
        'cache_size_mb': cache_info['cache_volume_mb'],
        'audio_dir_size_mb': sum(f.stat().st_size for f in audio_files) / (1024 * 1024)
    }
    
    print("\n🎯 COMPLETION SUMMARY:")
    print(f"   📊 Processed: {stats['processed_cards']}/{stats['input_cards']} cards")
    print(f"   🎵 Audio files: {stats['audio_files_created']} files")
    print(f"   💾 Cache: {stats['cache_items']} items ({stats['cache_size_mb']:.1f} MB)")
    print(f"   📁 Audio size: {stats['audio_dir_size_mb']:.1f} MB")
    print(f"   ✅ Deck saved: {output_deck_path}")
    
    return stats


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Generate TTS audio for Anki deck with configurable source/target languages"
    )
    parser.add_argument(
        "--source", "-s", 
        type=Path, 
        default=Path("data/DTZ_Goethe_B1_DE_PL_Sample_FrequencySorted.apkg"),
        help="Source .apkg file path"
    )
    parser.add_argument(
        "--target", "-t",
        type=Path,
        default=Path("data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg"),
        help="Target .apkg file path"
    )
    parser.add_argument(
        "--audio-dir", "-a",
        type=Path,
        default=Path("audio_files"),
        help="Directory to save audio files"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="Limit number of cards for testing"
    )
    parser.add_argument(
        "--no-confirm", 
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    args = parser.parse_args()
    
    if not args.source.exists():
        print(f"❌ Source file not found: {args.source}")
        exit(1)
    
    print("🚀 Starting TTS audio generation")
    print(f"   Source: {args.source}")
    print(f"   Target: {args.target}")
    print(f"   Languages: German → Polish")
    print("⚠️  This will generate audio for ALL text fields in the deck")
    print("💰 Estimated cost: ~$6-10 for full deck (depends on Google TTS pricing)")
    
    if args.limit:
        print(f"🧪 TESTING MODE: Processing only {args.limit} cards")
    
    if not args.no_confirm:
        print("\nPress Enter to continue, Ctrl+C to cancel...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            exit(0)
    
    stats = generate_audio_for_entire_deck(
        args.source, 
        args.target,
        audio_dir=args.audio_dir,
        limit_cards=args.limit,
        source_lang="german",
        target_lang="polish"
    )
    
    print(f"\n🎉 Complete! Import {args.target} into Anki to test the enhanced cards.")
    print(f"📊 Statistics: {stats}")


if __name__ == "__main__":
    main()