from schema import AnkiCard


def create_translation_prompt(card: AnkiCard) -> str:
    """
    Create a prompt for translating a German-English Anki card to German-Polish.

    Args:
        card: The original AnkiCard with German-English content

    Returns:
        str: Formatted prompt for LLM translation
    """

    prompt = f"""You are a professional German-Polish translator working on creating German-Polish language learning flashcards for DTZ (Deutsch-Test für Zuwanderer) Goethe B1 level vocabulary.

Your task is to translate ALL English content in this Anki flashcard to Polish, while keeping all German content exactly the same.

ORIGINAL CARD (German-English):
- German word/phrase (full_d): {card.full_d}
- English translation (base_e): {card.base_e}
- German base form (base_d): {card.base_d}
- German article (artikel_d): {card.artikel_d}
- German plural (plural_d): {card.plural_d}
- Audio text (audio_text_d): {card.audio_text_d}

Example sentences:
- German sentence 1 (s1): {card.s1}
- English translation 1 (s1e): {card.s1e}
- German sentence 2 (s2): {card.s2}
- English translation 2 (s2e): {card.s2e}
- German sentence 3 (s3): {card.s3}
- English translation 3 (s3e): {card.s3e}
- German sentence 4 (s4): {card.s4}
- English translation 4 (s4e): {card.s4e}
- German sentence 5 (s5): {card.s5}
- English translation 5 (s5e): {card.s5e}
- German sentence 6 (s6): {card.s6}
- English translation 6 (s6e): {card.s6e}
- German sentence 7 (s7): {card.s7}
- English translation 7 (s7e): {card.s7e}
- German sentence 8 (s8): {card.s8}
- English translation 8 (s8e): {card.s8e}
- German sentence 9 (s9): {card.s9}
- English translation 9 (s9e): {card.s9e}

TRANSLATION REQUIREMENTS:
1. Translate ALL English content (base_e, s1e, s2e, s3e, s4e, s5e, s6e, s7e, s8e, s9e) to Polish
2. Keep ALL German content exactly the same (full_d, base_d, artikel_d, plural_d, audio_text_d, s1, s2, s3, s4, s5, s6, s7, s8, s9)
3. Keep all other fields unchanged (note_id, model_id, original_order, audio fields)
4. Ensure Polish translations are accurate and appropriate for B1 level learners
5. Use natural, contemporary Polish that matches the formality level of the original English
6. For grammar terms or linguistic concepts, use standard Polish linguistic terminology
7. If an English field is empty, leave the corresponding Polish field empty

CONTEXT: This is for German language learners who speak Polish as their native language, studying for the DTZ (Deutsch-Test für Zuwanderer) at B1 level.

Please provide the complete translated card with all fields filled out appropriately."""

    return prompt


def create_batch_translation_prompt(cards: list[AnkiCard], batch_size: int = 5) -> str:
    """
    Create a prompt for translating multiple German-English Anki cards to German-Polish in batch.

    Args:
        cards: List of AnkiCards with German-English content
        batch_size: Number of cards to process in one batch

    Returns:
        str: Formatted prompt for batch LLM translation
    """

    if len(cards) > batch_size:
        cards = cards[:batch_size]

    prompt = f"""You are a professional German-Polish translator working on creating German-Polish language learning flashcards for DTZ (Deutsch-Test für Zuwanderer) Goethe B1 level vocabulary.

Your task is to translate ALL English content in these {len(cards)} Anki flashcards to Polish, while keeping all German content exactly the same.

TRANSLATION REQUIREMENTS:
1. Translate ALL English content (base_e, s1e, s2e, s3e, s4e, s5e, s6e, s7e, s8e, s9e) to Polish
2. Keep ALL German content exactly the same (full_d, base_d, artikel_d, plural_d, audio_text_d, s1, s2, s3, s4, s5, s6, s7, s8, s9)
3. Keep all other fields unchanged (note_id, model_id, original_order, audio fields)
4. Ensure Polish translations are accurate and appropriate for B1 level learners
5. Use natural, contemporary Polish that matches the formality level of the original English
6. For grammar terms or linguistic concepts, use standard Polish linguistic terminology
7. If an English field is empty, leave the corresponding Polish field empty

CARDS TO TRANSLATE:

"""

    for i, card in enumerate(cards, 1):
        prompt += f"""
CARD {i}:
- German word/phrase (full_d): {card.full_d}
- English translation (base_e): {card.base_e}
- German base form (base_d): {card.base_d}
- Example sentences and their English translations:
"""

        # Add non-empty example sentences
        examples = [
            (card.s1, card.s1e),
            (card.s2, card.s2e),
            (card.s3, card.s3e),
            (card.s4, card.s4e),
            (card.s5, card.s5e),
            (card.s6, card.s6e),
            (card.s7, card.s7e),
            (card.s8, card.s8e),
            (card.s9, card.s9e),
        ]

        for j, (german_ex, english_ex) in enumerate(examples, 1):
            if german_ex.strip():
                prompt += f"  - German example {j}: {german_ex}\n"
                prompt += f"  - English translation {j}: {english_ex}\n"

    prompt += f"""

CONTEXT: This is for German language learners who speak Polish as their native language, studying for the DTZ (Deutsch-Test für Zuwanderer) at B1 level.

Please provide the complete translated cards with all fields filled out appropriately, maintaining the same structure and field names as the original cards."""

    return prompt
