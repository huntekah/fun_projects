#!/usr/bin/env python3
"""
Count characters in specific Anki card fields.
"""

from pathlib import Path
from utilities import load_anki_deck


def count_characters_in_deck(deck_path: Path):
    """Count characters in specified fields across all cards."""
    
    print(f"📊 Analyzing character counts in: {deck_path}")
    
    # Load the deck
    deck = load_anki_deck(deck_path)
    
    # Initialize counters
    german_base_chars = 0
    polish_base_chars = 0
    german_sentences_chars = 0
    polish_sentences_chars = 0
    
    # Count characters in each card
    for card in deck.cards:
        # 1. German base_source
        if card.base_source:
            german_base_chars += len(card.base_source)
        
        # 2. Polish base_target
        if card.base_target:
            polish_base_chars += len(card.base_target)
        
        # 3. All German sentence fields (s1_source through s9_source)
        for i in range(1, 10):
            field_name = f"s{i}_source"
            field_value = getattr(card, field_name, "")
            if field_value:
                german_sentences_chars += len(field_value)
        
        # 4. All Polish sentence fields (s1_target through s9_target)
        for i in range(1, 10):
            field_name = f"s{i}_target"
            field_value = getattr(card, field_name, "")
            if field_value:
                polish_sentences_chars += len(field_value)
    
    # Calculate total characters
    total_german = german_base_chars + german_sentences_chars
    total_polish = polish_base_chars + polish_sentences_chars
    total_all = total_german + total_polish
    
    # Print results
    print(f"\n📈 CHARACTER COUNT RESULTS:")
    print(f"   Total cards analyzed: {len(deck.cards)}")
    print(f"\n🇩🇪 GERMAN TEXT:")
    print(f"   1. base_source (words): {german_base_chars:,} characters")
    print(f"   3. s1-s9_source (sentences): {german_sentences_chars:,} characters")
    print(f"   German total: {total_german:,} characters")
    print(f"\n🇵🇱 POLISH TEXT:")
    print(f"   2. base_target (words): {polish_base_chars:,} characters")
    print(f"   4. s1-s9_target (sentences): {polish_sentences_chars:,} characters")
    print(f"   Polish total: {total_polish:,} characters")
    print(f"\n📊 SUMMARY:")
    print(f"   Total characters: {total_all:,}")
    print(f"   German vs Polish ratio: {total_german/total_polish:.2f}:1" if total_polish > 0 else "   Polish has no content")
    
    return {
        'german_base': german_base_chars,
        'polish_base': polish_base_chars,
        'german_sentences': german_sentences_chars,
        'polish_sentences': polish_sentences_chars,
        'total_german': total_german,
        'total_polish': total_polish,
        'total_all': total_all
    }


if __name__ == "__main__":
    # Analyze the translated deck
    deck_path = Path("data/DTZ_Goethe_B1_DE_PL_Sample.apkg")
    
    if deck_path.exists():
        stats = count_characters_in_deck(deck_path)
    else:
        print(f"❌ Deck file not found: {deck_path}")