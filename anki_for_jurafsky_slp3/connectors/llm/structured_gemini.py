import logging
import os
import time
from typing import Any, Dict, Tuple, Type, TypeVar

from google import genai
from google.genai.types import GenerateContentResponse
from pydantic import BaseModel
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from src.utils.cache import disk_cache
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(self, model: str = None) -> None:
        self.model: str = model or os.getenv("LLM_MODEL", "gemini-2.5-flash")
        self.client = genai.Client()

    def _make_api_call(
        self, text: str, schema: Any, generation_config: Dict[str, Any] | None = None
    ) -> Tuple[GenerateContentResponse, float]:
        config: dict[str, Any] = {
            "response_mime_type": "application/json",
            "response_schema": schema,
        }
        if generation_config:
            config.update(generation_config)

        start_time = time.time()
        response = self.client.models.generate_content(
            model=self.model, contents=text, config=config
        )
        api_latency = time.time() - start_time

        return response, api_latency

    def _parse_basemodel_response(
        self, response: GenerateContentResponse, schema: Type[T]
    ) -> T:
        if not isinstance(response.parsed, schema):
            raise TypeError(
                f"Expected Pydantic response of type {schema.__name__}, "
                f"but got {type(response.parsed).__name__}"
            )
        return response.parsed

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=5, min=20, max=360),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _generate_with_retry(
        self, text: str, schema: Any, generation_config: Dict[str, Any] | None = None
    ) -> Tuple[GenerateContentResponse, float]:
        return self._make_api_call(text, schema, generation_config)

    @disk_cache
    def generate(self, text: str, schema: Type[T]) -> Tuple[T, float]:
        response, latency = self._generate_with_retry(text, schema)
        parsed_response = self._parse_basemodel_response(response, schema)
        return parsed_response, latency