import random
from pathlib import Path
from utilities import load_anki_deck, save_anki_deck, copy_non_translation_fields_from_original
from connectors.llm.structured_gemini import LLMClient, VertexAIConfig
from prompt import create_translation_prompt
from schema import AnkiCard, AnkiDeck


def translate_card_with_llm(card: AnkiCard, llm_client: LLMClient) -> AnkiCard:
    """
    Translate a single AnkiCard from German-English to German-Polish using LLM.

    Args:
        card: Original AnkiCard with German-English content
        llm_client: Configured LLM client

    Returns:
        AnkiCard: Translated card with German-Polish content, cleaned of LLM hallucinations
    """
    prompt = create_translation_prompt(card)

    try:
        translated_card = llm_client.generate(prompt, AnkiCard)
        
        # Clean up LLM hallucinations in non-translation fields
        cleaned_card, issues_fixed = copy_non_translation_fields_from_original(translated_card, card)
        
        return cleaned_card
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR translating card {card.note_id}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        print("-" * 80)
        
        return card


def main():
    """Test translation of 3 random Anki cards and save as new deck."""
    import traceback

    try:
        # Load original deck
        original_deck_path = Path(
            "data/B1_Wortliste_DTZ_Goethe_vocabsentensesaudiotranslation.apkg"
        )
        print(f"Loading deck from {original_deck_path}...")

        original_deck = load_anki_deck(original_deck_path)
        print(f"Loaded {original_deck.total_cards} cards from original deck")

        # Select 3 random cards
        # cards_for_translation = random.sample(original_deck.cards, min(20, len(original_deck.cards)))
        cards_for_translation = [card.model_copy() for card in original_deck.cards]
        print(f"Selected {len(cards_for_translation)} random cards for translation")

        # Print original cards
        print("\n=== ORIGINAL CARDS (DE-EN) ===")
        for i, card in enumerate(cards_for_translation, 1):
            print(f"\nCard {i}:")
            print(f"  German: {card.full_source}")
            print(f"  English: {card.base_target}")
            if card.s1_source:
                print(f"  Example DE: {card.s1_source}")
                print(f"  Example EN: {card.s1_target}")

        # Initialize LLM client
        config = VertexAIConfig()
        llm_client = LLMClient(config)
        print(f"\n=== TRANSLATING WITH {config.llm_model} ===")

        # Translate cards
        translated_cards = []
        failed_cards = 0
        total_cleaning_issues = 0
        
        for i, card in enumerate(cards_for_translation, 1):
            print(f"\nTranslating card {i}/{len(cards_for_translation)}...")
            print(f"  German: {card.full_source}")
            print(f"  English: {card.base_target}")
            
            original_card = card.model_copy()  # Keep original for comparison
            translated_card = translate_card_with_llm(card, llm_client)
            translated_cards.append(translated_card)
            
            print(f"  Polish: {translated_card.base_target}")
            
            # Check if translation actually happened (card changed)
            if translated_card.base_target == original_card.base_target:
                failed_cards += 1

        print(f"\n📊 Translation Summary: {len(translated_cards) - failed_cards}/{len(translated_cards)} successful")
        if failed_cards > 0:
            print(f"⚠️  {failed_cards} cards failed to translate (returned unchanged)")

        # Print translated cards
        print("\n=== TRANSLATED CARDS (DE-PL) ===")
        for i, card in enumerate(translated_cards, 1):
            print(f"\nCard {i}:")
            print(f"  German: {card.full_source}")
            print(f"  Polish: {card.base_target}")
            if card.s1_source:
                print(f"  Example DE: {card.s1_source}")
                print(f"  Example PL: {card.s1_target}")
                
            print(card)

        # Create new deck with translated cards
        translated_deck = AnkiDeck(
            cards=translated_cards,
            name="DTZ_Goethe_B1_DE_PL_Sample",
            total_cards=len(translated_cards),
        )

        # Save translated deck
        output_path = Path("data/DTZ_Goethe_B1_DE_PL_Sample.apkg")
        print(f"\n=== SAVING TRANSLATED DECK ===")
        save_anki_deck(translated_deck, output_path, original_deck_path)
        print(f"Saved translated deck to {output_path}")

    except Exception as e:
        print(f"\n💥 FATAL ERROR in main():")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\n🔍 Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        raise  # Re-raise to exit with error code


if __name__ == "__main__":
    main()
