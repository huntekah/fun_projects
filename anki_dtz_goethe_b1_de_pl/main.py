import random
from pathlib import Path
from utilities import load_anki_deck, save_anki_deck
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
        AnkiCard: Translated card with German-Polish content
    """
    prompt = create_translation_prompt(card)
    
    try:
        translated_card = llm_client.generate(prompt, AnkiCard)
        return translated_card
    except Exception as e:
        print(f"Error translating card {card.note_id}: {e}")
        # Return original card if translation fails
        return card


def main():
    """Test translation of 3 random Anki cards and save as new deck."""
    
    # Load original deck
    original_deck_path = Path("data/B1_Wortliste_DTZ_Goethe_vocabsentensesaudiotranslation.apkg")
    print(f"Loading deck from {original_deck_path}...")
    
    original_deck = load_anki_deck(original_deck_path)
    print(f"Loaded {original_deck.total_cards} cards from original deck")
    
    # Select 3 random cards
    random_cards = random.sample(original_deck.cards, min(3, len(original_deck.cards)))
    print(f"Selected {len(random_cards)} random cards for translation")
    
    # Print original cards
    print("\n=== ORIGINAL CARDS (DE-EN) ===")
    for i, card in enumerate(random_cards, 1):
        print(f"\nCard {i}:")
        print(f"  German: {card.full_d}")
        print(f"  English: {card.base_e}")
        if card.s1:
            print(f"  Example DE: {card.s1}")
            print(f"  Example EN: {card.s1e}")
    
    # Initialize LLM client
    config = VertexAIConfig()
    llm_client = LLMClient(config)
    print(f"\n=== TRANSLATING WITH {config.llm_model} ===")
    
    # Translate cards
    translated_cards = []
    for i, card in enumerate(random_cards, 1):
        print(f"Translating card {i}/{len(random_cards)}...")
        translated_card = translate_card_with_llm(card, llm_client)
        translated_cards.append(translated_card)
    
    # Print translated cards
    print("\n=== TRANSLATED CARDS (DE-PL) ===")
    for i, card in enumerate(translated_cards, 1):
        print(f"\nCard {i}:")
        print(f"  German: {card.full_d}")
        print(f"  Polish: {card.base_e}")
        if card.s1:
            print(f"  Example DE: {card.s1}")
            print(f"  Example PL: {card.s1e}")
    
    # Create new deck with translated cards
    translated_deck = AnkiDeck(
        cards=translated_cards,
        name="DTZ_Goethe_B1_DE_PL_Sample",
        total_cards=len(translated_cards)
    )
    
    # Save translated deck
    output_path = Path("data/DTZ_Goethe_B1_DE_PL_Sample.apkg")
    print(f"\n=== SAVING TRANSLATED DECK ===")
    save_anki_deck(translated_deck, output_path, original_deck_path)
    print(f"Saved translated deck to {output_path}")


if __name__ == "__main__":
    main()
