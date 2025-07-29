#!/usr/bin/env python3
"""
Frequency-based sorting for Anki cards using German word frequency data.
Sorts cards by frequency rank to optimize learning order.
"""

import re
import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from schema import AnkiCard, AnkiDeck
from csv_export import export_deck_to_csv, load_deck_from_csv


def load_frequency_list(frequency_file: Path) -> Dict[str, int]:
    """
    Load German frequency list from file.
    Expected format: "word frequency_count" per line.
    
    Args:
        frequency_file: Path to frequency list file (e.g., de_50k_frequency.txt)
        
    Returns:
        Dict mapping word -> frequency_rank (lower rank = more frequent)
    """
    print(f"📖 Loading frequency list from {frequency_file}")
    
    if not frequency_file.exists():
        raise FileNotFoundError(f"Frequency file not found: {frequency_file}")
    
    frequency_map = {}
    
    with open(frequency_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # Expected format: "word frequency_count"
            parts = line.split()
            if len(parts) >= 2:
                try:
                    word = parts[0].lower()
                    frequency_count = int(parts[1])
                    # Use line number as rank (1-based, lower = more frequent)
                    frequency_map[word] = line_num
                except ValueError:
                    continue
    
    print(f"✅ Loaded {len(frequency_map)} words from frequency list")
    return frequency_map


def normalize_german_word(word: str) -> str:
    """
    Normalize German word for frequency matching.
    Handles common patterns in Anki cards vs frequency lists.
    
    Args:
        word: German word to normalize
        
    Returns:
        Normalized word for frequency lookup
    """
    if not word:
        return ""
    
    # Remove leading/trailing whitespace
    word = word.strip()
    
    # Handle parentheses: "(das) Haus" -> "Haus"
    if word.startswith('(') and ')' in word:
        word = word[word.index(')') + 1:].strip()
    
    # Handle reflexive verbs: "sich waschen" -> "waschen" 
    if word.startswith('sich '):
        word = word[5:].strip()
    
    # Handle commas: "gehen, ging, gegangen" -> "gehen"
    if ',' in word:
        word = word[:word.index(',')].strip()
    
    # Handle slashes: "der/die Angestellte" -> "Angestellte"
    if '/' in word:
        word = word[word.rindex('/') + 1:].strip()
    
    # Handle hyphens: "lang-term" -> "lang"
    if '-' in word:
        word = word[:word.index('-')].strip()
    
    # Remove articles at the beginning
    word_parts = word.split()
    if len(word_parts) > 1 and word_parts[0].lower() in ['der', 'die', 'das', 'ein', 'eine']:
        word = ' '.join(word_parts[1:])
    
    # Clean up extra spaces
    word = re.sub(r'\s+', ' ', word).strip()
    
    return word.lower()


def get_word_frequency_rank(card: AnkiCard, frequency_map: Dict[str, int]) -> int:
    """
    Get frequency rank for an Anki card's German word.
    Lower rank = more frequent = should appear earlier.
    
    Args:
        card: AnkiCard to analyze
        frequency_map: Word -> frequency_rank mapping
        
    Returns:
        Frequency rank (lower = more frequent), or large number if not found
    """
    # Try multiple German word sources in order of preference
    word_candidates = [
        card.base_source,    # Base German word
        card.full_source,    # Full German phrase
        card.audio_text_d,   # Audio text
    ]
    
    for candidate in word_candidates:
        if not candidate:
            continue
            
        normalized_word = normalize_german_word(candidate)
        if normalized_word in frequency_map:
            return frequency_map[normalized_word]
        
        # Try individual words if it's a phrase
        words = normalized_word.split()
        for word in words:
            if word in frequency_map:
                return frequency_map[word]
    
    # Return very high rank if word not found (sorts to end)
    return 999999


def sort_cards_by_frequency(cards: List[AnkiCard], frequency_map: Dict[str, int]) -> Tuple[List[AnkiCard], Dict]:
    """
    Sort Anki cards by German word frequency.
    More frequent words appear first.
    
    Args:
        cards: List of AnkiCard objects to sort
        frequency_map: Word -> frequency_rank mapping
        
    Returns:
        Tuple of (sorted_cards, stats_dict)
    """
    print(f"🔢 Sorting {len(cards)} cards by frequency...")
    
    # Add frequency rank to each card for sorting
    cards_with_rank = []
    found_count = 0
    unmatched_words = []
    
    for card in cards:
        freq_rank = get_word_frequency_rank(card, frequency_map)
        cards_with_rank.append((card, freq_rank))
        
        if freq_rank < 999999:
            found_count += 1
        else:
            # Collect unmatched words for analysis
            word_candidates = [
                card.base_source,
                card.full_source, 
                card.audio_text_d,
            ]
            # Use the first non-empty candidate as the unmatched word
            unmatched_word = next((w for w in word_candidates if w), "")
            if unmatched_word:
                unmatched_words.append({
                    'original': unmatched_word,
                    'normalized': normalize_german_word(unmatched_word),
                    'base_source': card.base_source,
                    'full_source': card.full_source
                })
    
    # Sort by frequency rank (ascending = most frequent first)
    sorted_cards_with_rank = sorted(cards_with_rank, key=lambda x: x[1])
    
    # Add frequency rank to each card for browser sorting
    sorted_cards = []
    for i, (card, rank) in enumerate(sorted_cards_with_rank):
        updated_card = card.model_copy()
        updated_card.frequency_rank = f"{i+1:04d}"  # Zero-padded: 0001, 0002, 0003...
        sorted_cards.append(updated_card)
    
    stats = {
        'total_cards': len(cards),
        'frequency_matches': found_count,
        'no_frequency_data': len(cards) - found_count,
        'match_percentage': (found_count / len(cards)) * 100 if cards else 0,
        'unmatched_words': unmatched_words
    }
    
    print(f"✅ Frequency sorting complete:")
    print(f"   📊 {found_count}/{len(cards)} cards matched frequency data ({stats['match_percentage']:.1f}%)")
    print(f"   🔝 Most frequent: '{sorted_cards[0].base_source}' (rank {sorted_cards_with_rank[0][1]})")
    if found_count > 1:
        print(f"   📈 Least frequent (matched): '{sorted_cards_with_rank[found_count-1][0].base_source}' (rank {sorted_cards_with_rank[found_count-1][1]})")
    
    # Print unmatched words for analysis
    if unmatched_words:
        print(f"\n❌ UNMATCHED WORDS ({len(unmatched_words)} cards):")
        for i, word_info in enumerate(unmatched_words, 1):
            print(f"   {i:2d}. '{word_info['original']}' → normalized: '{word_info['normalized']}'")
            if word_info['base_source'] != word_info['original']:
                print(f"       base_source: '{word_info['base_source']}'")
            if word_info['full_source'] != word_info['original']:
                print(f"       full_source: '{word_info['full_source']}'")
    
    return sorted_cards, stats


def frequency_sort_csv(input_csv: Path, output_csv: Path, frequency_file: Path) -> Dict:
    """
    Sort a CSV file of Anki cards by German word frequency.
    
    Args:
        input_csv: Input CSV file path
        output_csv: Output CSV file path  
        frequency_file: German frequency list file
        
    Returns:
        Statistics dictionary
    """
    print(f"📄 Frequency sorting CSV: {input_csv} → {output_csv}")
    
    # Load frequency data
    frequency_map = load_frequency_list(frequency_file)
    
    # Load cards from CSV
    deck = load_deck_from_csv(input_csv)
    
    # Sort cards by frequency
    sorted_cards, stats = sort_cards_by_frequency(deck.cards, frequency_map)
    
    # Create new deck with sorted cards
    sorted_deck = AnkiDeck(
        cards=sorted_cards,
        name=f"{deck.name}_frequency_sorted",
        total_cards=len(sorted_cards)
    )
    
    # Export sorted cards to new CSV
    export_deck_to_csv(sorted_deck, output_csv)
    
    print(f"✅ Frequency-sorted CSV saved: {output_csv}")
    return stats


def frequency_sort_deck(input_apkg: Path, output_apkg: Path, frequency_file: Path) -> Dict:
    """
    Sort an entire Anki deck by German word frequency.
    
    Args:
        input_apkg: Input .apkg file path
        output_apkg: Output .apkg file path
        frequency_file: German frequency list file
        
    Returns:
        Statistics dictionary
    """
    print(f"📦 Frequency sorting deck: {input_apkg} → {output_apkg}")
    
    from utilities import load_anki_deck, save_anki_deck
    
    # Load frequency data
    frequency_map = load_frequency_list(frequency_file)
    
    # Load deck
    deck = load_anki_deck(input_apkg)
    
    # Sort cards by frequency
    sorted_cards, stats = sort_cards_by_frequency(deck.cards, frequency_map)
    
    # Create new deck with sorted cards
    sorted_deck = AnkiDeck(
        cards=sorted_cards,
        name=f"{deck.name}_frequency_sorted",
        total_cards=len(sorted_cards)
    )
    
    # Save sorted deck
    save_anki_deck(sorted_deck, output_apkg, input_apkg)
    
    print(f"✅ Frequency-sorted deck saved: {output_apkg}")
    return stats


if __name__ == "__main__":
    # Example usage / test
    from pathlib import Path
    
    # Test with sample data  
    # Use full frequency list for better coverage (try de_full_frequency.txt if available)
    frequency_file = Path("data/de_full_frequency.txt")
    if not frequency_file.exists():
        frequency_file = Path("data/de_50k_frequency.txt")
    
    input_apkg = Path("data/DTZ_Goethe_B1_DE_PL_Sample.apkg")
    output_apkg = Path("data/DTZ_Goethe_B1_DE_PL_Sample_FrequencySorted.apkg")
    
    if input_apkg.exists():
        if not frequency_file.exists():
            print("❌ Frequency file not found. Run './get_frequency_list' first")
        else:
            stats = frequency_sort_deck(input_apkg, output_apkg, frequency_file)
            print(f"📊 Final statistics: {stats}")
    else:
        print(f"❌ Input file not found: {input_apkg}")