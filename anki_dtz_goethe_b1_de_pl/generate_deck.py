#!/usr/bin/env python3
"""
Standalone script for generating .apkg files from CSV + media files.
This script can be copied to the contribution repository to generate decks.

Requirements:
- pandas
- genanki
- Python 3.8+

Usage:
    python generate_deck.py [csv_file] [output_file] [media_dir]
    
Example:
    python generate_deck.py cards.csv deck.apkg media/
"""

import sys
import pandas as pd
import genanki
from pathlib import Path
from typing import List, Optional


# Card template definitions (copied from card_templates.py)
DTZ_MODEL_FIELDS = [
    {"name": "full_source"},     
    {"name": "base_target"},     
    {"name": "base_source"},     
    {"name": "artikel_d"},       
    {"name": "plural_d"},        
    {"name": "audio_text_d"},    
    {"name": "s1_source"},       
    {"name": "s1_target"},       
    {"name": "s2_source"},       
    {"name": "s2_target"},       
    {"name": "s3_source"},       
    {"name": "s3_target"},       
    {"name": "s4_source"},       
    {"name": "s4_target"},       
    {"name": "s5_source"},       
    {"name": "s5_target"},       
    {"name": "s6_source"},       
    {"name": "s6_target"},       
    {"name": "s7_source"},       
    {"name": "s7_target"},       
    {"name": "s8_source"},       
    {"name": "s8_target"},       
    {"name": "s9_source"},       
    {"name": "s9_target"},       
    {"name": "original_order"},  
    {"name": "base_audio"},      
    {"name": "s1_audio"},        
    {"name": "s2_audio"},        
    {"name": "s3_audio"},        
    {"name": "s4_audio"},        
    {"name": "s5_audio"},        
    {"name": "s6_audio"},        
    {"name": "s7_audio"},        
    {"name": "s8_audio"},        
    {"name": "s9_audio"},        
]

DTZ_CARD_TEMPLATES = [
    {
        "name": "German to Polish",
        "qfmt": "{{base_source}}{{base_audio}}",
        "afmt": """{{base_target}}<br>
{{full_source}}{{base_audio}}
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<hr id=answer>

<div style='font-family: Arial; font-size: 16px;'>{{s1_source}}{{s1_audio}}{{hint:s1_target}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s2_source}}{{s2_audio}}{{hint:s2_target}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s3_source}}{{s3_audio}}{{hint:s3_target}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s4_source}}{{s4_audio}}{{hint:s4_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s5_source}}{{s5_audio}}{{hint:s5_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s6_source}}{{s6_audio}}{{hint:s6_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s7_source}}{{s7_audio}}{{hint:s7_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s8_source}}{{s8_audio}}{{hint:s8_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s9_source}}{{s9_audio}}{{hint:s9_target}}</div>""",
    },
    {
        "name": "Polish to German", 
        "qfmt": "{{base_target}}",
        "afmt": """{{full_source}}{{base_audio}}<br>
{{base_target}}
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<hr id=answer>

<div style='font-family: Arial; font-size: 16px;'>{{s1_target}}{{s1_audio}}{{hint:s1_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s2_target}}{{s2_audio}}{{hint:s2_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s3_target}}{{s3_audio}}{{hint:s3_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s4_target}}{{s4_audio}}{{hint:s4_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s5_target}}{{s5_audio}}{{hint:s5_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s6_target}}{{s6_audio}}{{hint:s6_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s7_target}}{{s7_audio}}{{hint:s7_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s8_target}}{{s8_audio}}{{hint:s8_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s9_target}}{{s9_audio}}{{hint:s9_source}}</div>""",
    },
]

DTZ_CARD_CSS = """
.card {
    font-family: Arial, sans-serif;
    text-align: center;
    color: black;
    background-color: white;
}
.german {
    font-size: 20px;
    font-weight: bold;
    color: #2E86AB;
}
.polish {
    font-size: 18px;
    color: #A23B72;
}
.example {
    font-size: 14px;
    font-style: italic;
    color: #666;
    margin-top: 10px;
}
.example-pl {
    font-size: 14px;
    font-style: italic;
    color: #999;
}
"""


def load_cards_from_csv(csv_path: Path) -> List[dict]:
    """Load card data from CSV file."""
    print(f"📄 Loading cards from: {csv_path}")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}")
    
    print(f"📊 Loaded {len(df)} rows from CSV")
    
    cards = []
    for idx, row in df.iterrows():
        # Convert row to dictionary, handling NaN values
        card_data = {}
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                card_data[col] = ""
            else:
                card_data[col] = str(value)
        
        cards.append(card_data)
    
    print(f"✅ Successfully loaded {len(cards)} cards")
    return cards


def collect_media_files(media_dir: Optional[Path]) -> List[str]:
    """Collect media files from media directory."""
    if not media_dir or not media_dir.exists():
        print("⚠️  No media directory provided or found")
        return []
    
    print(f"📁 Collecting media files from: {media_dir}")
    
    media_files = []
    for file_path in media_dir.iterdir():
        if file_path.is_file():
            media_files.append(str(file_path))
    
    print(f"✅ Found {len(media_files)} media files")
    return media_files


def generate_apkg(cards: List[dict], output_path: Path, media_files: List[str]) -> None:
    """Generate .apkg file from cards and media."""
    print(f"🔧 Generating .apkg file: {output_path}")
    
    # Create genanki model
    model = genanki.Model(
        1607392319,  # Model ID (must match original)
        "DTZ Goethe B1 German-Polish Model",
        fields=DTZ_MODEL_FIELDS,
        templates=DTZ_CARD_TEMPLATES,
        css=DTZ_CARD_CSS,
    )
    
    # Create genanki deck
    deck = genanki.Deck(
        2059400110,  # Deck ID (must match original)
        "DTZ Goethe B1 German-Polish Vocabulary",
    )
    
    print(f"🃏 Converting {len(cards)} cards to genanki notes...")
    
    # Convert cards to genanki notes
    failed_cards = 0
    for i, card in enumerate(cards):
        try:
            # Extract fields in the correct order
            fields = [
                str(card.get('full_source', '')),
                str(card.get('base_target', '')),
                str(card.get('base_source', '')),
                str(card.get('artikel_d', '')),
                str(card.get('plural_d', '')),
                str(card.get('audio_text_d', '')),
                str(card.get('s1_source', '')),
                str(card.get('s1_target', '')),
                str(card.get('s2_source', '')),
                str(card.get('s2_target', '')),
                str(card.get('s3_source', '')),
                str(card.get('s3_target', '')),
                str(card.get('s4_source', '')),
                str(card.get('s4_target', '')),
                str(card.get('s5_source', '')),
                str(card.get('s5_target', '')),
                str(card.get('s6_source', '')),
                str(card.get('s6_target', '')),
                str(card.get('s7_source', '')),
                str(card.get('s7_target', '')),
                str(card.get('s8_source', '')),
                str(card.get('s8_target', '')),
                str(card.get('s9_source', '')),
                str(card.get('s9_target', '')),
                str(card.get('original_order', '')),
                str(card.get('base_audio', '')),
                str(card.get('s1_audio', '')),
                str(card.get('s2_audio', '')),
                str(card.get('s3_audio', '')),
                str(card.get('s4_audio', '')),
                str(card.get('s5_audio', '')),
                str(card.get('s6_audio', '')),
                str(card.get('s7_audio', '')),
                str(card.get('s8_audio', '')),
                str(card.get('s9_audio', '')),
            ]
            
            note = genanki.Note(model=model, fields=fields)
            deck.add_note(note)
            
        except Exception as e:
            failed_cards += 1
            print(f"⚠️  Warning: Failed to convert card {i+1}: {e}")
            continue
    
    if failed_cards > 0:
        print(f"⚠️  {failed_cards} cards failed to convert")
    
    # Generate .apkg file
    print("📦 Writing .apkg file...")
    try:
        package = genanki.Package(deck, media_files=media_files)
        package.write_to_file(str(output_path))
    except Exception as e:
        raise RuntimeError(f"Failed to write .apkg file: {e}")
    
    # Verify file was created
    if not output_path.exists():
        raise RuntimeError("Output file was not created successfully")
    
    file_size = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Successfully generated {output_path}")
    print(f"   Cards: {len(cards) - failed_cards}")
    print(f"   Media files: {len(media_files)}")
    print(f"   File size: {file_size:.1f} MB")


def main():
    """Main entry point for standalone script."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_deck.py <csv_file> [output_file] [media_dir]")
        print("\nExample:")
        print("  python generate_deck.py cards.csv")
        print("  python generate_deck.py cards.csv my_deck.apkg")
        print("  python generate_deck.py cards.csv my_deck.apkg media/")
        sys.exit(1)
    
    csv_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("generated_deck.apkg")
    media_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("media")
    
    try:
        # Load cards from CSV
        cards = load_cards_from_csv(csv_file)
        
        # Collect media files
        media_files = collect_media_files(media_dir)
        
        # Generate .apkg file
        generate_apkg(cards, output_file, media_files)
        
        print(f"\n🎉 Success! Generated deck: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()