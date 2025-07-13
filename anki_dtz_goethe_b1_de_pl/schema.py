from pydantic import BaseModel
from typing import List, Optional


class AnkiCard(BaseModel):
    note_id: int
    model_id: int
    full_d: str = ""
    base_e: str = ""
    base_d: str = ""
    artikel_d: str = ""
    plural_d: str = ""
    audio_text_d: str = ""
    s1: str = ""
    s1e: str = ""
    s2: str = ""
    s2e: str = ""
    s3: str = ""
    s3e: str = ""
    s4: str = ""
    s4e: str = ""
    s5: str = ""
    s5e: str = ""
    s6: str = ""
    s6e: str = ""
    s7: str = ""
    s7e: str = ""
    s8: str = ""
    s8e: str = ""
    s9: str = ""
    s9e: str = ""
    original_order: str = ""
    base_a: str = ""
    s1a: str = ""
    s2a: str = ""
    s3a: str = ""
    s4a: str = ""
    s5a: str = ""
    s6a: str = ""
    s7a: str = ""
    s8a: str = ""
    s9a: str = ""


class AnkiDeck(BaseModel):
    cards: List[AnkiCard]
    name: Optional[str] = None
    total_cards: int = 0
    
    def __post_init__(self):
        self.total_cards = len(self.cards)