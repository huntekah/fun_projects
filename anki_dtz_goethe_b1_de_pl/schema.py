from pydantic import BaseModel
from typing import List, Optional


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


class AnkiDeck(BaseModel):
    cards: List[AnkiCard]
    name: Optional[str] = None
    total_cards: int = 0

    def __post_init__(self):
        self.total_cards = len(self.cards)
