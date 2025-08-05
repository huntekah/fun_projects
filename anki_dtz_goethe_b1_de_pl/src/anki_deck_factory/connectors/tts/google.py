import hashlib
from pathlib import Path
from typing import Optional
from google.cloud import texttospeech
from diskcache import Cache

from .base import AbstractTTS


class GoogleTTS(AbstractTTS):
    """Google Cloud Text-to-Speech implementation of the AbstractTTS interface."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the TTS client and cache."""
        self.client = texttospeech.TextToSpeechClient()
        
        # Initialize DiskCache for caching TTS results
        if cache_dir is None:
            cache_dir = Path("tts_cache")
        cache_dir.mkdir(exist_ok=True)
        self.cache = Cache(str(cache_dir))
        
        # Define voice configurations for each language
        self.voices = {
            'de-DE': texttospeech.VoiceSelectionParams(
                language_code="de-DE",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            ),
            'pl-PL': texttospeech.VoiceSelectionParams(
                language_code="pl-PL", 
                name="pl-PL-Standard-G",
            )
        }
        
        # Audio configuration
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
    
    def _generate_cache_key(self, text: str, language_code: str, voice_name: str, speaking_rate: float = 1.0) -> str:
        """Generate a cache key for text, voice configuration, and speaking rate."""
        # Smart backward compatibility: only include speed in key if != 1.0
        if speaking_rate == 1.0:
            content = f"{text}_{voice_name}"  # Same as old cache keys
        else:
            content = f"{text}_{voice_name}_{speaking_rate}"  # New cache keys for variable speed
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
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
        if not text or not text.strip():
            raise ValueError(f"Empty text provided for synthesis")
        
        if language_code not in self.voices:
            raise ValueError(f"Unsupported language: {language_code}")
        
        # Generate output path if not provided
        if output_file is None:
            safe_text = "".join(c for c in text[:20] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_file = Path(f"audio_{safe_text}_{language_code}.mp3")
        
        # Generate cache key
        cache_key = self._generate_cache_key(text, language_code, voice_name)
        
        try:
            # Check cache first
            cached_audio = self.cache.get(cache_key)
            if cached_audio is not None:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "wb") as out:
                    if isinstance(cached_audio, bytes):
                        out.write(cached_audio)
                    else:
                        raise TypeError(f"Unexpected cached audio type: {type(cached_audio)}")
                return output_file
            
            # If text doesn't have any punctuation at the end, add a dot
            if text[-1] not in [".", "!", "?"]:
                text += ". "

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Get voice for language
            voice = self.voices[language_code]
            
            # Create audio config
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0
            )
            
            # Perform TTS request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice, 
                audio_config=audio_config
            )
            
            # Cache the audio data
            audio_data = response.audio_content
            self.cache.set(cache_key, audio_data)
            
            # Save audio file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "wb") as out:
                out.write(audio_data)
            
            return output_file
            
        except Exception as e:
            raise RuntimeError(f"TTS synthesis failed for '{text}': {e}")
    
    def get_supported_voices(self, language_code: str) -> list[str]:
        """
        Get list of available voices for a language.
        
        Args:
            language_code: Language code (e.g., 'de-DE', 'pl-PL')
            
        Returns:
            List of voice identifiers
        """
        try:
            # List voices from Google Cloud TTS
            response = self.client.list_voices()
            voices = []
            for voice in response.voices:
                if language_code in voice.language_codes:
                    voices.append(voice.name)
            return voices
        except Exception as e:
            # Return our predefined voices as fallback
            if language_code in self.voices:
                voice = self.voices[language_code]
                return [getattr(voice, 'name', f'{language_code}-default')]
            return []
    
    def cache_info(self) -> dict:
        """Get cache statistics."""
        return {
            'cache_size': getattr(self.cache, 'size', 0),
            'cache_volume_mb': self.cache.volume() / (1024 * 1024),
            'cache_directory': str(self.cache.directory)
        }
    
    def close(self):
        """Close the cache properly."""
        self.cache.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()