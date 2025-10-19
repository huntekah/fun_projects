from typing import List, Literal, Union
from pydantic import BaseModel, Field


class QACard(BaseModel):
    """Represents a simple Question/Answer card."""

    type: Literal["Q&A"]
    q: str = Field(..., description="The question text.")
    a: str = Field(..., description="The answer text.")


class ClozeCard(BaseModel):
    """Represents a card with a cloze deletion."""

    type: Literal["Cloze"]
    text: str = Field(
        ..., description="The full text with cloze syntax, e.g., {{c1::text}}."
    )


class EnumerationCard(BaseModel):
    """Represents a card for an ordered or unordered list."""

    type: Literal["Enumeration"]
    prompt: str = Field(
        ...,
        description="The question that prompts for the list, e.g., 'What are the steps of...'",
    )
    items: List[str] = Field(..., description="The list of items to be memorized.")
    ordered: bool = Field(
        default=False, description="Whether the order of items matters."
    )


CardType = Union[QACard, ClozeCard, EnumerationCard]


class AtomicCards(BaseModel):
    """Container for a list of extracted atomic cards from a text chunk."""

    cards: List[CardType] = Field(
        ..., description="List of atomic flashcards extracted from the text."
    )
