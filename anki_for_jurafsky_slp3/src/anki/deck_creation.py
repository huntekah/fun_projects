import random
import warnings
from typing import List
from pathlib import Path

import genanki
from src.models.cards import CardType, QACard, ClozeCard, EnumerationCard


def print_warning_details(w: List[warnings.WarningMessage], card: CardType) -> None:
    """Print details about the card that triggered a warning."""
    print(f"\n⚠️  Warning triggered by card:")
    print(f"Card type: {type(card).__name__}")
    print(f"Card: {card}")
    print(f"Warning: {w[0].message}")
    print("=" * 50)





# A simple, clean CSS for all card types
SHARED_CSS = '''
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}
.card-front, .card-back {
    padding: 20px;
}
.card-back ul, .card-back ol {
    display: inline-block;
    text-align: left;
}
'''

# Model for Basic Q&A Cards
basic_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31),  # Unique model ID
    'Simple Q&A Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
    ],
    templates=[
        {
            'name': 'Q&A Card',
            'qfmt': '<div class="card-front">{{Question}}</div>',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="card-back">{{Answer}}</div>',
        },
    ],
    css=SHARED_CSS
)

# Model for Enumeration Cards
enumeration_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31), # Unique model ID
    'Enumeration Model',
    fields=[
        {'name': 'Prompt'},
        {'name': 'ItemsHTML'}, # We will store the list as pre-formatted HTML
    ],
    templates=[
        {
            'name': 'Enumeration Card',
            'qfmt': '<div class="card-front">{{Prompt}}</div>',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="card-back">{{ItemsHTML}}</div>',
        },
    ],
    css=SHARED_CSS
)


def create_anki_deck(cards: List[CardType], deck_name: str, output_filename: str):
    """
    Creates an Anki .apkg file from a list of card objects.

    :param cards: A list of QACard, ClozeCard, or EnumerationCard objects.
    :param deck_name: The name of the deck to be created.
    :param output_filename: The path to save the .apkg file (e.g., 'output.apkg').
    """
    deck_id = random.randrange(1 << 30, 1 << 31)
    anki_deck = genanki.Deck(deck_id, deck_name)
    
    # We need to collect all models used in the deck
    models_in_use = {basic_model, enumeration_model, genanki.CLOZE_MODEL}

    for card in cards:
        note = None
        if isinstance(card, QACard):
            note = genanki.Note(
                model=basic_model,
                fields=[card.q, card.a]
            )
        elif isinstance(card, ClozeCard):
            note = genanki.Note(
                # Use the built-in Cloze model
                model=genanki.CLOZE_MODEL,
                fields=[card.text]
            )
        elif isinstance(card, EnumerationCard):
            # Convert the list of items into an HTML list
            list_tag = 'ol' if card.ordered else 'ul'
            items_html = f"<{list_tag}>" + "".join(f"<li>{item}</li>" for item in card.items) + f"</{list_tag}>"
            note = genanki.Note(
                model=enumeration_model,
                fields=[card.prompt, items_html]
            )
        
        if note:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                anki_deck.add_note(note)
                if w:
                    print_warning_details(w, card)

    # Create the package
    anki_package = genanki.Package(anki_deck)
    
    # Add all the models that were used to the package
    anki_package.models = list(models_in_use)

    # Ensure output directory exists
    output_path = Path(output_filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the package to a file
    anki_package.write_to_file(output_filename)
    print(f"Successfully created Anki deck at: {output_filename}")
    print(f"Deck contains {len(cards)} cards")