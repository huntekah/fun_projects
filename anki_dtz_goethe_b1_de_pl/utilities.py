import sqlite3
import zipfile
import tempfile
import os
import json
import genanki
from pathlib import Path
from typing import Dict, Any, List
from schema import AnkiCard, AnkiDeck
from card_templates import DTZ_MODEL_FIELDS, DTZ_CARD_TEMPLATES, DTZ_CARD_CSS


def load_anki_deck(path: Path) -> AnkiDeck:
    """
    Load an Anki deck from a .apkg file.
    
    Args:
        path: Path to the .apkg file
        
    Returns:
        AnkiDeck: Parsed deck with all cards
    """
    cards = []
    deck_name = path.stem
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Unzip the .apkg file
        with zipfile.ZipFile(path, "r") as z:
            z.extractall(tmpdir)

        # Path to the SQLite database
        db_path = os.path.join(tmpdir, "collection.anki2")

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get field names from models
        cursor.execute("SELECT models FROM col")
        models_json = cursor.fetchone()[0]
        models = json.loads(models_json)
        
        # Create a mapping of model_id to field names
        model_fields = {}
        for model_id, model in models.items():
            field_names = [field['name'] for field in model['flds']]
            model_fields[int(model_id)] = field_names

        # Get the note and card information
        cursor.execute("SELECT id, mid, flds FROM notes")
        notes = cursor.fetchall()

        # The 'flds' column contains the fields of a note joined by a special character
        # We can split this to get individual fields.
        for note_id, model_id, flds in notes:
            fields = flds.split('\x1f')
            field_names = model_fields.get(model_id, [])
            
            # Create a dictionary mapping field names to values
            fields_dict = {
                'note_id': note_id,
                'model_id': model_id
            }
            for i, field_value in enumerate(fields):
                field_name = field_names[i] if i < len(field_names) else f"field_{i}"
                fields_dict[field_name] = field_value
            
            # Create AnkiCard instance
            card = AnkiCard(**fields_dict)
            cards.append(card)

        conn.close()

    return AnkiDeck(cards=cards, name=deck_name, total_cards=len(cards))


def save_anki_deck(deck: AnkiDeck, output_path: Path, original_apkg_path: Path = None) -> None:
    """
    Save an AnkiDeck to a .apkg file using genanki.
    
    Args:
        deck: The AnkiDeck to save
        output_path: Path where to save the deck (.apkg format)
        original_apkg_path: Optional path to original .apkg file to extract media files
    """
    # Create genanki model that matches our card structure
    model = genanki.Model(
        1607392319,  # Model ID
        'DTZ Goethe B1 German-Polish Model',
        fields=DTZ_MODEL_FIELDS,
        templates=DTZ_CARD_TEMPLATES,
        css=DTZ_CARD_CSS
    )

    # Create genanki deck
    anki_deck = genanki.Deck(
        2059400110,  # Deck ID
        deck.name or "DTZ Goethe B1 Vocabulary"
    )

    # Convert our cards to genanki notes
    for card in deck.cards:
        # Ensure all fields are strings and handle None/empty values
        fields = [
            card.full_d or "",
            card.base_e or "",
            card.base_d or "",
            card.artikel_d or "",
            card.plural_d or "",
            card.audio_text_d or "",
            card.s1 or "",
            card.s1e or "",
            card.s2 or "",
            card.s2e or "",
            card.s3 or "",
            card.s3e or "",
            card.s4 or "",
            card.s4e or "",
            card.s5 or "",
            card.s5e or "",
            card.s6 or "",
            card.s6e or "",
            card.s7 or "",
            card.s7e or "",
            card.s8 or "",
            card.s8e or "",
            card.s9 or "",
            card.s9e or "",
            card.original_order or "",
            card.base_a or "",
            card.s1a or "",
            card.s2a or "",
            card.s3a or "",
            card.s4a or "",
            card.s5a or "",
            card.s6a or "",
            card.s7a or "",
            card.s8a or "",
            card.s9a or "",
        ]
        
        note = genanki.Note(
            model=model,
            fields=fields
        )
        anki_deck.add_note(note)

    # Extract media files from original .apkg if provided
    media_files = []
    if original_apkg_path and original_apkg_path.exists():
        media_files = _extract_media_files(original_apkg_path)

    # Generate the .apkg file
    genanki.Package(anki_deck, media_files=media_files).write_to_file(str(output_path))
    
    print(f"Saved {deck.total_cards} cards to {output_path}")


def _extract_media_files(apkg_path: Path) -> List[str]:
    """
    Extract media files from an existing .apkg file.
    
    Args:
        apkg_path: Path to the original .apkg file
        
    Returns:
        List of media file paths
    """
    media_files = []
    
    # Create a persistent temp directory for media files
    media_temp_dir = tempfile.mkdtemp(prefix="anki_media_")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Unzip the .apkg file
            with zipfile.ZipFile(apkg_path, "r") as z:
                z.extractall(tmpdir)
            
            # Find all media files (typically numbered files)
            import shutil
            for item in os.listdir(tmpdir):
                item_path = os.path.join(tmpdir, item)
                if os.path.isfile(item_path) and item.isdigit():
                    # Copy media file to persistent location
                    media_file_path = os.path.join(media_temp_dir, f"media_{item}")
                    shutil.copy2(item_path, media_file_path)
                    media_files.append(media_file_path)
    except Exception as e:
        print(f"Warning: Could not extract media files: {e}")
        # Clean up temp dir if extraction failed
        import shutil
        shutil.rmtree(media_temp_dir, ignore_errors=True)
        return []
    
    return media_files