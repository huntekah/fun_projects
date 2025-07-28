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


def _map_fields_to_schema(raw_fields_dict: Dict[str, Any], note_id: int, model_id: int) -> Dict[str, Any]:
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
        # Only print once per deck, not per card
        pass
        return {
            "note_id": note_id,
            "model_id": model_id,
            "original_guid": raw_fields_dict.get("original_guid", ""),
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
            "original_order": raw_fields_dict.get("original_order", ""),
        }
    elif has_old_fields:
        # Old scheme (original deck) - need to map to new schema
        # Only print once per deck, not per card
        pass
        return {
            "note_id": note_id,
            "model_id": model_id,
            "original_guid": raw_fields_dict.get("original_guid", ""),
            # Map old field names to new schema field names
            "full_source": raw_fields_dict.get("full_d", ""),
            "base_source": raw_fields_dict.get("base_d", ""),
            "base_target": raw_fields_dict.get("base_e", ""),
            # German-specific fields (keep same names)
            "artikel_d": raw_fields_dict.get("artikel_d", ""),
            "plural_d": raw_fields_dict.get("plural_d", ""),
            "audio_text_d": raw_fields_dict.get("audio_text_d", ""),
            # Map sentence fields
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
            # Map audio fields
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
            # Metadata
            "original_order": raw_fields_dict.get("original_order", ""),
        }
    else:
        # Fallback - try both schemes and use default values
        print(f"  ⚠️  Could not detect field naming scheme - using fallback mapping")
        return {
            "note_id": note_id,
            "model_id": model_id,
            # Try both old and new field names, fallback to empty
            "full_source": raw_fields_dict.get("full_source", raw_fields_dict.get("full_d", "")),
            "base_source": raw_fields_dict.get("base_source", raw_fields_dict.get("base_d", "")),
            "base_target": raw_fields_dict.get("base_target", raw_fields_dict.get("base_e", "")),
            "artikel_d": raw_fields_dict.get("artikel_d", ""),
            "plural_d": raw_fields_dict.get("plural_d", ""),
            "audio_text_d": raw_fields_dict.get("audio_text_d", ""),
            "s1_source": raw_fields_dict.get("s1_source", raw_fields_dict.get("s1", "")),
            "s1_target": raw_fields_dict.get("s1_target", raw_fields_dict.get("s1e", "")),
            "s2_source": raw_fields_dict.get("s2_source", raw_fields_dict.get("s2", "")),
            "s2_target": raw_fields_dict.get("s2_target", raw_fields_dict.get("s2e", "")),
            "s3_source": raw_fields_dict.get("s3_source", raw_fields_dict.get("s3", "")),
            "s3_target": raw_fields_dict.get("s3_target", raw_fields_dict.get("s3e", "")),
            "s4_source": raw_fields_dict.get("s4_source", raw_fields_dict.get("s4", "")),
            "s4_target": raw_fields_dict.get("s4_target", raw_fields_dict.get("s4e", "")),
            "s5_source": raw_fields_dict.get("s5_source", raw_fields_dict.get("s5", "")),
            "s5_target": raw_fields_dict.get("s5_target", raw_fields_dict.get("s5e", "")),
            "s6_source": raw_fields_dict.get("s6_source", raw_fields_dict.get("s6", "")),
            "s6_target": raw_fields_dict.get("s6_target", raw_fields_dict.get("s6e", "")),
            "s7_source": raw_fields_dict.get("s7_source", raw_fields_dict.get("s7", "")),
            "s7_target": raw_fields_dict.get("s7_target", raw_fields_dict.get("s7e", "")),
            "s8_source": raw_fields_dict.get("s8_source", raw_fields_dict.get("s8", "")),
            "s8_target": raw_fields_dict.get("s8_target", raw_fields_dict.get("s8e", "")),
            "s9_source": raw_fields_dict.get("s9_source", raw_fields_dict.get("s9", "")),
            "s9_target": raw_fields_dict.get("s9_target", raw_fields_dict.get("s9e", "")),
            "base_audio": raw_fields_dict.get("base_audio", raw_fields_dict.get("base_a", "")),
            "s1_audio": raw_fields_dict.get("s1_audio", raw_fields_dict.get("s1a", "")),
            "s2_audio": raw_fields_dict.get("s2_audio", raw_fields_dict.get("s2a", "")),
            "s3_audio": raw_fields_dict.get("s3_audio", raw_fields_dict.get("s3a", "")),
            "s4_audio": raw_fields_dict.get("s4_audio", raw_fields_dict.get("s4a", "")),
            "s5_audio": raw_fields_dict.get("s5_audio", raw_fields_dict.get("s5a", "")),
            "s6_audio": raw_fields_dict.get("s6_audio", raw_fields_dict.get("s6a", "")),
            "s7_audio": raw_fields_dict.get("s7_audio", raw_fields_dict.get("s7a", "")),
            "s8_audio": raw_fields_dict.get("s8_audio", raw_fields_dict.get("s8a", "")),
            "s9_audio": raw_fields_dict.get("s9_audio", raw_fields_dict.get("s9a", "")),
            "original_order": raw_fields_dict.get("original_order", ""),
        }


def load_anki_deck(path: Path) -> AnkiDeck:
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
                raise FileNotFoundError(f"collection.anki2 not found in .apkg file")

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
                                print(f"  📋 Detected new field naming scheme (full_source, base_target, etc.)")
                            elif has_old_fields:
                                print(f"  📋 Detected old field naming scheme (full_d, base_e, etc.) - mapping to new schema")
                            else:
                                print(f"  ⚠️  Could not detect field naming scheme - using fallback mapping")
                            field_scheme_detected = True
                        
                        mapped_fields = _map_fields_to_schema(raw_fields_dict, note_id, model_id)

                        # Create AnkiCard instance with mapped fields
                        card = AnkiCard(**mapped_fields)
                        cards.append(card)
                        
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to parse note {note_id} (#{note_idx+1}): {e}")
                        continue

            finally:
                conn.close()

        print(f"✅ Successfully loaded {len(cards)} cards")
        return AnkiDeck(cards=cards, name=deck_name, total_cards=len(cards))
        
    except Exception as e:
        print(f"\n❌ ERROR loading Anki deck from {path}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\n🔍 Full traceback:")
        traceback.print_exc()
        print("-" * 80)
        raise


def save_anki_deck(
    deck: AnkiDeck, output_path: Path, original_apkg_path: Path = None
) -> None:
    """
    Save an AnkiDeck to a .apkg file using genanki.

    Args:
        deck: The AnkiDeck to save
        output_path: Path where to save the deck (.apkg format)
        original_apkg_path: Optional path to original .apkg file to extract media files
    """
    import traceback
    
    try:
        print(f"💾 Saving deck to: {output_path}")
        
        if not deck.cards:
            raise ValueError("Cannot save empty deck - no cards provided")
            
        if not str(output_path).endswith('.apkg'):
            print(f"⚠️  Warning: Output path doesn't end with .apkg: {output_path}")
            
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📋 Creating genanki model and deck structure...")
        
        # Create genanki model that matches our card structure
        try:
            model = genanki.Model(
                1607392319,  # Model ID
                "DTZ Goethe B1 German-Polish Model",
                fields=DTZ_MODEL_FIELDS,
                templates=DTZ_CARD_TEMPLATES,
                css=DTZ_CARD_CSS,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create genanki model: {e}")

        # Create genanki deck
        try:
            anki_deck = genanki.Deck(
                2059400110,  # Deck ID
                deck.name or "DTZ Goethe B1 Vocabulary",
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create genanki deck: {e}")

        print(f"🃏 Converting {len(deck.cards)} cards to genanki notes...")
        
        # Convert our cards to genanki notes
        failed_cards = 0
        for card_idx, card in enumerate(deck.cards):
            try:
                # Ensure all fields are strings and handle None/empty values
                fields = [
                    str(card.full_source or ""),
                    str(card.base_target or ""),
                    str(card.base_source or ""),
                    str(card.artikel_d or ""),
                    str(card.plural_d or ""),
                    str(card.audio_text_d or ""),
                    str(card.s1_source or ""),
                    str(card.s1_target or ""),
                    str(card.s2_source or ""),
                    str(card.s2_target or ""),
                    str(card.s3_source or ""),
                    str(card.s3_target or ""),
                    str(card.s4_source or ""),
                    str(card.s4_target or ""),
                    str(card.s5_source or ""),
                    str(card.s5_target or ""),
                    str(card.s6_source or ""),
                    str(card.s6_target or ""),
                    str(card.s7_source or ""),
                    str(card.s7_target or ""),
                    str(card.s8_source or ""),
                    str(card.s8_target or ""),
                    str(card.s9_source or ""),
                    str(card.s9_target or ""),
                    str(card.original_order or ""),
                    str(card.base_audio or ""),
                    str(card.s1_audio or ""),
                    str(card.s2_audio or ""),
                    str(card.s3_audio or ""),
                    str(card.s4_audio or ""),
                    str(card.s5_audio or ""),
                    str(card.s6_audio or ""),
                    str(card.s7_audio or ""),
                    str(card.s8_audio or ""),
                    str(card.s9_audio or ""),
                ]

                # Preserve original GUID to maintain study progress
                note = genanki.Note(
                    model=model, 
                    fields=fields,
                    guid=card.original_guid or str(card.note_id)  # Use original GUID to preserve progress
                )
                anki_deck.add_note(note)
                
            except Exception as e:
                failed_cards += 1
                print(f"⚠️  Warning: Failed to convert card {card_idx+1} (note_id={getattr(card, 'note_id', 'unknown')}): {e}")
                continue

        if failed_cards > 0:
            print(f"⚠️  {failed_cards} cards failed to convert and were skipped")

        # Extract media files from original .apkg if provided
        media_files = []
        if original_apkg_path and original_apkg_path.exists():
            print(f"🎵 Extracting media files from original deck...")
            media_files = _extract_media_files(original_apkg_path)
            print(f"  Found {len(media_files)} media files")

        # Generate the .apkg file
        print(f"📦 Generating .apkg file...")
        try:
            genanki.Package(anki_deck, media_files=media_files).write_to_file(str(output_path))
        except Exception as e:
            raise RuntimeError(f"Failed to write .apkg file: {e}")

        # Verify file was created
        if not output_path.exists():
            raise RuntimeError("Output file was not created successfully")
            
        file_size = output_path.stat().st_size
        print(f"✅ Successfully saved {len(deck.cards) - failed_cards} cards to {output_path}")
        print(f"   File size: {file_size / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"\n❌ ERROR saving Anki deck to {output_path}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\n🔍 Full traceback:")
        traceback.print_exc()
        print("-" * 80)
        raise


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


def copy_non_translation_fields_from_original(translated_card: AnkiCard, original_card: AnkiCard, verbose: bool = True) -> tuple[AnkiCard, int]:
    """
    Copy non-translation fields from original card to fix LLM hallucinations.
    
    LLMs sometimes output 'string' or other garbage in fields that should be copied unchanged.
    This function preserves original values for metadata and audio fields.
    
    Args:
        translated_card: Card returned by LLM with potential hallucinations
        original_card: Original card with correct metadata
        verbose: Whether to print cleaning details
        
    Returns:
        tuple[AnkiCard, int]: Cleaned card with proper field values, number of issues fixed
    """
    import traceback
    
    try:
        if verbose:
            print(f"🧹 Cleaning translated card {translated_card.note_id}...")
        
        # Create a copy to avoid modifying the original
        cleaned_card = translated_card.model_copy()
        
        # Fields that should NEVER be translated (preserve original values)
        metadata_fields = [
            'note_id', 'model_id', 'original_order'
        ]
        
        # German-specific fields that should remain unchanged
        german_fields = [
            'full_source', 'base_source', 'artikel_d', 'plural_d', 'audio_text_d',
            's1_source', 's2_source', 's3_source', 's4_source', 's5_source',
            's6_source', 's7_source', 's8_source', 's9_source'
        ]
        
        # Audio fields that should be copied from original
        audio_fields = [
            'base_audio', 's1_audio', 's2_audio', 's3_audio', 's4_audio',
            's5_audio', 's6_audio', 's7_audio', 's8_audio', 's9_audio'
        ]
        
        # Copy metadata fields (these should never change)
        for field in metadata_fields:
            original_value = getattr(original_card, field, "")
            setattr(cleaned_card, field, original_value)
        
        # Copy German-specific fields (source language should never change)
        for field in german_fields:
            original_value = getattr(original_card, field, "")
            setattr(cleaned_card, field, original_value)
        
        # Copy audio fields (these are technical metadata, not translations)
        issues_found = []
        for field in audio_fields:
            original_value = getattr(original_card, field, "")
            translated_value = getattr(translated_card, field, "")
            
            # Check for LLM hallucinations in audio fields
            if translated_value and translated_value.lower() in ['string', 'none', 'null', 'empty', '""', "''", 'undefined']:
                issues_found.append(f"{field}: '{translated_value}' → '{original_value}'")
                setattr(cleaned_card, field, original_value)
            elif translated_value != original_value and original_value:
                # If LLM changed an audio field that had a value, restore original
                issues_found.append(f"{field}: '{translated_value}' → '{original_value}' (restored)")
                setattr(cleaned_card, field, original_value)
            else:
                # Keep original value
                setattr(cleaned_card, field, original_value)
        
        # Handle empty target fields (if LLM left translations empty, that's probably wrong)
        target_fields = [
            'base_target', 's1_target', 's2_target', 's3_target', 's4_target',
            's5_target', 's6_target', 's7_target', 's8_target', 's9_target'
        ]
        
        empty_translations = []
        for field in target_fields:
            original_source_field = field.replace('_target', '_source')
            original_source_value = getattr(original_card, original_source_field, "")
            translated_value = getattr(translated_card, field, "")
            
            # If source has content but translation is empty, that's suspicious
            if original_source_value.strip() and not translated_value.strip():
                empty_translations.append(f"{field} (source: '{original_source_value[:30]}...')")
        
        total_issues = len(issues_found)
        
        if verbose:
            if issues_found:
                print(f"  ⚠️  Fixed {len(issues_found)} LLM hallucinations:")
                for issue in issues_found[:3]:  # Show first 3 issues
                    print(f"    - {issue}")
                if len(issues_found) > 3:
                    print(f"    - ... and {len(issues_found) - 3} more")
            
            if empty_translations:
                print(f"  ⚠️  Found {len(empty_translations)} empty translations:")
                for empty in empty_translations[:2]:  # Show first 2
                    print(f"    - {empty}")
                if len(empty_translations) > 2:
                    print(f"    - ... and {len(empty_translations) - 2} more")
            
            if not issues_found and not empty_translations:
                print(f"  ✅ No issues found - card is clean")
        
        return cleaned_card, total_issues
        
    except Exception as e:
        print(f"\n❌ ERROR cleaning translated card:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\n🔍 Full traceback:")
        traceback.print_exc()
        print("-" * 80)
        
        # Return original translated card if cleaning fails
        return translated_card, 0
