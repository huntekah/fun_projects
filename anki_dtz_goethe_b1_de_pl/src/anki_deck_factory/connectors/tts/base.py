from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path


class AbstractTTS(ABC):
    """Abstract base class for Text-to-Speech services."""
    
    @abstractmethod
    def synthesize(
        self, 
        text: str, 
        language_code: str, 
        voice_name: str,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            language_code: Language code (e.g., 'de-DE', 'pl-PL')
            voice_name: Voice identifier for the TTS engine
            output_file: Optional output file path. If None, generate a unique filename.
            
        Returns:
            Path to the generated audio file
        """
        pass
    
    @abstractmethod
    def get_supported_voices(self, language_code: str) -> list[str]:
        """
        Get list of available voices for a language.
        
        Args:
            language_code: Language code (e.g., 'de-DE', 'pl-PL')
            
        Returns:
            List of voice identifiers
        """
        pass
    
    @abstractmethod
    def __enter__(self):
        """Context manager entry."""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass