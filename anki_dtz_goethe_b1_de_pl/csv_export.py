#!/usr/bin/env python3
"""
CSV export/import functions for Anki deck contribution workflow.
Converts AnkiDeck to/from CSV + media format for easy community contribution.
"""

import argparse
import pandas as pd
import shutil
import zipfile
import tempfile
import os
from pathlib import Path
from typing import List, Optional, Tuple
from schema import AnkiCard, AnkiDeck
from utilities import load_anki_deck, save_anki_deck


def export_deck_to_csv(deck: AnkiDeck, output_path: Path) -> None:
    """
    Export AnkiDeck to CSV format for contribution repository.
    
    Args:
        deck: AnkiDeck object to export
        output_path: Path to save the CSV file (e.g., 'cards.csv')
    """
    print(f"📄 Exporting {len(deck.cards)} cards to CSV: {output_path}")
    
    # Convert AnkiCard objects to list of dictionaries
    cards_data = []
    for card in deck.cards:
        card_dict = {
            'note_id': card.note_id,
            'model_id': card.model_id,
            'full_source': card.full_source,
            'base_source': card.base_source,
            'base_target': card.base_target,
            'artikel_d': card.artikel_d,
            'plural_d': card.plural_d,
            'audio_text_d': card.audio_text_d,
            's1_source': card.s1_source,
            's1_target': card.s1_target,
            's2_source': card.s2_source,
            's2_target': card.s2_target,
            's3_source': card.s3_source,
            's3_target': card.s3_target,
            's4_source': card.s4_source,
            's4_target': card.s4_target,
            's5_source': card.s5_source,
            's5_target': card.s5_target,
            's6_source': card.s6_source,
            's6_target': card.s6_target,
            's7_source': card.s7_source,
            's7_target': card.s7_target,
            's8_source': card.s8_source,
            's8_target': card.s8_target,
            's9_source': card.s9_source,
            's9_target': card.s9_target,
            'base_audio': card.base_audio,
            's1_audio': card.s1_audio,
            's2_audio': card.s2_audio,
            's3_audio': card.s3_audio,
            's4_audio': card.s4_audio,
            's5_audio': card.s5_audio,
            's6_audio': card.s6_audio,
            's7_audio': card.s7_audio,
            's8_audio': card.s8_audio,
            's9_audio': card.s9_audio,
            'original_order': card.original_order,
        }
        cards_data.append(card_dict)
    
    # Create DataFrame and export to CSV
    df = pd.DataFrame(cards_data)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Export with proper CSV formatting
    df.to_csv(
        output_path,
        index=False,  # Don't include row indices
        encoding='utf-8',
        quoting=1,  # Quote all non-numeric fields (handles multiline text)
        lineterminator='\n'  # Use consistent line endings
    )
    
    print(f"✅ Successfully exported {len(cards_data)} cards to {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")


def export_media_files(apkg_path: Path, media_output_dir: Path) -> List[str]:
    """
    Extract media files from .apkg file to media directory.
    
    Args:
        apkg_path: Path to the .apkg file
        media_output_dir: Directory to save media files
        
    Returns:
        List of extracted media file names
    """
    print(f"🎵 Extracting media files from {apkg_path} to {media_output_dir}")
    
    # Ensure media directory exists
    media_output_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_files = []
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract .apkg file
            with zipfile.ZipFile(apkg_path, "r") as z:
                z.extractall(tmpdir)
            
            # Find and copy media files (typically numbered files)
            for item in os.listdir(tmpdir):
                item_path = os.path.join(tmpdir, item)
                
                # Skip database files, only copy media
                if os.path.isfile(item_path) and item not in ['collection.anki2', 'media']:
                    # Check if it's likely a media file (numbered or has audio extension)
                    if (item.isdigit() or 
                        any(item.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg', '.m4a'])):
                        
                        output_file = media_output_dir / item
                        shutil.copy2(item_path, output_file)
                        extracted_files.append(item)
                        print(f"  📁 Extracted: {item}")
    
    except Exception as e:
        print(f"⚠️  Warning: Could not extract media files: {e}")
        return []
    
    print(f"✅ Successfully extracted {len(extracted_files)} media files")
    return extracted_files


def load_deck_from_csv(csv_path: Path, media_dir: Optional[Path] = None) -> AnkiDeck:
    """
    Load AnkiDeck from CSV file and optional media directory.
    
    Args:
        csv_path: Path to the CSV file containing card data
        media_dir: Optional path to media directory
        
    Returns:
        AnkiDeck: Loaded deck with cards
    """
    print(f"📄 Loading deck from CSV: {csv_path}")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Load CSV data
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}")
    
    print(f"📊 Loaded {len(df)} rows from CSV")
    
    # Convert DataFrame rows to AnkiCard objects
    cards = []
    for idx, row in df.iterrows():
        try:
            # Handle NaN values by converting to empty strings
            card_data = {}
            for col in df.columns:
                value = row[col]
                try:
                    is_na = bool(pd.isna(value))
                except (ValueError, TypeError):
                    is_na = pd.isna(value).any() if hasattr(pd.isna(value), 'any') else False
                if is_na:
                    card_data[col] = ""
                else:
                    card_data[col] = str(value)
            
            # Ensure required fields have proper types
            if 'note_id' in card_data:
                card_data['note_id'] = int(float(card_data['note_id'])) if card_data['note_id'] else 0
            if 'model_id' in card_data:
                card_data['model_id'] = int(float(card_data['model_id'])) if card_data['model_id'] else 0
            
            card = AnkiCard(**card_data)
            cards.append(card)
            
        except Exception as e:
            try:
                row_num = int(idx) + 1  # type: ignore
            except (ValueError, TypeError):
                row_num = str(idx)
            print(f"⚠️  Warning: Failed to parse row {row_num}: {e}")
            continue
    
    deck_name = csv_path.stem
    deck = AnkiDeck(
        cards=cards,
        name=deck_name,
        total_cards=len(cards)
    )
    
    print(f"✅ Successfully loaded {len(cards)} cards into deck '{deck_name}'")
    
    # Validate media files if media directory provided
    if media_dir and media_dir.exists():
        media_files = list(media_dir.glob('*'))
        print(f"📁 Found {len(media_files)} media files in {media_dir}")
    
    return deck


def generate_apkg_from_csv(csv_path: Path, output_apkg_path: Path, media_dir: Optional[Path] = None) -> None:
    """
    Complete pipeline: CSV + media → .apkg file.
    This function can be copied to the contribution repository.
    
    Args:
        csv_path: Path to the CSV file containing card data
        output_apkg_path: Path where to save the generated .apkg file
        media_dir: Optional path to media directory
    """
    print(f"🔧 Generating .apkg from CSV: {csv_path} → {output_apkg_path}")
    
    # Load deck from CSV
    deck = load_deck_from_csv(csv_path, media_dir)
    
    # Generate .apkg file using existing save function
    # Note: media_dir files will be included if they exist
    original_apkg_path = None  # No original .apkg for media extraction in this case
    
    # Create a temporary .apkg with media if media_dir exists
    if media_dir and media_dir.exists():
        print(f"📁 Including media files from {media_dir}")
        # The save_anki_deck function will handle media inclusion
        
    save_anki_deck(deck, output_apkg_path, original_apkg_path or Path())
    
    print(f"✅ Successfully generated {output_apkg_path}")
    file_size = output_apkg_path.stat().st_size / (1024 * 1024)
    print(f"   File size: {file_size:.1f} MB")


def export_contribution_package(apkg_path: Path, output_dir: Path) -> Tuple[Path, Path]:
    """
    Export complete contribution package: CSV + media files.
    
    Args:
        apkg_path: Source .apkg file
        output_dir: Directory to create contribution package
        
    Returns:
        Tuple of (csv_path, media_dir) for the exported package
    """
    print(f"📦 Creating contribution package from {apkg_path}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load deck from .apkg
    deck = load_anki_deck(apkg_path)
    
    # Export CSV
    csv_path = output_dir / "cards.csv"
    export_deck_to_csv(deck, csv_path)
    
    # Export media files
    media_dir = output_dir / "media"
    extracted_files = export_media_files(apkg_path, media_dir)
    
    # Create README for contributors
    readme_path = output_dir / "README.md"
    readme_content = f"""# DTZ Goethe B1 German-Polish Anki Deck

This repository contains the community-editable version of the DTZ Goethe B1 German-Polish vocabulary deck.

## Files

- `cards.csv` - The main card data (edit this file to contribute)
- `media/` - Audio files referenced by the cards
- `generate_deck.py` - Script to generate .apkg file from CSV

## How to Contribute

1. Edit `cards.csv` in your favorite spreadsheet application or text editor
2. Ensure German sentences remain unchanged (source fields)
3. Edit Polish translations (target fields) to improve accuracy
4. Run `python generate_deck.py` to create the updated .apkg file

## Statistics

- Total cards: {len(deck.cards)}
- Media files: {len(extracted_files)}
- Generated from: {apkg_path.name}

## Field Reference

### Content Fields
- `full_source`, `base_source` - German words/phrases (DO NOT EDIT)
- `base_target` - Polish translation of base word
- `artikel_d`, `plural_d` - German grammar info (DO NOT EDIT)
- `s1_source` through `s9_source` - German example sentences (DO NOT EDIT)
- `s1_target` through `s9_target` - Polish translations of example sentences

### Technical Fields  
- `note_id`, `model_id`, `original_order` - Internal Anki IDs (DO NOT EDIT)
- `base_audio` through `s9_audio` - Audio file references (DO NOT EDIT)
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Created contribution package in {output_dir}")
    print(f"   📄 CSV: {csv_path}")
    print(f"   📁 Media: {media_dir} ({len(extracted_files)} files)")
    print(f"   📖 README: {readme_path}")
    
    return csv_path, media_dir


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Export/import Anki decks to/from CSV for contribution workflow"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export APKG to CSV')
    export_parser.add_argument(
        "--source", "-s",
        type=Path,
        required=True,
        help="Source .apkg file to export"
    )
    export_parser.add_argument(
        "--target", "-t",
        type=Path,
        default=Path("contribution_package"),
        help="Target directory for CSV package"
    )
    
    # Import command  
    import_parser = subparsers.add_parser('import', help='Import CSV to APKG')
    import_parser.add_argument(
        "--source", "-s", 
        type=Path,
        required=True,
        help="Source CSV file to import"
    )
    import_parser.add_argument(
        "--target", "-t",
        type=Path,
        required=True,
        help="Target .apkg file to create"
    )
    import_parser.add_argument(
        "--media-dir", "-m",
        type=Path,
        help="Media directory (optional)"
    )
    
    args = parser.parse_args()
    
    if args.command == 'export':
        if not args.source.exists():
            print(f"❌ Source file not found: {args.source}")
            exit(1)
        
        print(f"📤 Exporting {args.source} to {args.target}")
        csv_path, media_dir = export_contribution_package(args.source, args.target)
        print(f"✅ Export complete: {csv_path}")
        
    elif args.command == 'import':
        if not args.source.exists():
            print(f"❌ Source CSV not found: {args.source}")
            exit(1)
            
        print(f"📥 Importing {args.source} to {args.target}")
        generate_apkg_from_csv(args.source, args.target, args.media_dir)
        print(f"✅ Import complete: {args.target}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()