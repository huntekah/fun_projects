from schema import AnkiCard, AnkiCardTextFields


def create_text_translation_prompt(text_model: AnkiCardTextFields) -> str:
    """
    Create a prompt for translating AnkiCardTextFields from German-English to German-Polish.
    This is more efficient than translating the full AnkiCard since it excludes metadata.

    Args:
        text_model: The text-only AnkiCardTextFields with German-English content

    Returns:
        str: Formatted prompt for LLM translation
    """

    prompt = f"""You are a professional German-Polish translator working on creating German-Polish language learning flashcards for DTZ (Deutsch-Test für Zuwanderer) Goethe B1 level vocabulary.

Your task is to provide DIRECT Polish translations for ALL German content. The English translations are provided as reference context to help you understand the meaning, but you should translate FROM GERMAN TO POLISH directly, not from English to Polish.

IMPORTANT: Translate German → Polish directly. Use English only as reference context to understand meaning.

ORIGINAL FLASHCARD DATA:
- German word/phrase (full_source): {text_model.full_source}
- German base form (base_source): {text_model.base_source}
- English reference (base_target): {text_model.base_target} ← USE AS CONTEXT ONLY
- German article (artikel_d): {text_model.artikel_d}
- German plural (plural_d): {text_model.plural_d}
- Audio text (audio_text_d): {text_model.audio_text_d}

German example sentences with English reference context:
- German sentence 1: {text_model.s1_source}
  English reference: {text_model.s1_target} ← USE AS CONTEXT ONLY
- German sentence 2: {text_model.s2_source}
  English reference: {text_model.s2_target} ← USE AS CONTEXT ONLY
- German sentence 3: {text_model.s3_source}
  English reference: {text_model.s3_target} ← USE AS CONTEXT ONLY
- German sentence 4: {text_model.s4_source}
  English reference: {text_model.s4_target} ← USE AS CONTEXT ONLY
- German sentence 5: {text_model.s5_source}
  English reference: {text_model.s5_target} ← USE AS CONTEXT ONLY
- German sentence 6: {text_model.s6_source}
  English reference: {text_model.s6_target} ← USE AS CONTEXT ONLY
- German sentence 7: {text_model.s7_source}
  English reference: {text_model.s7_target} ← USE AS CONTEXT ONLY
- German sentence 8: {text_model.s8_source}
  English reference: {text_model.s8_target} ← USE AS CONTEXT ONLY
- German sentence 9: {text_model.s9_source}
  English reference: {text_model.s9_target} ← USE AS CONTEXT ONLY

TRANSLATION APPROACH:
1. **Primary task**: Translate each German text DIRECTLY to Polish
2. **English role**: Use English translations only as reference context to understand meaning and nuance
3. **Avoid translation chains**: Do NOT translate English to Polish - translate German to Polish
4. **Quality goal**: Produce natural, idiomatic Polish that accurately conveys the German meaning

TRANSLATION REQUIREMENTS:
1. Provide direct German→Polish translations for ALL target fields (base_target, s1_target, s2_target, s3_target, s4_target, s5_target, s6_target, s7_target, s8_target, s9_target)
2. Keep ALL German source content exactly the same (full_source, base_source, artikel_d, plural_d, audio_text_d, s1_source, s2_source, s3_source, s4_source, s5_source, s6_source, s7_source, s8_source, s9_source)
3. Use English translations as context to understand meaning, register, and nuance
4. Ensure Polish translations are natural, idiomatic, and appropriate for B1 level learners
5. Match the formality and register of the German original (not the English)
6. For grammar terms or linguistic concepts, use standard Polish linguistic terminology
7. If a German source field is empty, leave the corresponding Polish target field empty

CONTEXT: This is for German language learners who speak Polish as their native language, studying for the DTZ (Deutsch-Test für Zuwanderer) at B1 level. They need accurate, natural Polish translations that help them understand German vocabulary and usage patterns.

Please provide the complete result with all fields filled out appropriately using the same field names (source/target structure)."""

    return prompt


def create_translation_prompt(card: AnkiCard) -> str:
    """
    Create a prompt for translating a German-English Anki card to German-Polish.

    Args:
        card: The original AnkiCard with German-English content

    Returns:
        str: Formatted prompt for LLM translation
    """

    prompt = f"""You are a professional German-Polish translator working on creating German-Polish language learning flashcards for DTZ (Deutsch-Test für Zuwanderer) Goethe B1 level vocabulary.

Your task is to translate ALL target language content (currently English) in this Anki flashcard to Polish, while keeping all source language content (German) exactly the same.

ORIGINAL CARD (German-English):
- German word/phrase (full_source): {card.full_source}
- English translation (base_target): {card.base_target}
- German base form (base_source): {card.base_source}
- German article (artikel_d): {card.artikel_d}
- German plural (plural_d): {card.plural_d}
- Audio text (audio_text_d): {card.audio_text_d}

Example sentences:
- German sentence 1 (s1_source): {card.s1_source}
- English translation 1 (s1_target): {card.s1_target}
- German sentence 2 (s2_source): {card.s2_source}
- English translation 2 (s2_target): {card.s2_target}
- German sentence 3 (s3_source): {card.s3_source}
- English translation 3 (s3_target): {card.s3_target}
- German sentence 4 (s4_source): {card.s4_source}
- English translation 4 (s4_target): {card.s4_target}
- German sentence 5 (s5_source): {card.s5_source}
- English translation 5 (s5_target): {card.s5_target}
- German sentence 6 (s6_source): {card.s6_source}
- English translation 6 (s6_target): {card.s6_target}
- German sentence 7 (s7_source): {card.s7_source}
- English translation 7 (s7_target): {card.s7_target}
- German sentence 8 (s8_source): {card.s8_source}
- English translation 8 (s8_target): {card.s8_target}
- German sentence 9 (s9_source): {card.s9_source}
- English translation 9 (s9_target): {card.s9_target}

TRANSLATION REQUIREMENTS:
1. Translate ALL target language content (base_target, s1_target, s2_target, s3_target, s4_target, s5_target, s6_target, s7_target, s8_target, s9_target) from English to Polish
2. Keep ALL source language content exactly the same (full_source, base_source, artikel_d, plural_d, audio_text_d, s1_source, s2_source, s3_source, s4_source, s5_source, s6_source, s7_source, s8_source, s9_source)
3. Keep ALL metadata fields unchanged (note_id, model_id, original_order)
4. Keep ALL audio fields unchanged - copy them exactly as they are (base_audio, s1_audio, s2_audio, s3_audio, s4_audio, s5_audio, s6_audio, s7_audio, s8_audio, s9_audio)
5. NEVER output "string" or placeholder text - copy the original values exactly
6. Ensure Polish translations are accurate and appropriate for B1 level learners
7. Use natural, contemporary Polish that matches the formality level of the original English
8. For grammar terms or linguistic concepts, use standard Polish linguistic terminology
9. If a target language field is empty, leave the corresponding Polish field empty

CONTEXT: This is for German language learners who speak Polish as their native language, studying for the DTZ (Deutsch-Test für Zuwanderer) at B1 level.

Please provide the complete translated card with all fields filled out appropriately using the same field names (source/target structure)."""

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

Your task is to translate ALL target language content (currently English) in these {len(cards)} Anki flashcards to Polish, while keeping all source language content (German) exactly the same.

TRANSLATION REQUIREMENTS:
1. Translate ALL target language content (base_target, s1_target, s2_target, s3_target, s4_target, s5_target, s6_target, s7_target, s8_target, s9_target) from English to Polish
2. Keep ALL source language content exactly the same (full_source, base_source, artikel_d, plural_d, audio_text_d, s1_source, s2_source, s3_source, s4_source, s5_source, s6_source, s7_source, s8_source, s9_source)
3. Keep ALL metadata fields unchanged (note_id, model_id, original_order)
4. Keep ALL audio fields unchanged - copy them exactly as they are (base_audio, s1_audio, s2_audio, s3_audio, s4_audio, s5_audio, s6_audio, s7_audio, s8_audio, s9_audio)
5. NEVER output "string" or placeholder text - copy the original values exactly
6. Ensure Polish translations are accurate and appropriate for B1 level learners
7. Use natural, contemporary Polish that matches the formality level of the original English
8. For grammar terms or linguistic concepts, use standard Polish linguistic terminology
9. If a target language field is empty, leave the corresponding Polish field empty

CARDS TO TRANSLATE:

"""

    for i, card in enumerate(cards, 1):
        prompt += f"""
CARD {i}:
- German word/phrase (full_source): {card.full_source}
- English translation (base_target): {card.base_target}
- German base form (base_source): {card.base_source}
- Example sentences and their translations:
"""

        # Add non-empty example sentences
        examples = [
            (card.s1_source, card.s1_target),
            (card.s2_source, card.s2_target),
            (card.s3_source, card.s3_target),
            (card.s4_source, card.s4_target),
            (card.s5_source, card.s5_target),
            (card.s6_source, card.s6_target),
            (card.s7_source, card.s7_target),
            (card.s8_source, card.s8_target),
            (card.s9_source, card.s9_target),
        ]

        for j, (source_ex, target_ex) in enumerate(examples, 1):
            if source_ex and source_ex.strip():
                prompt += f"  - German example {j} (s{j}_source): {source_ex}\n"
                prompt += f"  - English translation {j} (s{j}_target): {target_ex}\n"

    prompt += f"""

CONTEXT: This is for German language learners who speak Polish as their native language, studying for the DTZ (Deutsch-Test für Zuwanderer) at B1 level.

Please provide the complete translated cards with all fields filled out appropriately, maintaining the same source/target field structure."""

    return prompt
