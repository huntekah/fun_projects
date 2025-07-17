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
            http_options=HttpOptions(timeout=10000),
        )

    def generate(self, text: str, schema: Type[T], log_costs=True) -> T:
        logger.debug(f"Generating content for text: {text}")
        response: GenerateContentResponse = self.client.models.generate_content(
            model=self.model,
            contents=text,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )

        if isinstance(response.parsed, schema):
            return response.parsed

        raise ValueError(
            f"Expected response of type {type(schema)}, got {type(response.parsed)}"
        )
