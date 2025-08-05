import sqlite3
import zipfile
import tempfile
import os
import json
import genanki
from pathlib import Path
from typing import Dict, Any, List

from ..domain.models import AnkiCard, AnkiDeck


class APKGHandler:
    """Handler for Anki package (.apkg) file operations."""
    
    def __init__(self):
        """Initialize the APKG handler."""
        pass
    
    def _map_fields_to_schema(self, raw_fields_dict: Dict[str, Any], note_id: int, model_id: int) -> Dict[str, Any]:
        """
        Map raw field names to AnkiCard schema, handling both old and new naming schemes.
        
        Old scheme (original DE-EN deck): full_d, base_d, base_e, s1, s1e, base_a, s1a, etc.
        New scheme (translated DE-PL deck): full_source, base_source, base_target, s1_source, s1_target, base_audio, s1_audio, etc.
        
        Args:
            raw_fields_dict: Dictionary of field_name -> value from .apkg file
            note_id: Note ID
            model_id: Model ID
            
        Returns:
            Dictionary with AnkiCard schema field names
        """
        # Detect which naming scheme is used by checking for key fields
        has_old_fields = any(field in raw_fields_dict for field in ['full_d', 'base_d', 'base_e'])
        has_new_fields = any(field in raw_fields_dict for field in ['full_source', 'base_source', 'base_target'])
        
        if has_new_fields and not has_old_fields:
            # New scheme (translated deck) - direct mapping
            return {
                "note_id": note_id,
                "model_id": model_id,
                "original_guid": raw_fields_dict.get("original_guid", ""),
                "frequency_rank": raw_fields_dict.get("frequency_rank", ""),
                # Direct mapping for new scheme
                "full_source": raw_fields_dict.get("full_source", ""),
                "base_source": raw_fields_dict.get("base_source", ""),
                "base_target": raw_fields_dict.get("base_target", ""),
                "artikel_d": raw_fields_dict.get("artikel_d", ""),
                "plural_d": raw_fields_dict.get("plural_d", ""),
                "audio_text_d": raw_fields_dict.get("audio_text_d", ""),
                "s1_source": raw_fields_dict.get("s1_source", ""),
                "s1_target": raw_fields_dict.get("s1_target", ""),
                "s2_source": raw_fields_dict.get("s2_source", ""),
                "s2_target": raw_fields_dict.get("s2_target", ""),
                "s3_source": raw_fields_dict.get("s3_source", ""),
                "s3_target": raw_fields_dict.get("s3_target", ""),
                "s4_source": raw_fields_dict.get("s4_source", ""),
                "s4_target": raw_fields_dict.get("s4_target", ""),
                "s5_source": raw_fields_dict.get("s5_source", ""),
                "s5_target": raw_fields_dict.get("s5_target", ""),
                "s6_source": raw_fields_dict.get("s6_source", ""),
                "s6_target": raw_fields_dict.get("s6_target", ""),
                "s7_source": raw_fields_dict.get("s7_source", ""),
                "s7_target": raw_fields_dict.get("s7_target", ""),
                "s8_source": raw_fields_dict.get("s8_source", ""),
                "s8_target": raw_fields_dict.get("s8_target", ""),
                "s9_source": raw_fields_dict.get("s9_source", ""),
                "s9_target": raw_fields_dict.get("s9_target", ""),
                "base_audio": raw_fields_dict.get("base_audio", ""),
                "s1_audio": raw_fields_dict.get("s1_audio", ""),
                "s2_audio": raw_fields_dict.get("s2_audio", ""),
                "s3_audio": raw_fields_dict.get("s3_audio", ""),
                "s4_audio": raw_fields_dict.get("s4_audio", ""),
                "s5_audio": raw_fields_dict.get("s5_audio", ""),
                "s6_audio": raw_fields_dict.get("s6_audio", ""),
                "s7_audio": raw_fields_dict.get("s7_audio", ""),
                "s8_audio": raw_fields_dict.get("s8_audio", ""),
                "s9_audio": raw_fields_dict.get("s9_audio", ""),
                "base_target_audio": raw_fields_dict.get("base_target_audio", ""),
                "s1_target_audio": raw_fields_dict.get("s1_target_audio", ""),
                "s2_target_audio": raw_fields_dict.get("s2_target_audio", ""),
                "s3_target_audio": raw_fields_dict.get("s3_target_audio", ""),
                "s4_target_audio": raw_fields_dict.get("s4_target_audio", ""),
                "s5_target_audio": raw_fields_dict.get("s5_target_audio", ""),
                "s6_target_audio": raw_fields_dict.get("s6_target_audio", ""),
                "s7_target_audio": raw_fields_dict.get("s7_target_audio", ""),
                "s8_target_audio": raw_fields_dict.get("s8_target_audio", ""),
                "s9_target_audio": raw_fields_dict.get("s9_target_audio", ""),
                "original_order": raw_fields_dict.get("original_order", ""),
            }
        elif has_old_fields:
            # Old scheme (original deck) - need to map to new schema
            return {
                "note_id": note_id,
                "model_id": model_id,
                "original_guid": raw_fields_dict.get("original_guid", ""),
                "frequency_rank": raw_fields_dict.get("frequency_rank", ""),
                # Map old field names to new schema
                "full_source": raw_fields_dict.get("full_d", ""),
                "base_source": raw_fields_dict.get("base_d", ""),
                "base_target": raw_fields_dict.get("base_e", ""),  # English in original
                "artikel_d": raw_fields_dict.get("artikel_d", ""),
                "plural_d": raw_fields_dict.get("plural_d", ""),
                "audio_text_d": raw_fields_dict.get("audio_text_d", ""),
                "s1_source": raw_fields_dict.get("s1", ""),
                "s1_target": raw_fields_dict.get("s1e", ""),
                "s2_source": raw_fields_dict.get("s2", ""),
                "s2_target": raw_fields_dict.get("s2e", ""),
                "s3_source": raw_fields_dict.get("s3", ""),
                "s3_target": raw_fields_dict.get("s3e", ""),
                "s4_source": raw_fields_dict.get("s4", ""),
                "s4_target": raw_fields_dict.get("s4e", ""),
                "s5_source": raw_fields_dict.get("s5", ""),
                "s5_target": raw_fields_dict.get("s5e", ""),
                "s6_source": raw_fields_dict.get("s6", ""),
                "s6_target": raw_fields_dict.get("s6e", ""),
                "s7_source": raw_fields_dict.get("s7", ""),
                "s7_target": raw_fields_dict.get("s7e", ""),
                "s8_source": raw_fields_dict.get("s8", ""),
                "s8_target": raw_fields_dict.get("s8e", ""),
                "s9_source": raw_fields_dict.get("s9", ""),
                "s9_target": raw_fields_dict.get("s9e", ""),
                "base_audio": raw_fields_dict.get("base_a", ""),
                "s1_audio": raw_fields_dict.get("s1a", ""),
                "s2_audio": raw_fields_dict.get("s2a", ""),
                "s3_audio": raw_fields_dict.get("s3a", ""),
                "s4_audio": raw_fields_dict.get("s4a", ""),
                "s5_audio": raw_fields_dict.get("s5a", ""),
                "s6_audio": raw_fields_dict.get("s6a", ""),
                "s7_audio": raw_fields_dict.get("s7a", ""),
                "s8_audio": raw_fields_dict.get("s8a", ""),
                "s9_audio": raw_fields_dict.get("s9a", ""),
                "base_target_audio": raw_fields_dict.get("base_target_audio", ""),
                "s1_target_audio": raw_fields_dict.get("s1_target_audio", ""),
                "s2_target_audio": raw_fields_dict.get("s2_target_audio", ""),
                "s3_target_audio": raw_fields_dict.get("s3_target_audio", ""),
                "s4_target_audio": raw_fields_dict.get("s4_target_audio", ""),
                "s5_target_audio": raw_fields_dict.get("s5_target_audio", ""),
                "s6_target_audio": raw_fields_dict.get("s6_target_audio", ""),
                "s7_target_audio": raw_fields_dict.get("s7_target_audio", ""),
                "s8_target_audio": raw_fields_dict.get("s8_target_audio", ""),
                "s9_target_audio": raw_fields_dict.get("s9_target_audio", ""),
                "original_order": raw_fields_dict.get("original_order", ""),
            }
        else:
            # Fallback - treat as new scheme but with empty defaults
            return {
                "note_id": note_id,
                "model_id": model_id,
                "original_guid": raw_fields_dict.get("original_guid", ""),
                "frequency_rank": raw_fields_dict.get("frequency_rank", ""),
                "full_source": raw_fields_dict.get("full_source", ""),
                "base_source": raw_fields_dict.get("base_source", ""),
                "base_target": raw_fields_dict.get("base_target", ""),
                "artikel_d": raw_fields_dict.get("artikel_d", ""),
                "plural_d": raw_fields_dict.get("plural_d", ""),
                "audio_text_d": raw_fields_dict.get("audio_text_d", ""),
                "s1_source": raw_fields_dict.get("s1_source", ""),
                "s1_target": raw_fields_dict.get("s1_target", ""),
                "s2_source": raw_fields_dict.get("s2_source", ""),
                "s2_target": raw_fields_dict.get("s2_target", ""),
                "s3_source": raw_fields_dict.get("s3_source", ""),
                "s3_target": raw_fields_dict.get("s3_target", ""),
                "s4_source": raw_fields_dict.get("s4_source", ""),
                "s4_target": raw_fields_dict.get("s4_target", ""),
                "s5_source": raw_fields_dict.get("s5_source", ""),
                "s5_target": raw_fields_dict.get("s5_target", ""),
                "s6_source": raw_fields_dict.get("s6_source", ""),
                "s6_target": raw_fields_dict.get("s6_target", ""),
                "s7_source": raw_fields_dict.get("s7_source", ""),
                "s7_target": raw_fields_dict.get("s7_target", ""),
                "s8_source": raw_fields_dict.get("s8_source", ""),
                "s8_target": raw_fields_dict.get("s8_target", ""),
                "s9_source": raw_fields_dict.get("s9_source", ""),
                "s9_target": raw_fields_dict.get("s9_target", ""),
                "base_audio": raw_fields_dict.get("base_audio", ""),
                "s1_audio": raw_fields_dict.get("s1_audio", ""),
                "s2_audio": raw_fields_dict.get("s2_audio", ""),
                "s3_audio": raw_fields_dict.get("s3_audio", ""),
                "s4_audio": raw_fields_dict.get("s4_audio", ""),
                "s5_audio": raw_fields_dict.get("s5_audio", ""),
                "s6_audio": raw_fields_dict.get("s6_audio", ""),
                "s7_audio": raw_fields_dict.get("s7_audio", ""),
                "s8_audio": raw_fields_dict.get("s8_audio", ""),
                "s9_audio": raw_fields_dict.get("s9_audio", ""),
                "base_target_audio": raw_fields_dict.get("base_target_audio", ""),
                "s1_target_audio": raw_fields_dict.get("s1_target_audio", ""),
                "s2_target_audio": raw_fields_dict.get("s2_target_audio", ""),
                "s3_target_audio": raw_fields_dict.get("s3_target_audio", ""),
                "s4_target_audio": raw_fields_dict.get("s4_target_audio", ""),
                "s5_target_audio": raw_fields_dict.get("s5_target_audio", ""),
                "s6_target_audio": raw_fields_dict.get("s6_target_audio", ""),
                "s7_target_audio": raw_fields_dict.get("s7_target_audio", ""),
                "s8_target_audio": raw_fields_dict.get("s8_target_audio", ""),
                "s9_target_audio": raw_fields_dict.get("s9_target_audio", ""),
                "original_order": raw_fields_dict.get("original_order", ""),
            }
    
    def load_deck(self, path: Path) -> AnkiDeck:
        """
        Load an Anki deck from a .apkg file.

        Args:
            path: Path to the .apkg file

        Returns:
            AnkiDeck: Parsed deck with all cards
        """
        import traceback
        
        try:
            print(f"🔍 Loading deck from: {path}")
            
            if not path.exists():
                raise FileNotFoundError(f"Anki deck file not found: {path}")
            
            if not path.suffix.lower() == '.apkg':
                raise ValueError(f"Expected .apkg file, got: {path.suffix}")
                
            cards = []
            deck_name = path.stem

            with tempfile.TemporaryDirectory() as tmpdir:
                print(f"📂 Extracting .apkg to temp dir: {tmpdir}")
                
                # Unzip the .apkg file
                try:
                    with zipfile.ZipFile(path, "r") as z:
                        z.extractall(tmpdir)
                except zipfile.BadZipFile as e:
                    raise ValueError(f"Invalid .apkg file (corrupted zip): {e}")

                # Path to the SQLite database
                db_path = os.path.join(tmpdir, "collection.anki2")
                
                if not os.path.exists(db_path):
                    raise FileNotFoundError("collection.anki2 not found in .apkg file")

                print(f"🗄️  Connecting to SQLite database: {db_path}")
                
                # Connect to the SQLite database
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                except sqlite3.Error as e:
                    raise RuntimeError(f"Failed to connect to SQLite database: {e}")

                try:
                    # Get field names from models
                    print("📋 Reading card models and field definitions...")
                    cursor.execute("SELECT models FROM col")
                    models_result = cursor.fetchone()
                    if not models_result:
                        raise RuntimeError("No models found in collection")
                    
                    models_json = models_result[0]
                    models = json.loads(models_json)

                    # Create a mapping of model_id to field names
                    model_fields = {}
                    for model_id, model in models.items():
                        field_names = [field["name"] for field in model["flds"]]
                        model_fields[int(model_id)] = field_names
                        print(f"  Model {model_id}: {len(field_names)} fields")

                    # Get the note and card information
                    print("🃏 Reading notes and cards...")
                    cursor.execute("SELECT id, mid, flds, guid FROM notes")
                    notes = cursor.fetchall()
                    print(f"  Found {len(notes)} notes")

                    # The 'flds' column contains the fields of a note joined by a special character
                    # We can split this to get individual fields.
                    field_scheme_detected = False
                    for note_idx, (note_id, model_id, flds, guid) in enumerate(notes):
                        try:
                            fields = flds.split("\x1f")
                            field_names = model_fields.get(model_id, [])

                            # Create a dictionary mapping old field names to values
                            raw_fields_dict = {"note_id": note_id, "model_id": model_id, "original_guid": guid}
                            for i, field_value in enumerate(fields):
                                field_name = field_names[i] if i < len(field_names) else f"field_{i}"
                                raw_fields_dict[field_name] = field_value

                            # Detect field naming scheme and map accordingly (only print detection once)
                            if not field_scheme_detected:
                                has_old_fields = any(field in raw_fields_dict for field in ['full_d', 'base_d', 'base_e'])
                                has_new_fields = any(field in raw_fields_dict for field in ['full_source', 'base_source', 'base_target'])
                                if has_new_fields and not has_old_fields:
                                    print("  📋 Detected new field naming scheme (full_source, base_target, etc.)")
                                elif has_old_fields:
                                    print("  📋 Detected old field naming scheme (full_d, base_e, etc.) - mapping to new schema")
                                else:
                                    print("  ⚠️  Could not detect field naming scheme - using fallback mapping")
                                field_scheme_detected = True
                            
                            mapped_fields = self._map_fields_to_schema(raw_fields_dict, note_id, model_id)

                            # Create the AnkiCard object
                            card = AnkiCard(**mapped_fields)
                            cards.append(card)
                            
                        except Exception as e:
                            print(f"⚠️  Error processing note {note_id}: {e}")
                            traceback.print_exc()
                            continue

                    conn.close()
                    print(f"✅ Successfully loaded {len(cards)} cards from {deck_name}")

                except sqlite3.Error as e:
                    conn.close()
                    raise RuntimeError(f"Database error: {e}")
                except Exception as e:
                    conn.close()
                    raise RuntimeError(f"Error reading database: {e}")

            # Create and return the deck
            deck = AnkiDeck(cards=cards, name=deck_name)
            deck.total_cards = len(cards)
            return deck

        except Exception as e:
            print(f"❌ Failed to load deck from {path}: {e}")
            traceback.print_exc()
            raise
    
    def extract_media_files(self, apkg_path: Path) -> List[str]:
        """
        Extract and list media files from an .apkg file.
        
        Args:
            apkg_path: Path to the .apkg file
            
        Returns:
            List of media filenames found in the package
        """
        media_files = []
        
        try:
            with zipfile.ZipFile(apkg_path, 'r') as zip_file:
                for file_info in zip_file.infolist():
                    if not file_info.filename.startswith('_') and file_info.filename != 'collection.anki2':
                        if file_info.filename.lower().endswith(('.mp3', '.wav', '.ogg', '.jpg', '.png', '.gif')):
                            media_files.append(file_info.filename)
            
            print(f"📁 Found {len(media_files)} media files in {apkg_path.name}")
            return media_files
            
        except Exception as e:
            print(f"⚠️  Error extracting media files from {apkg_path}: {e}")
            return []