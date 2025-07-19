from pydantic import BaseModel
from typing import List, Optional


class AnkiCardTextFields(BaseModel):
    """
    Text-only model for AnkiCard with just the fields that need translation.
    This is sent to LLM for translation - excludes metadata and audio fields.
    """
    # Main word/phrase
    full_source: str = ""  # German word/phrase (unchanged)
    base_source: str = ""  # German base word (unchanged)
    base_target: str = ""  # Translation target (English -> Polish)
    
    # German-specific grammatical fields (unchanged)
    artikel_d: str = ""    # German article (der/die/das)
    plural_d: str = ""     # German plural form
    audio_text_d: str = "" # German audio text
    
    # Example sentences
    s1_source: str = ""    # German sentence 1 (unchanged)
    s1_target: str = ""    # Translation target 1 (English -> Polish)
    s2_source: str = ""    # German sentence 2 (unchanged)
    s2_target: str = ""    # Translation target 2 (English -> Polish)
    s3_source: str = ""    # German sentence 3 (unchanged)
    s3_target: str = ""    # Translation target 3 (English -> Polish)
    s4_source: str = ""    # German sentence 4 (unchanged)
    s4_target: str = ""    # Translation target 4 (English -> Polish)
    s5_source: str = ""    # German sentence 5 (unchanged)
    s5_target: str = ""    # Translation target 5 (English -> Polish)
    s6_source: str = ""    # German sentence 6 (unchanged)
    s6_target: str = ""    # Translation target 6 (English -> Polish)
    s7_source: str = ""    # German sentence 7 (unchanged)
    s7_target: str = ""    # Translation target 7 (English -> Polish)
    s8_source: str = ""    # German sentence 8 (unchanged)
    s8_target: str = ""    # Translation target 8 (English -> Polish)
    s9_source: str = ""    # German sentence 9 (unchanged)
    s9_target: str = ""    # Translation target 9 (English -> Polish)


class AnkiCard(BaseModel):
    """
    Universal AnkiCard schema for any language pair translation.
    
    Source language: The original language (e.g., German)
    Target language: The translation target (e.g., Polish, English, etc.)
    """
    note_id: int
    model_id: int
    
    # Main word/phrase
    full_source: str = ""  # Previously full_d (full German word/phrase)
    base_source: str = ""  # Previously base_d (base German word)
    base_target: str = ""  # Previously base_e (English/Polish translation)
    
    # German-specific grammatical fields (keep German naming as these are language-specific)
    artikel_d: str = ""    # German article (der/die/das)
    plural_d: str = ""     # German plural form
    audio_text_d: str = "" # German audio text
    
    # Example sentences
    s1_source: str = ""    # Previously s1 (sentence 1 in German)
    s1_target: str = ""    # Previously s1e (sentence 1 in target language)
    s2_source: str = ""    # Previously s2
    s2_target: str = ""    # Previously s2e
    s3_source: str = ""    # Previously s3
    s3_target: str = ""    # Previously s3e
    s4_source: str = ""    # Previously s4
    s4_target: str = ""    # Previously s4e
    s5_source: str = ""    # Previously s5
    s5_target: str = ""    # Previously s5e
    s6_source: str = ""    # Previously s6
    s6_target: str = ""    # Previously s6e
    s7_source: str = ""    # Previously s7
    s7_target: str = ""    # Previously s7e
    s8_source: str = ""    # Previously s8
    s8_target: str = ""    # Previously s8e
    s9_source: str = ""    # Previously s9
    s9_target: str = ""    # Previously s9e
    
    # Audio fields (keep existing naming)
    base_audio: str = ""   # Previously base_a
    s1_audio: str = ""     # Previously s1a
    s2_audio: str = ""     # Previously s2a
    s3_audio: str = ""     # Previously s3a
    s4_audio: str = ""     # Previously s4a
    s5_audio: str = ""     # Previously s5a
    s6_audio: str = ""     # Previously s6a
    s7_audio: str = ""     # Previously s7a
    s8_audio: str = ""     # Previously s8a
    s9_audio: str = ""     # Previously s9a
    
    # Metadata
    original_order: str = ""
    
    # Backward compatibility properties (optional - can be removed later)
    @property
    def full_d(self) -> str:
        """Backward compatibility: full_d -> full_source"""
        return self.full_source
    
    @full_d.setter
    def full_d(self, value: str) -> None:
        """Backward compatibility setter: full_d -> full_source"""
        self.full_source = value
    
    @property
    def base_e(self) -> str:
        """Backward compatibility: base_e -> base_target"""
        return self.base_target
    
    @base_e.setter
    def base_e(self, value: str) -> None:
        """Backward compatibility setter: base_e -> base_target"""
        self.base_target = value
    
    @property
    def base_d(self) -> str:
        """Backward compatibility: base_d -> base_source"""
        return self.base_source
    
    @base_d.setter
    def base_d(self, value: str) -> None:
        """Backward compatibility setter: base_d -> base_source"""
        self.base_source = value
    
    def to_text_model(self) -> 'AnkiCardTextFields':
        """
        Convert AnkiCard to AnkiCardTextFields for LLM translation.
        Extracts only the text fields that need translation, excluding metadata and audio.
        
        Returns:
            AnkiCardTextFields: Text-only model for LLM translation
        """
        return AnkiCardTextFields(
            # Main word/phrase
            full_source=self.full_source,
            base_source=self.base_source,
            base_target=self.base_target,
            # German-specific fields
            artikel_d=self.artikel_d,
            plural_d=self.plural_d,
            audio_text_d=self.audio_text_d,
            # Example sentences
            s1_source=self.s1_source,
            s1_target=self.s1_target,
            s2_source=self.s2_source,
            s2_target=self.s2_target,
            s3_source=self.s3_source,
            s3_target=self.s3_target,
            s4_source=self.s4_source,
            s4_target=self.s4_target,
            s5_source=self.s5_source,
            s5_target=self.s5_target,
            s6_source=self.s6_source,
            s6_target=self.s6_target,
            s7_source=self.s7_source,
            s7_target=self.s7_target,
            s8_source=self.s8_source,
            s8_target=self.s8_target,
            s9_source=self.s9_source,
            s9_target=self.s9_target,
        )
    
    def from_text_model(self, text_model: 'AnkiCardTextFields') -> 'AnkiCard':
        """
        Update this AnkiCard with translated content from AnkiCardTextFields.
        Preserves all metadata, audio fields, and note IDs from the original card.
        
        Args:
            text_model: Translated text fields from LLM
            
        Returns:
            AnkiCard: Updated card with translations but preserved metadata
        """
        # Create a copy to avoid modifying the original
        updated_card = self.model_copy()
        
        # Update only the text fields from the translated model
        updated_card.full_source = text_model.full_source
        updated_card.base_source = text_model.base_source
        updated_card.base_target = text_model.base_target
        updated_card.artikel_d = text_model.artikel_d
        updated_card.plural_d = text_model.plural_d
        updated_card.audio_text_d = text_model.audio_text_d
        updated_card.s1_source = text_model.s1_source
        updated_card.s1_target = text_model.s1_target
        updated_card.s2_source = text_model.s2_source
        updated_card.s2_target = text_model.s2_target
        updated_card.s3_source = text_model.s3_source
        updated_card.s3_target = text_model.s3_target
        updated_card.s4_source = text_model.s4_source
        updated_card.s4_target = text_model.s4_target
        updated_card.s5_source = text_model.s5_source
        updated_card.s5_target = text_model.s5_target
        updated_card.s6_source = text_model.s6_source
        updated_card.s6_target = text_model.s6_target
        updated_card.s7_source = text_model.s7_source
        updated_card.s7_target = text_model.s7_target
        updated_card.s8_source = text_model.s8_source
        updated_card.s8_target = text_model.s8_target
        updated_card.s9_source = text_model.s9_source
        updated_card.s9_target = text_model.s9_target
        
        # Note: metadata (note_id, model_id, original_order) and audio fields are preserved
        # from the original card and not updated from text_model
        
        return updated_card


class AnkiDeck(BaseModel):
    cards: List[AnkiCard]
    name: Optional[str] = None
    total_cards: int = 0

    def __post_init__(self):
        self.total_cards = len(self.cards)
