#!/usr/bin/env python3
"""
Add TTS audio to Anki cards using Google Cloud Text-to-Speech.
Test script to generate audio for a random card's key fields.
"""

import random
import hashlib
from pathlib import Path
from google.cloud import texttospeech
from diskcache import Cache
from utilities import load_anki_deck
from src.anki_deck_factory.domain.models import AnkiCard


class TTSGenerator:
    """Google Cloud Text-to-Speech generator with language-specific voices and caching."""
    
    def __init__(self, cache_dir: Path | None = None):
        """Initialize the TTS client and cache."""
        self.client = texttospeech.TextToSpeechClient()
        
        # Initialize DiskCache for caching TTS results
        if cache_dir is None:
            cache_dir = Path("tts_cache")
        cache_dir.mkdir(exist_ok=True)
        self.cache = Cache(str(cache_dir))
        
        # Define voice configurations for each language
        self.voices = {
            'german': texttospeech.VoiceSelectionParams(
                language_code="de-DE",
                # name="de-DE-Chirp3-HD-Achernar",  # German Studio voice
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            ),
            'polish': texttospeech.VoiceSelectionParams(
                language_code="pl-PL", 
                name="pl-PL-Standard-G",  # Polish Standard voice (sounds great)
                # ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
        }
        
        # Audio configuration
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
    
    def _generate_cache_key(self, text: str, language: str, speaking_rate: float = 1.0) -> str:
        """Generate a cache key for text, voice configuration, and speaking rate."""
        voice_name = self.voices[language].name
        # Smart backward compatibility: only include speed in key if != 1.0
        if speaking_rate == 1.0:
            content = f"{text}_{voice_name}"  # Same as old cache keys
        else:
            content = f"{text}_{voice_name}_{speaking_rate}"  # New cache keys for variable speed
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def close(self):
        """Close the cache properly."""
        self.cache.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def cache_info(self) -> dict:
        """Get cache statistics."""
        return {
            'cache_size': getattr(self.cache, 'size', 0),
            'cache_volume_mb': self.cache.volume() / (1024 * 1024),
            'cache_directory': str(self.cache.directory)
        }
    
    def synthesize_speech(self, text: str, language: str, output_path: Path, speaking_rate: float = 1.0) -> bool:
        """
        Synthesize speech for given text in specified language with caching.
        
        Args:
            text: Text to synthesize
            language: 'german' or 'polish'
            output_path: Path to save MP3 file
            speaking_rate: Speech speed (0.25-2.0, default 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            print(f"⚠️  Skipping empty text for {output_path}")
            return False
        
        if language not in self.voices:
            print(f"❌ Unsupported language: {language}")
            return False
        
        # Generate cache key including speaking rate
        cache_key = self._generate_cache_key(text, language, speaking_rate)
        
        try:
            # Check cache first
            cached_audio = self.cache.get(cache_key)
            if cached_audio is not None:
                print(f"💾 Using cached {language} audio: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as out:
                    if isinstance(cached_audio, bytes):
                        out.write(cached_audio)
                    else:
                        # Handle unexpected cached data type
                        print(f"⚠️  Warning: Unexpected cached audio type: {type(cached_audio)}")
                        return False
                print(f"✅ Saved from cache: {output_path}")
                return True
            
            # if text doesnt have any interpunction at the end, add a dot.
            if text[-1] not in [".", "!", "?"]:
                text += ". "

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Get voice for language
            voice = self.voices[language]
            
            # Create audio config with variable speaking rate
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate
            )
            
            # Perform TTS request
            print(f"🎤 Generating {language} audio (speed {speaking_rate}): '{text[:50]}{'...' if len(text) > 50 else ''}'")
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice, 
                audio_config=audio_config
            )
            
            # Cache the audio data
            audio_data = response.audio_content
            self.cache.set(cache_key, audio_data)
            print(f"💾 Cached audio for key: {cache_key[:12]}...")
            
            # Save audio file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as out:
                out.write(audio_data)
            
            print(f"✅ Saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ TTS failed for '{text}': {e}")
            return False


def generate_audio_for_card(card: AnkiCard, output_dir: Path, tts_generator: TTSGenerator | None = None) -> dict:
    """
    Generate TTS audio for key fields of an Anki card.
    
    Args:
        card: AnkiCard to generate audio for
        output_dir: Directory to save audio files
        tts_generator: Optional TTSGenerator instance (will create if None)
        
    Returns:
        Dict with generation results
    """
    # Use provided generator or create new one
    if tts_generator is None:
        tts = TTSGenerator()
        should_close = True
    else:
        tts = tts_generator
        should_close = False
    
    # Define fields to generate audio for
    fields_to_generate = [
        ('base_source', 'german', card.base_source),
        ('base_target', 'polish', card.base_target),
        ('s1_source', 'german', card.s1_source),
        ('s1_target', 'polish', card.s1_target),
    ]
    
    results = {}
    
    print(f"\n🎵 Generating TTS for card: {card.base_source}")
    print(f"   Note ID: {card.note_id}")
    
    for field_name, language, text in fields_to_generate:
        if not text or not text.strip():
            print(f"⚠️  Skipping empty field: {field_name}")
            results[field_name] = None
            continue
        
        # Create output filename
        safe_filename = f"card_{card.note_id}_{field_name}.mp3"
        output_path = output_dir / safe_filename
        
        # Generate audio
        success = tts.synthesize_speech(text, language, output_path)
        results[field_name] = output_path if success else None
    
    # Close if we created the generator
    if should_close:
        tts.close()
    
    return results


def test_tts_with_random_card(deck_path: Path, output_dir: Path | None = None) -> None:
    """
    Test TTS generation with a random card from the deck.
    
    Args:
        deck_path: Path to Anki deck file
        output_dir: Directory to save test audio files
    """
    if output_dir is None:
        output_dir = Path("test_audio")
    
    print("🔊 Testing Google Cloud TTS with random card")
    print(f"📁 Output directory: {output_dir}")
    
    # Load deck
    deck = load_anki_deck(deck_path)
    
    # Filter cards with content in key fields
    cards_with_content = [
        card for card in deck.cards 
        if card.base_source and card.base_target and card.s1_source and card.s1_target
    ]
    
    if not cards_with_content:
        print("❌ No cards found with content in all required fields")
        return
    
    # Select random card (with fixed seed for consistent testing)
    random.seed(42)
    random_card = random.choice(cards_with_content)
    
    print("\n📊 Selected random card:")
    print(f"   German word: {random_card.base_source}")
    print(f"   Polish word: {random_card.base_target}")
    print(f"   German sentence: {random_card.s1_source}")
    print(f"   Polish sentence: {random_card.s1_target}")
    
    # Generate audio with caching
    with TTSGenerator() as tts:
        # Show initial cache info
        cache_info = tts.cache_info()
        print("\n💾 Cache info (before):")
        print(f"   Cached items: {cache_info['cache_size']}")
        print(f"   Cache size: {cache_info['cache_volume_mb']:.2f} MB")
        print(f"   Cache directory: {cache_info['cache_directory']}")
        
        results = generate_audio_for_card(random_card, output_dir, tts)
        
        # Show final cache info
        cache_info = tts.cache_info()
        print("\n💾 Cache info (after):")
        print(f"   Cached items: {cache_info['cache_size']}")
        print(f"   Cache size: {cache_info['cache_volume_mb']:.2f} MB")
    
    # Summary
    successful = sum(1 for path in results.values() if path is not None)
    total = len(results)
    
    print("\n📈 TTS Generation Summary:")
    print(f"   Successful: {successful}/{total} files")
    
    if successful > 0:
        print(f"   Audio files saved in: {output_dir}")
        print("   🎧 Test the audio quality and pronunciation!")
        print("   💡 Run again to see caching in action!")
    
    return results  # type: ignore


if __name__ == "__main__":
    # Test with sample deck
    deck_path = Path("data/DTZ_Goethe_B1_DE_PL_Sample_FrequencySorted.apkg")
    
    if deck_path.exists():
        test_results = test_tts_with_random_card(deck_path)
    else:
        print(f"❌ Deck file not found: {deck_path}")
        print("Please ensure the deck file exists before running TTS tests.")