import datetime
import logging
from typing import Type, TypeVar

from google import genai
from google.genai.types import (
    GenerateContentResponse,
    GenerateContentResponseUsageMetadata,
    HttpOptions,
)
from pydantic import BaseModel


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class VertexAIConfig(BaseModel):
    """Configuration for Vertex AI Gemini client."""

    project_id: str = "maximal-arcade-267011"
    location: str = "europe-west4"
    llm_model: str = "gemini-2.0-flash"


class LLMClient:
    def __init__(self, config: VertexAIConfig) -> None:
        self.project: str = config.project_id
        self.location: str = config.location
        self.model: str = config.llm_model
        self.client = genai.Client(
            vertexai=True,
            project=self.project,
            location=self.location,
            http_options=HttpOptions(timeout=100_000),
        )

    def generate(self, text: str, schema: Type[T]) -> T:
        import traceback
        
        try:
            logger.debug(f"Generating content for text: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            if not text or not text.strip():
                raise ValueError("Empty or whitespace-only text provided")
            
            if not schema:
                raise ValueError("No schema provided for structured generation")
            
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
            return response.parsed
            
        except Exception as e:
            logger.error(f"LLM generation failed for schema {schema.__name__ if schema else 'Unknown'}")
            logger.error(f"Text length: {len(text) if text else 0} characters")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            
            # Don't print full traceback here as it will be handled by the calling function
            # Just re-raise with the original exception
            raise
