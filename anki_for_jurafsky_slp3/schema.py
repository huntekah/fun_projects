# from pydantic import BaseModel, Field
# from typing import List, Optional


# class SLP3FlashcardTextFields(BaseModel):
#     """Text-only model for SLP3 flashcard with just the fields that need generation."""

#     concept: str = Field(default="", description="Main NLP/linguistic concept")
#     definition: str = Field(default="", description="Clear definition of the concept")
#     explanation: str = Field(default="", description="Detailed explanation with context")

#     example1: str = Field(default="", description="First practical example")
#     example2: str = Field(default="", description="Second practical example")
#     example3: str = Field(default="", description="Third practical example")

#     key_points: str = Field(default="", description="Bullet points of key information")
#     related_concepts: str = Field(default="", description="Related NLP concepts")
#     chapter_reference: str = Field(default="", description="Chapter/section reference in SLP3")


# class SLP3Flashcard(BaseModel):
#     """Flashcard schema for Jurafsky SLP3 content."""

#     note_id: int = Field(description="Unique note identifier")
#     model_id: int = Field(description="Anki model identifier")

#     concept: str = Field(default="", description="Main NLP/linguistic concept")
#     definition: str = Field(default="", description="Clear definition of the concept")
#     explanation: str = Field(default="", description="Detailed explanation with context")

#     example1: str = Field(default="", description="First practical example")
#     example2: str = Field(default="", description="Second practical example")
#     example3: str = Field(default="", description="Third practical example")

#     key_points: str = Field(default="", description="Bullet points of key information")
#     related_concepts: str = Field(default="", description="Related NLP concepts")
#     chapter_reference: str = Field(default="", description="Chapter/section reference in SLP3")

#     difficulty_level: str = Field(default="", description="Beginner/Intermediate/Advanced")
#     tags: str = Field(default="", description="Comma-separated tags for organization")

#     def to_text_model(self) -> SLP3FlashcardTextFields:
#         """Convert to text-only model for LLM processing."""
#         return SLP3FlashcardTextFields(
#             concept=self.concept,
#             definition=self.definition,
#             explanation=self.explanation,
#             example1=self.example1,
#             example2=self.example2,
#             example3=self.example3,
#             key_points=self.key_points,
#             related_concepts=self.related_concepts,
#             chapter_reference=self.chapter_reference
#         )

#     def from_text_model(self, text_model: SLP3FlashcardTextFields) -> 'SLP3Flashcard':
#         """Update from text-only model while preserving metadata."""
#         return SLP3Flashcard(
#             note_id=self.note_id,
#             model_id=self.model_id,
#             concept=text_model.concept,
#             definition=text_model.definition,
#             explanation=text_model.explanation,
#             example1=text_model.example1,
#             example2=text_model.example2,
#             example3=text_model.example3,
#             key_points=text_model.key_points,
#             related_concepts=text_model.related_concepts,
#             chapter_reference=text_model.chapter_reference,
#             difficulty_level=self.difficulty_level,
#             tags=self.tags
#         )


# class SLP3Deck(BaseModel):
#     """Collection of SLP3 flashcards with metadata."""

#     name: str = Field(description="Deck name")
#     description: str = Field(description="Deck description")
#     cards: List[SLP3Flashcard] = Field(default_factory=list, description="List of flashcards")

#     def add_card(self, card: SLP3Flashcard) -> None:
#         """Add a flashcard to the deck."""
#         self.cards.append(card)

#     def get_card_count(self) -> int:
#         """Get the number of cards in the deck."""
#         return len(self.cards)
