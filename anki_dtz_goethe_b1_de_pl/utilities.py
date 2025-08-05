import sqlite3
import zipfile
import tempfile
import os
import json
import genanki
from pathlib import Path
from typing import Dict, Any, List
from schema import AnkiCard, AnkiDeck
from card_templates import (
    DTZ_MODEL_FIELDS, DTZ_CARD_TEMPLATES, DTZ_CARD_CSS,
    DTZ_RECOGNITION_TEMPLATES, DTZ_PRODUCTION_TEMPLATES, 
    DTZ_LISTENING_TEMPLATES, DTZ_SENTENCE_PRODUCTION_TEMPLATES
)


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
        # Only print once per deck, not per card
        pass
        return {
            "note_id": note_id,
            "model_id": model_id,
            "original_guid": raw_fields_dict.get("original_guid", ""),
            "frequency_rank": raw_fields_dict.get("frequency_rank", ""),
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
            # Polish audio fields don't exist in old scheme - default to empty
            "base_target_audio": "",
            "s1_target_audio": "",
            "s2_target_audio": "",
            "s3_target_audio": "",
            "s4_target_audio": "",
            "s5_target_audio": "",
            "s6_target_audio": "",
            "s7_target_audio": "",
            "s8_target_audio": "",
            "s9_target_audio": "",
            # Metadata
            "original_order": raw_fields_dict.get("original_order", ""),
        }
    else:
        # Fallback - try both schemes and use default values
        print("  ⚠️  Could not detect field naming scheme - using fallback mapping")
        return {
            "note_id": note_id,
            "model_id": model_id,
            "frequency_rank": raw_fields_dict.get("frequency_rank", ""),
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
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        print("-" * 80)
        raise


def save_anki_deck_4subdecks(
    deck: AnkiDeck, output_path: Path, original_apkg_path: Path | None = None, additional_media_dir: Path | None = None
) -> None:
    """
    Save an AnkiDeck to a .apkg file using 4 separate subdecks with proper genanki deck assignment.
    
    This function creates separate notes for each subdeck type to ensure cards appear in the correct
    subdeck. This solves the genanki limitation where template-based deck assignment doesn't work.

    Args:
        deck: AnkiDeck to save
        output_path: Path for the output .apkg file
        original_apkg_path: Optional path to original .apkg for media extraction
        additional_media_dir: Optional directory containing new media files (e.g., TTS audio)
    """
    import traceback
    
    try:
        print(f"💾 Saving 4-subdeck structure to: {output_path}")
        
        if not deck.cards:
            raise ValueError("Cannot save empty deck - no cards provided")
            
        if not str(output_path).endswith('.apkg'):
            print(f"⚠️  Warning: Output path doesn't end with .apkg: {output_path}")
            
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print("📋 Creating separate genanki models for each subdeck...")
        
        # Import deck IDs from card templates
        from card_templates import DECK_ID_MAIN, DECK_ID_RECOGNITION, DECK_ID_PRODUCTION, DECK_ID_LISTENING, DECK_ID_SENTENCE_PROD
        
        # Create separate models for each card type
        recognition_model = genanki.Model(
            1607392320,  # Recognition Model ID
            "DTZ German-Polish Recognition",
            fields=DTZ_MODEL_FIELDS,
            templates=DTZ_RECOGNITION_TEMPLATES,
            css=DTZ_CARD_CSS,
        )
        
        production_model = genanki.Model(
            1607392321,  # Production Model ID
            "DTZ German-Polish Production", 
            fields=DTZ_MODEL_FIELDS,
            templates=DTZ_PRODUCTION_TEMPLATES,
            css=DTZ_CARD_CSS,
        )
        
        listening_model = genanki.Model(
            1607392322,  # Listening Model ID
            "DTZ German-Polish Listening",
            fields=DTZ_MODEL_FIELDS,
            templates=DTZ_LISTENING_TEMPLATES,
            css=DTZ_CARD_CSS,
        )
        
        sentence_production_model = genanki.Model(
            1607392323,  # Sentence Production Model ID
            "DTZ German-Polish Sentence Production",
            fields=DTZ_MODEL_FIELDS,
            templates=DTZ_SENTENCE_PRODUCTION_TEMPLATES,
            css=DTZ_CARD_CSS,
        )
        
        # Create parent deck and subdecks
        try:
            # Main parent deck
            parent_deck = genanki.Deck(
                DECK_ID_MAIN,
                "DTZ Goethe B1 German-Polish 4-Subdeck",
            )
            
            # 01 Recognition subdeck (German → Polish)
            recognition_deck = genanki.Deck(
                DECK_ID_RECOGNITION,
                "DTZ Goethe B1 German-Polish 4-Subdeck::01 Recognition",
            )
            
            # 02 Production subdeck (Polish → German)  
            production_deck = genanki.Deck(
                DECK_ID_PRODUCTION,
                "DTZ Goethe B1 German-Polish 4-Subdeck::02 Production",
            )
            
            # 03 Listening Comprehension subdeck (Audio → Text)
            listening_deck = genanki.Deck(
                DECK_ID_LISTENING,
                "DTZ Goethe B1 German-Polish 4-Subdeck::03 Listening Comprehension",
            )
            
            # 04 Sentence Production subdeck (Polish → German sentences)
            sentence_prod_deck = genanki.Deck(
                DECK_ID_SENTENCE_PROD,
                "DTZ Goethe B1 German-Polish 4-Subdeck::04 Sentence Production",
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to create genanki decks: {e}")

        print(f"🃏 Converting {len(deck.cards)} cards to 4-subdeck notes...")
        
        # Convert cards to separate notes for each subdeck
        failed_cards = 0
        for card_idx, card in enumerate(deck.cards):
            try:
                # Prepare field values (same for all note types)
                fields = [
                    str(getattr(card, 'frequency_rank', '') or ""),
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
                    str(getattr(card, 'full_source_audio', '') or ""),
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
                    str(getattr(card, 'base_target_audio', '') or ""),
                    str(getattr(card, 's1_target_audio', '') or ""),
                    str(getattr(card, 's2_target_audio', '') or ""),
                    str(getattr(card, 's3_target_audio', '') or ""),
                    str(getattr(card, 's4_target_audio', '') or ""),
                    str(getattr(card, 's5_target_audio', '') or ""),
                    str(getattr(card, 's6_target_audio', '') or ""),
                    str(getattr(card, 's7_target_audio', '') or ""),
                    str(getattr(card, 's8_target_audio', '') or ""),
                    str(getattr(card, 's9_target_audio', '') or ""),
                ]

                base_guid = card.original_guid or str(card.note_id)
                
                # 1. Recognition note (German → Polish)
                recognition_note = genanki.Note(
                    model=recognition_model,
                    fields=fields,
                    guid=f"{base_guid}_recognition",
                    sort_field=0
                )
                recognition_deck.add_note(recognition_note)
                
                # 2. Production note (Polish → German)
                production_note = genanki.Note(
                    model=production_model,
                    fields=fields,
                    guid=f"{base_guid}_production",
                    sort_field=0
                )
                production_deck.add_note(production_note)
                
                # 3. Listening comprehension note (one per source card)
                # Templates will automatically only generate cards for sentences with content
                listening_note = genanki.Note(
                    model=listening_model,
                    fields=fields,
                    guid=f"{base_guid}_listening",
                    sort_field=0
                )
                listening_deck.add_note(listening_note)
                
                # 4. Sentence production note (one per source card)
                # Templates will automatically only generate cards for sentences with content
                sentence_prod_note = genanki.Note(
                    model=sentence_production_model,
                    fields=fields,
                    guid=f"{base_guid}_sentence_prod",
                    sort_field=0
                )
                sentence_prod_deck.add_note(sentence_prod_note)
                
                if card_idx == 0:  # Log first card for verification
                    print(f"  Card {card_idx+1}: Created 4 notes (1 recognition + 1 production + 1 listening + 1 sentence production)")
                        
            except Exception as e:
                failed_cards += 1
                print(f"⚠️  Warning: Failed to convert card {card_idx+1} (note_id={getattr(card, 'note_id', 'unknown')}): {e}")
                continue

        if failed_cards > 0:
            print(f"⚠️  {failed_cards} cards failed to convert and were skipped")

        # Collect media files (same as original function)
        available_media = {}  # filename -> file_path mapping
        
        # Extract media files from original .apkg if provided
        if original_apkg_path and original_apkg_path.exists():
            print("🎵 Extracting media files from original deck...")
            original_media = _extract_media_files(original_apkg_path)
            for media_path in original_media:
                filename = os.path.basename(media_path)
                available_media[filename] = media_path
            print(f"  Found {len(original_media)} original media files")
        
        # Add new media files from additional directory if provided
        if additional_media_dir and additional_media_dir.exists():
            print(f"🎵 Scanning new media files from {additional_media_dir}...")
            new_media = list(additional_media_dir.glob("*.mp3"))
            for media_path in new_media:
                filename = media_path.name
                available_media[filename] = str(media_path)  # New media overwrites original if same name
            print(f"  Found {len(new_media)} new media files")
            
            # Ensure silence file exists for audio control
            silence_file = "_1-minute-of-silence.mp3"
            if silence_file not in available_media:
                silence_path = additional_media_dir / silence_file
                if not silence_path.exists():
                    print(f"🔇 Creating silence file for audio control: {silence_file}")
                    _create_silence_file(silence_path)
                available_media[silence_file] = str(silence_path)
        
        print(f"📦 Total available media files: {len(available_media)}")
        
        # Filter media files to only include those actually referenced in the deck
        referenced_media = _get_referenced_media_files(deck, available_media)
        print(f"🔍 Media files actually used in deck: {len(referenced_media)}")
        
        media_files = list(referenced_media.values())

        # Generate the .apkg file with all 5 decks (parent + 4 subdecks)
        print("📦 Generating .apkg file with 4 separate subdecks...")
        try:
            # Package parent deck and all 4 subdecks separately
            all_decks = [parent_deck, recognition_deck, production_deck, listening_deck, sentence_prod_deck]
            genanki.Package(all_decks, media_files=media_files).write_to_file(str(output_path))
        except Exception as e:
            raise RuntimeError(f"Failed to write .apkg file: {e}")

        # Verify file was created and report stats
        if not output_path.exists():
            raise RuntimeError("Output file was not created successfully")
            
        file_size = output_path.stat().st_size
        
        # Count total notes created (should be 4 notes per source card)
        total_notes = len(recognition_deck.notes) + len(production_deck.notes) + len(listening_deck.notes) + len(sentence_prod_deck.notes)
        
        print(f"✅ Successfully saved 4-subdeck structure to {output_path}")
        print(f"   Source cards: {len(deck.cards)}")
        print(f"   Total notes created: {total_notes} (4 per source card)")
        print(f"   Recognition notes: {len(recognition_deck.notes)} (1 per source card)")
        print(f"   Production notes: {len(production_deck.notes)} (1 per source card)")
        print(f"   Listening notes: {len(listening_deck.notes)} (1 per source card)")  
        print(f"   Sentence production notes: {len(sentence_prod_deck.notes)} (1 per source card)")
        print(f"   File size: {file_size / (1024*1024):.1f} MB")
        print(f"")
        print(f"📋 Each note will generate multiple cards based on available content:")
        print(f"   • Listening: 1-9 cards per note (based on sentence content)")
        print(f"   • Sentence production: 1-9 cards per note (based on sentence content)")
        print(f"   • Recognition: 1 card per note")
        print(f"   • Production: 1 card per note")
        
    except Exception as e:
        print(f"\n❌ ERROR saving 4-subdeck Anki deck to {output_path}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        print("-" * 80)
        raise


def save_anki_deck(
    deck: AnkiDeck, output_path: Path, original_apkg_path: Path | None = None, additional_media_dir: Path | None = None
) -> None:
    """
    Save an AnkiDeck to a .apkg file using genanki.

    Args:
        deck: AnkiDeck to save
        output_path: Path for the output .apkg file
        original_apkg_path: Optional path to original .apkg for media extraction
        additional_media_dir: Optional directory containing new media files (e.g., TTS audio)
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
        
        print("📋 Creating genanki model and deck structure...")
        
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

        # Import deck IDs from card templates
        from card_templates import DECK_ID_MAIN, DECK_ID_RECOGNITION, DECK_ID_PRODUCTION, DECK_ID_LISTENING, DECK_ID_SENTENCE_PROD
        
        # Create parent deck and subdecks
        try:
            # Main parent deck
            parent_deck = genanki.Deck(
                DECK_ID_MAIN,
                "DTZ Goethe B1 German-Polish Model",
            )
            
            # 01 Recognition subdeck (German → Polish)
            recognition_deck = genanki.Deck(
                DECK_ID_RECOGNITION,
                "DTZ Goethe B1 German-Polish Model::01 Recognition",
            )
            
            # 02 Production subdeck (Polish → German)  
            production_deck = genanki.Deck(
                DECK_ID_PRODUCTION,
                "DTZ Goethe B1 German-Polish Model::02 Production",
            )
            
            # 03 Listening Comprehension subdeck (Audio → Text)
            listening_deck = genanki.Deck(
                DECK_ID_LISTENING,
                "DTZ Goethe B1 German-Polish Model::03 Listening Comprehension",
            )
            
            # 04 Sentence Production subdeck (Polish → German sentences)
            sentence_prod_deck = genanki.Deck(
                DECK_ID_SENTENCE_PROD,
                "DTZ Goethe B1 German-Polish Model::04 Sentence Production",
            )
            
            # Store reference to parent deck for adding notes
            anki_deck = parent_deck
            
        except Exception as e:
            raise RuntimeError(f"Failed to create genanki decks: {e}")

        print(f"🃏 Converting {len(deck.cards)} cards to genanki notes...")
        
        # Convert our cards to genanki notes
        failed_cards = 0
        for card_idx, card in enumerate(deck.cards):
            try:
                # Ensure all fields are strings and handle None/empty values
                fields = [
                    str(getattr(card, 'frequency_rank', '') or ""),
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
                    str(getattr(card, 'full_source_audio', '') or ""),
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
                    str(getattr(card, 'base_target_audio', '') or ""),
                    str(getattr(card, 's1_target_audio', '') or ""),
                    str(getattr(card, 's2_target_audio', '') or ""),
                    str(getattr(card, 's3_target_audio', '') or ""),
                    str(getattr(card, 's4_target_audio', '') or ""),
                    str(getattr(card, 's5_target_audio', '') or ""),
                    str(getattr(card, 's6_target_audio', '') or ""),
                    str(getattr(card, 's7_target_audio', '') or ""),
                    str(getattr(card, 's8_target_audio', '') or ""),
                    str(getattr(card, 's9_target_audio', '') or ""),
                ]

                # Preserve original GUID to maintain study progress
                
                note = genanki.Note(
                    model=model, 
                    fields=fields,
                    guid=card.original_guid or str(card.note_id),  # Use original GUID to preserve progress
                    sort_field=0  # Use first field for sorting
                )
                # Set the note's creation time to maintain frequency order
                # note.note_id = creation_time  # Commented out - note_id is read-only
                anki_deck.add_note(note)
                
            except Exception as e:
                failed_cards += 1
                print(f"⚠️  Warning: Failed to convert card {card_idx+1} (note_id={getattr(card, 'note_id', 'unknown')}): {e}")
                continue

        if failed_cards > 0:
            print(f"⚠️  {failed_cards} cards failed to convert and were skipped")

        # Collect all available media files from multiple sources
        available_media = {}  # filename -> file_path mapping
        
        # Extract media files from original .apkg if provided
        if original_apkg_path and original_apkg_path.exists():
            print("🎵 Extracting media files from original deck...")
            original_media = _extract_media_files(original_apkg_path)
            for media_path in original_media:
                filename = os.path.basename(media_path)
                available_media[filename] = media_path
            print(f"  Found {len(original_media)} original media files")
        
        # Add new media files from additional directory if provided
        if additional_media_dir and additional_media_dir.exists():
            print(f"🎵 Scanning new media files from {additional_media_dir}...")
            new_media = list(additional_media_dir.glob("*.mp3"))
            for media_path in new_media:
                filename = media_path.name
                available_media[filename] = str(media_path)  # New media overwrites original if same name
            print(f"  Found {len(new_media)} new media files")
            
            # Ensure silence file exists for audio control
            silence_file = "_1-minute-of-silence.mp3"
            if silence_file not in available_media:
                silence_path = additional_media_dir / silence_file
                if not silence_path.exists():
                    print(f"🔇 Creating silence file for audio control: {silence_file}")
                    _create_silence_file(silence_path)
                available_media[silence_file] = str(silence_path)
        
        print(f"📦 Total available media files: {len(available_media)}")
        
        # Filter media files to only include those actually referenced in the deck
        referenced_media = _get_referenced_media_files(deck, available_media)
        print(f"🔍 Media files actually used in deck: {len(referenced_media)}")
        
        media_files = list(referenced_media.values())

        # Generate the .apkg file with parent deck and subdecks
        print("📦 Generating .apkg file with 4 subdecks...")
        try:
            # Package all decks together: parent + 4 subdecks
            all_decks = [parent_deck, recognition_deck, production_deck, listening_deck, sentence_prod_deck]
            genanki.Package(all_decks, media_files=media_files).write_to_file(str(output_path))
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
        print("\n🔍 Full traceback:")
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


def _create_silence_file(output_path: Path) -> None:
    """
    Create a minimal silence MP3 file for audio control in Anki templates.
    
    Args:
        output_path: Path where to save the silence file
    """
    try:
        # Create a very short silence file using ffmpeg if available
        import subprocess
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=duration=0.1', 
            '-acodec', 'mp3', '-y', str(output_path)
        ], check=True, capture_output=True)
        print(f"   Created silence file with ffmpeg: {output_path.name}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: create a minimal MP3 header (empty file that players recognize)
        # This is a minimal valid MP3 file (just headers, practically silent)
        mp3_header = bytes([
            0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
        with open(output_path, 'wb') as f:
            f.write(mp3_header * 100)  # Repeat to make it a bit longer
        print(f"   Created minimal silence file: {output_path.name}")


def _get_referenced_media_files(deck: AnkiDeck, available_media: Dict[str, str]) -> Dict[str, str]:
    """
    Filter available media files to only include those actually referenced in the deck.
    
    Args:
        deck: AnkiDeck to analyze for media references
        available_media: Dict mapping filename -> file_path of all available media
        
    Returns:
        Dict mapping filename -> file_path of only referenced media files
    """
    import re
    from card_templates import DTZ_CARD_TEMPLATES
    
    referenced_files = set()
    
    # Pattern to match Anki sound references: [sound:filename.mp3]
    sound_pattern = re.compile(r'\[sound:([^\]]+)\]')
    
    # First, scan card templates for hardcoded media references
    print("🔍 Scanning card templates for media references...")
    template_media_count = 0
    for template in DTZ_CARD_TEMPLATES:
        # Check both question and answer formats
        for format_key in ['qfmt', 'afmt']:
            if format_key in template:
                matches = sound_pattern.findall(template[format_key])
                for filename in matches:
                    referenced_files.add(filename)
                    template_media_count += 1
                    print(f"   Found template reference: {filename}")
    
    # Then check all audio fields in all cards
    field_media_count = 0
    for card in deck.cards:
        # List all audio fields to check
        audio_fields = [
            'full_source_audio', 'base_audio', 's1_audio', 's2_audio', 's3_audio', 's4_audio', 
            's5_audio', 's6_audio', 's7_audio', 's8_audio', 's9_audio',
            'base_target_audio', 's1_target_audio', 's2_target_audio', 's3_target_audio', 
            's4_target_audio', 's5_target_audio', 's6_target_audio', 's7_target_audio', 
            's8_target_audio', 's9_target_audio'
        ]
        
        for field_name in audio_fields:
            field_value = getattr(card, field_name, "")
            if field_value:
                # Extract filename from [sound:filename.mp3] format
                matches = sound_pattern.findall(field_value)
                for filename in matches:
                    if filename not in referenced_files:  # Avoid double counting
                        field_media_count += 1
                    referenced_files.add(filename)
    
    print(f"   Template media references: {template_media_count}")
    print(f"   Field media references: {field_media_count}")
    print(f"   Total unique media files referenced: {len(referenced_files)}")
    
    # Filter available media to only include referenced files
    referenced_media = {}
    missing_files = []
    
    for filename in referenced_files:
        if filename in available_media:
            referenced_media[filename] = available_media[filename]
        else:
            missing_files.append(filename)
    
    # Handle special case: silence file needed for audio control but might not exist
    silence_file = "_1-minute-of-silence.mp3"
    if silence_file in referenced_files and silence_file not in available_media:
        print(f"⚠️  Creating placeholder for required silence file: {silence_file}")
        # Create a minimal silence file if needed (we'll handle this in save function)
        missing_files = [f for f in missing_files if f != silence_file]
    
    if missing_files:
        print(f"⚠️  Warning: {len(missing_files)} referenced media files not found:")
        for filename in missing_files[:5]:  # Show first 5 missing files
            print(f"     - {filename}")
        if len(missing_files) > 5:
            print(f"     ... and {len(missing_files) - 5} more")
    
    return referenced_media


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
            'full_source_audio', 'base_audio', 's1_audio', 's2_audio', 's3_audio', 's4_audio',
            's5_audio', 's6_audio', 's7_audio', 's8_audio', 's9_audio'
        ]
        
        # Copy metadata fields (these should never change)
        for field in metadata_fields:
            original_value = getattr(original_card, field, "")
            setattr(cleaned_card, field, original_value)
        
        # Copy frequency_rank if it exists
        if hasattr(original_card, 'frequency_rank'):
            setattr(cleaned_card, 'frequency_rank', original_card.frequency_rank)
        
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
                print("  ✅ No issues found - card is clean")
        
        return cleaned_card, total_issues
        
    except Exception as e:
        print("\n❌ ERROR cleaning translated card:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        print("-" * 80)
        
        # Return original translated card if cleaning fails
        return translated_card, 0
