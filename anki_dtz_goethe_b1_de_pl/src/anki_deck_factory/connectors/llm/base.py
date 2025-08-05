from abc import ABC, abstractmethod
from typing import List
from ...domain.models import AnkiCardTextFields


class AbstractTranslator(ABC):
    """Abstract base class for translation services."""
    
    @abstractmethod
    def translate(self, card: AnkiCardTextFields) -> AnkiCardTextFields:
        """
        Translate a single card's text fields.
        
        Args:
            card: AnkiCardTextFields with source language content
            
        Returns:
            AnkiCardTextFields with translated target language content
        """
        pass
    
    @abstractmethod
    def translate_batch(self, cards: List[AnkiCardTextFields]) -> List[AnkiCardTextFields]:
        """
        Translate multiple cards efficiently.
        
        Args:
            cards: List of AnkiCardTextFields with source language content
            
        Returns:
            List of AnkiCardTextFields with translated target language content
        """
        pass