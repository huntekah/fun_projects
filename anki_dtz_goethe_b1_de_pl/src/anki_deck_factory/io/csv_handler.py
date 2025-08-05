import pandas as pd
import shutil
import zipfile
import tempfile
import os
from pathlib import Path
from typing import List, Optional, Tuple

from ..domain.models import AnkiCard, AnkiDeck


class CSVHandler:
    """Handler for CSV import/export operations with Anki decks."""
    
    def __init__(self):
        """Initialize the CSV handler."""
        pass
    
    def export_deck_to_csv(self, deck: AnkiDeck, output_path: Path) -> None:
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
                'original_guid': card.original_guid,
                'frequency_rank': card.frequency_rank,
                'original_order': card.original_order,
            }
            cards_data.append(card_dict)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(cards_data)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with UTF-8 encoding to preserve special characters
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"✅ Successfully exported {len(cards_data)} cards to {output_path}")
        print(f"🔍 CSV columns: {list(df.columns)}")
    
    def export_media_files(self, apkg_path: Path, media_output_dir: Path) -> List[str]:
        """
        Extract media files from .apkg and copy to output directory.
        
        Args:
            apkg_path: Path to the source .apkg file
            media_output_dir: Directory to copy media files to
            
        Returns:
            List of copied media filenames
        """
        print(f"📁 Extracting media files from {apkg_path} to {media_output_dir}")
        
        # Ensure output directory exists
        media_output_dir.mkdir(parents=True, exist_ok=True)
        
        copied_files = []
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Extract .apkg file
                with zipfile.ZipFile(apkg_path, 'r') as zip_file:
                    zip_file.extractall(tmpdir)
                
                # Copy media files (exclude database and system files)
                tmpdir_path = Path(tmpdir)
                for file_path in tmpdir_path.iterdir():
                    if file_path.is_file() and not file_path.name.startswith('_') and file_path.name != 'collection.anki2':
                        # Copy to media output directory
                        dest_path = media_output_dir / file_path.name
                        shutil.copy2(file_path, dest_path)
                        copied_files.append(file_path.name)
                        print(f"  📄 Copied: {file_path.name}")
        
        except Exception as e:
            print(f"⚠️  Error extracting media files: {e}")
            
        print(f"✅ Extracted {len(copied_files)} media files")
        return copied_files
    
    def load_deck_from_csv(self, csv_path: Path, media_dir: Optional[Path] = None) -> AnkiDeck:
        """
        Load AnkiDeck from CSV file.
        
        Args:
            csv_path: Path to the CSV file
            media_dir: Optional directory containing media files
            
        Returns:
            AnkiDeck object loaded from CSV
        """
        print(f"📄 Loading deck from CSV: {csv_path}")
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Read CSV file
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            print(f"📊 Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV file: {e}")
        
        # Convert DataFrame rows to AnkiCard objects
        cards = []
        for _, row in df.iterrows():
            try:
                # Handle NaN values by converting to empty strings
                card_data = {}
                for column in df.columns:
                    value = row[column]
                    if pd.isna(value):
                        card_data[column] = ""
                    else:
                        card_data[column] = str(value)
                
                # Ensure required fields have default values
                if 'note_id' not in card_data or not card_data['note_id']:
                    card_data['note_id'] = 0
                if 'model_id' not in card_data or not card_data['model_id']:
                    card_data['model_id'] = 0
                
                # Convert note_id and model_id to integers
                card_data['note_id'] = int(float(card_data['note_id']))
                card_data['model_id'] = int(float(card_data['model_id']))
                
                # Create AnkiCard object
                card = AnkiCard(**card_data)
                cards.append(card)
                
            except Exception as e:
                print(f"⚠️  Warning: Failed to process row {len(cards)}: {e}")
                continue
        
        # Create deck
        deck_name = csv_path.stem
        deck = AnkiDeck(cards=cards, name=deck_name)
        deck.total_cards = len(cards)
        
        print(f"✅ Successfully loaded {len(cards)} cards from CSV")
        return deck
    
    def export_contribution_package(self, apkg_path: Path, output_dir: Path) -> Tuple[Path, Path]:
        """
        Export complete contribution package (CSV + media files).
        
        Args:
            apkg_path: Source .apkg file
            output_dir: Output directory for contribution package
            
        Returns:
            Tuple of (csv_path, media_dir_path)
        """
        print(f"📦 Creating contribution package from {apkg_path}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Import here to avoid circular imports
        from .apkg_handler import APKGHandler
        
        # Load deck from .apkg
        apkg_handler = APKGHandler()
        deck = apkg_handler.load_deck(apkg_path)
        
        # Export to CSV
        csv_path = output_dir / "cards.csv"
        self.export_deck_to_csv(deck, csv_path)
        
        # Export media files
        media_dir = output_dir / "media"
        self.export_media_files(apkg_path, media_dir)
        
        print(f"✅ Contribution package created in {output_dir}")
        print(f"   📄 CSV: {csv_path}")
        print(f"   📁 Media: {media_dir}")
        
        return csv_path, media_dir