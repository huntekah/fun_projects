import sqlite3
import zipfile
import tempfile
import os
import json
import genanki
from pathlib import Path
from typing import Dict, Any, List
from schema import AnkiCard, AnkiDeck


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
        'DTZ Goethe B1 Model',
        fields=[
            {'name': 'full_d'},
            {'name': 'base_e'},
            {'name': 'base_d'},
            {'name': 'artikel_d'},
            {'name': 'plural_d'},
            {'name': 'audio_text_d'},
            {'name': 's1'},
            {'name': 's1e'},
            {'name': 's2'},
            {'name': 's2e'},
            {'name': 's3'},
            {'name': 's3e'},
            {'name': 's4'},
            {'name': 's4e'},
            {'name': 's5'},
            {'name': 's5e'},
            {'name': 's6'},
            {'name': 's6e'},
            {'name': 's7'},
            {'name': 's7e'},
            {'name': 's8'},
            {'name': 's8e'},
            {'name': 's9'},
            {'name': 's9e'},
            {'name': 'original_order'},
            {'name': 'base_a'},
            {'name': 's1a'},
            {'name': 's2a'},
            {'name': 's3a'},
            {'name': 's4a'},
            {'name': 's5a'},
            {'name': 's6a'},
            {'name': 's7a'},
            {'name': 's8a'},
            {'name': 's9a'},
        ],
        templates=[
            {
                'name': 'German to English',
                'qfmt': '<div class="german">{{full_d}}</div><br>{{base_a}}',
                'afmt': '''
                <div class="german">{{full_d}}</div>
                <hr id="answer">
                <div class="english">{{base_e}}</div>
                {{#s1}}<br><div class="example">{{s1}}</div>{{/s1}}
                {{#s1e}}<div class="example-en">{{s1e}}</div>{{/s1e}}
                {{#s2}}<br><div class="example">{{s2}}</div>{{/s2}}
                {{#s2e}}<div class="example-en">{{s2e}}</div>{{/s2e}}
                {{#s3}}<br><div class="example">{{s3}}</div>{{/s3}}
                {{#s3e}}<div class="example-en">{{s3e}}</div>{{/s3e}}
                ''',
            },
            {
                'name': 'English to German',
                'qfmt': '<div class="english">{{base_e}}</div>',
                'afmt': '''
                <div class="english">{{base_e}}</div>
                <hr id="answer">
                <div class="german">{{full_d}}</div>
                {{base_a}}
                {{#s1}}<br><div class="example">{{s1}}</div>{{/s1}}
                {{#s1e}}<div class="example-en">{{s1e}}</div>{{/s1e}}
                {{#s2}}<br><div class="example">{{s2}}</div>{{/s2}}
                {{#s2e}}<div class="example-en">{{s2e}}</div>{{/s2e}}
                {{#s3}}<br><div class="example">{{s3}}</div>{{/s3}}
                {{#s3e}}<div class="example-en">{{s3e}}</div>{{/s3e}}
                ''',
            }
        ],
        css='''
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
        .english {
            font-size: 18px;
            color: #A23B72;
        }
        .example {
            font-size: 14px;
            font-style: italic;
            color: #666;
            margin-top: 10px;
        }
        .example-en {
            font-size: 14px;
            font-style: italic;
            color: #999;
        }
        '''
    )

    # Create genanki deck
    anki_deck = genanki.Deck(
        2059400110,  # Deck ID
        deck.name or "DTZ Goethe B1 Vocabulary"
    )

    # Convert our cards to genanki notes
    for card in deck.cards:
        note = genanki.Note(
            model=model,
            fields=[
                card.full_d,
                card.base_e,
                card.base_d,
                card.artikel_d,
                card.plural_d,
                card.audio_text_d,
                card.s1,
                card.s1e,
                card.s2,
                card.s2e,
                card.s3,
                card.s3e,
                card.s4,
                card.s4e,
                card.s5,
                card.s5e,
                card.s6,
                card.s6e,
                card.s7,
                card.s7e,
                card.s8,
                card.s8e,
                card.s9,
                card.s9e,
                card.original_order,
                card.base_a,
                card.s1a,
                card.s2a,
                card.s3a,
                card.s4a,
                card.s5a,
                card.s6a,
                card.s7a,
                card.s8a,
                card.s9a,
            ]
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