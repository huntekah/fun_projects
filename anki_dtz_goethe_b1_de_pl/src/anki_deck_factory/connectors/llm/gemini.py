import logging
import hashlib
import os
from typing import Type, TypeVar, List

import diskcache as dc
from dotenv import load_dotenv
from google import genai
from google.genai.types import (
    GenerateContentResponse,
    HttpOptions,
)
from pydantic import BaseModel

from .base import AbstractTranslator
from ...domain.models import AnkiCardTextFields

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Initialize disk cache for LLM responses
cache = dc.Cache('.llm_cache', size_limit=1_000_000_000)  # 1GB cache limit


class VertexAIConfig(BaseModel):
    """Configuration for Vertex AI Gemini client."""

    project_id: str = os.getenv("VERTEX_AI_PROJECT_ID", "")
    location: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    llm_model: str = os.getenv("VERTEX_AI_MODEL", "gemini-2.0-flash")


class LLMClient:
    def __init__(self, config: VertexAIConfig) -> None:
        self.project: str = config.project_id
        self.location: str = config.location
        self.model: str = config.llm_model
        self.config = config  # Store config for cache key generation
        self.client = genai.Client(
            vertexai=True,
            project=self.project,
            location=self.location,
            http_options=HttpOptions(timeout=100_000),
        )
    
    def _create_cache_key(self, text: str, schema: Type[T]) -> str:
        """
        Create a unique cache key for the LLM request.
        
        Args:
            text: The prompt text
            schema: The expected response schema
            
        Returns:
            str: Unique cache key
        """
        # Create hash of model + text + schema that uniquely identifies the request
        content_to_hash = f"{self.model}|{text}|{schema.__name__}"
        return hashlib.sha256(content_to_hash.encode()).hexdigest()
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics for monitoring."""
        try:
            cache_size_mb = sum(cache.volume().values()) / (1024 * 1024) if cache.volume() else 0
            return {
                "cache_items": getattr(cache, 'size', 0),
                "cache_size_mb": round(cache_size_mb, 1),
                "cache_directory": cache.directory
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

    def generate(self, text: str, schema: Type[T]) -> T:
        
        try:
            logger.debug(f"Generating content for text: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            if not text or not text.strip():
                raise ValueError("Empty or whitespace-only text provided")
            
            if not schema:
                raise ValueError("No schema provided for structured generation")
            
            # Create cache key and check for cached response
            cache_key = self._create_cache_key(text, schema)
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"🎯 Cache hit for {schema.__name__} - using cached response")
                try:
                    return schema(**cached_result)  # type: ignore
                except Exception as e:
                    logger.warning(f"Failed to deserialize cached response: {e}. Making fresh API call.")
                    # Continue to make API call if deserialization fails
            else:
                logger.debug(f"🔄 Cache miss for {schema.__name__} - making API call")
            
            logger.debug(f"Using model: {self.model}")
            logger.debug(f"Expected response schema: {schema.__name__}")
            
            try:
                response: GenerateContentResponse = self.client.models.generate_content(
                    model=self.model,
                    contents=text,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": schema,
                    },
                )
            except Exception as e:
                # Log API call details for debugging
                logger.error(f"API call failed - Model: {self.model}, Project: {self.project}, Location: {self.location}")
                if "quota" in str(e).lower() or "rate" in str(e).lower():
                    raise RuntimeError(f"API rate limit or quota exceeded: {e}")
                elif "auth" in str(e).lower() or "permission" in str(e).lower():
                    raise RuntimeError(f"Authentication or permission error: {e}")
                elif "timeout" in str(e).lower():
                    raise RuntimeError(f"API request timeout: {e}")
                else:
                    raise RuntimeError(f"API call failed: {e}")

            # Check if response exists and has content
            if not response:
                raise RuntimeError("Received empty response from API")
            
            # Log response metadata if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                logger.debug(f"Token usage - Input: {getattr(usage, 'prompt_token_count', 'N/A')}, "
                           f"Output: {getattr(usage, 'candidates_token_count', 'N/A')}, "
                           f"Total: {getattr(usage, 'total_token_count', 'N/A')}")
            
            # Check if response was parsed successfully
            if not hasattr(response, 'parsed') or response.parsed is None:
                # Try to get raw text response for debugging
                raw_text = getattr(response, 'text', 'No raw text available')
                raise RuntimeError(f"API response could not be parsed into {schema.__name__}. Raw response: {raw_text[:200]}...")

            # Validate the parsed response type
            if not isinstance(response.parsed, schema):
                received_type = type(response.parsed).__name__ if response.parsed else "None"
                raise ValueError(f"Expected response of type {schema.__name__}, got {received_type}")

            logger.debug(f"Successfully generated and parsed {schema.__name__} response")
            
            # Cache the successful response for future use
            try:
                cache.set(cache_key, response.parsed.model_dump())
                logger.debug(f"💾 Cached {schema.__name__} response")
            except Exception as e:
                logger.warning(f"Failed to cache response: {e}")
                # Continue execution even if caching fails
            
            return response.parsed
            
        except Exception as e:
            logger.error(f"LLM generation failed for schema {schema.__name__ if schema else 'Unknown'}")
            logger.error(f"Text length: {len(text) if text else 0} characters")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            
            # Don't print full traceback here as it will be handled by the calling function
            # Just re-raise with the original exception
            raise


class GeminiTranslator(AbstractTranslator):
    """Gemini implementation of the AbstractTranslator interface."""
    
    def __init__(self, config: VertexAIConfig = None):
        self.config = config or VertexAIConfig()
        self.client = LLMClient(self.config)
    
    def translate(self, card: AnkiCardTextFields) -> AnkiCardTextFields:
        """
        Translate a single card's text fields using Gemini.
        
        Args:
            card: AnkiCardTextFields with source language content
            
        Returns:
            AnkiCardTextFields with translated target language content
        """
        # Import here to avoid circular imports
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        from prompt import create_text_translation_prompt
        
        prompt = create_text_translation_prompt(card)
        translated_card = self.client.generate(prompt, AnkiCardTextFields)
        return translated_card
    
    def translate_batch(self, cards: List[AnkiCardTextFields]) -> List[AnkiCardTextFields]:
        """
        Translate multiple cards efficiently.
        
        Args:
            cards: List of AnkiCardTextFields with source language content
            
        Returns:
            List of AnkiCardTextFields with translated target language content
        """
        # For now, implement as sequential calls
        # TODO: Implement true batch processing if Gemini supports it
        translated_cards = []
        for card in cards:
            translated_card = self.translate(card)
            translated_cards.append(translated_card)
        return translated_cards
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics for monitoring."""
        return self.client.get_cache_stats()