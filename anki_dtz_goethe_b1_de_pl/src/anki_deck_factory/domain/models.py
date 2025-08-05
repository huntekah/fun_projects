from pydantic import BaseModel, Field
from typing import List, Optional


class AnkiCardTextFields(BaseModel):
    """Text-only model for AnkiCard with just the fields that need translation."""
    
    full_source: str = Field(default="", description="German word/phrase (unchanged)")
    base_source: str = Field(default="", description="German base word (unchanged)")
    base_target: str = Field(default="", description="Base word translated to target language")
    
    artikel_d: str = Field(default="", description="German article (der/die/das)")
    plural_d: str = Field(default="", description="German plural form")
    audio_text_d: str = Field(default="", description="German audio text")
    
    s1_source: str = Field(default="", description="German sentence 1 (unchanged)")
    s1_target: str = Field(default="", description="Sentence 1 translated to target language")
    s2_source: str = Field(default="", description="German sentence 2 (unchanged)")
    s2_target: str = Field(default="", description="Sentence 2 translated to target language")
    s3_source: str = Field(default="", description="German sentence 3 (unchanged)")
    s3_target: str = Field(default="", description="Sentence 3 translated to target language")
    s4_source: str = Field(default="", description="German sentence 4 (unchanged)")
    s4_target: str = Field(default="", description="Sentence 4 translated to target language")
    s5_source: str = Field(default="", description="German sentence 5 (unchanged)")
    s5_target: str = Field(default="", description="Sentence 5 translated to target language")
    s6_source: str = Field(default="", description="German sentence 6 (unchanged)")
    s6_target: str = Field(default="", description="Sentence 6 translated to target language")
    s7_source: str = Field(default="", description="German sentence 7 (unchanged)")
    s7_target: str = Field(default="", description="Sentence 7 translated to target language")
    s8_source: str = Field(default="", description="German sentence 8 (unchanged)")
    s8_target: str = Field(default="", description="Sentence 8 translated to target language")
    s9_source: str = Field(default="", description="German sentence 9 (unchanged)")
    s9_target: str = Field(default="", description="Sentence 9 translated to target language")


class AnkiCard(BaseModel):
    """Universal AnkiCard schema for any language pair translation."""
    
    note_id: int = Field(description="Unique note identifier")
    model_id: int = Field(description="Anki model identifier")
    original_guid: str = Field(default="", description="Original GUID from source deck for progress preservation")
    frequency_rank: str = Field(default="", description="Frequency rank for browser sorting (001, 002, 003...)")
    
    full_source: str = Field(default="", description="Full German word/phrase")
    base_source: str = Field(default="", description="Base German word")
    base_target: str = Field(default="", description="Base word translated to target language")
    
    artikel_d: str = Field(default="", description="German article (der/die/das)")
    plural_d: str = Field(default="", description="German plural form")
    audio_text_d: str = Field(default="", description="German audio text")
    
    s1_source: str = Field(default="", description="German sentence 1")
    s1_target: str = Field(default="", description="Sentence 1 translated to target language")
    s2_source: str = Field(default="", description="German sentence 2")
    s2_target: str = Field(default="", description="Sentence 2 translated to target language")
    s3_source: str = Field(default="", description="German sentence 3")
    s3_target: str = Field(default="", description="Sentence 3 translated to target language")
    s4_source: str = Field(default="", description="German sentence 4")
    s4_target: str = Field(default="", description="Sentence 4 translated to target language")
    s5_source: str = Field(default="", description="German sentence 5")
    s5_target: str = Field(default="", description="Sentence 5 translated to target language")
    s6_source: str = Field(default="", description="German sentence 6")
    s6_target: str = Field(default="", description="Sentence 6 translated to target language")
    s7_source: str = Field(default="", description="German sentence 7")
    s7_target: str = Field(default="", description="Sentence 7 translated to target language")
    s8_source: str = Field(default="", description="German sentence 8")
    s8_target: str = Field(default="", description="Sentence 8 translated to target language")
    s9_source: str = Field(default="", description="German sentence 9")
    s9_target: str = Field(default="", description="Sentence 9 translated to target language")
    
    full_source_audio: str = Field(default="", description="Audio file for full source phrase (German)")
    base_audio: str = Field(default="", description="Audio file for base word (German)")
    s1_audio: str = Field(default="", description="Audio file for sentence 1 (German)")
    s2_audio: str = Field(default="", description="Audio file for sentence 2 (German)")
    s3_audio: str = Field(default="", description="Audio file for sentence 3 (German)")
    s4_audio: str = Field(default="", description="Audio file for sentence 4 (German)")
    s5_audio: str = Field(default="", description="Audio file for sentence 5 (German)")
    s6_audio: str = Field(default="", description="Audio file for sentence 6 (German)")
    s7_audio: str = Field(default="", description="Audio file for sentence 7 (German)")
    s8_audio: str = Field(default="", description="Audio file for sentence 8 (German)")
    s9_audio: str = Field(default="", description="Audio file for sentence 9 (German)")
    
    base_target_audio: str = Field(default="", description="Audio file for base word (Polish)")
    s1_target_audio: str = Field(default="", description="Audio file for sentence 1 (Polish)")
    s2_target_audio: str = Field(default="", description="Audio file for sentence 2 (Polish)")
    s3_target_audio: str = Field(default="", description="Audio file for sentence 3 (Polish)")
    s4_target_audio: str = Field(default="", description="Audio file for sentence 4 (Polish)")
    s5_target_audio: str = Field(default="", description="Audio file for sentence 5 (Polish)")
    s6_target_audio: str = Field(default="", description="Audio file for sentence 6 (Polish)")
    s7_target_audio: str = Field(default="", description="Audio file for sentence 7 (Polish)")
    s8_target_audio: str = Field(default="", description="Audio file for sentence 8 (Polish)")
    s9_target_audio: str = Field(default="", description="Audio file for sentence 9 (Polish)")
    
    original_order: str = Field(default="", description="Original card order metadata")
    
    @property
    def full_d(self) -> str:
        return self.full_source
    
    @full_d.setter
    def full_d(self, value: str) -> None:
        self.full_source = value
    
    @property
    def base_e(self) -> str:
        return self.base_target
    
    @base_e.setter
    def base_e(self, value: str) -> None:
        self.base_target = value
    
    @property
    def base_d(self) -> str:
        return self.base_source
    
    @base_d.setter
    def base_d(self, value: str) -> None:
        self.base_source = value
    
    def to_text_model(self) -> 'AnkiCardTextFields':
        """Convert AnkiCard to AnkiCardTextFields for LLM translation."""
        return AnkiCardTextFields(
            full_source=self.full_source,
            base_source=self.base_source,
            base_target=self.base_target,
            artikel_d=self.artikel_d,
            plural_d=self.plural_d,
            audio_text_d=self.audio_text_d,
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
        """Update this AnkiCard with translated content from AnkiCardTextFields."""
        updated_card = self.model_copy()
        
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
        
        return updated_card


class AnkiDeck(BaseModel):
    cards: List[AnkiCard] = Field(description="List of AnkiCard objects")
    name: Optional[str] = Field(default=None, description="Deck name")
    total_cards: int = Field(default=0, description="Total number of cards")

    def __post_init__(self):
        self.total_cards = len(self.cards)