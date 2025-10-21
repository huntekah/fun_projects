"""
LeetCode Anki Deck Creation

This module creates Anki decks from AnkiLeetcodeCard objects using the active recall methodology.
The cards are structured to mimic real problem-solving: front shows the challenge, back shows the solution.
"""

import json
import random
from pathlib import Path
from typing import List

import genanki
from src.models.leetcode_cards import AnkiLeetcodeCard


LEETCODE_CSS = """
/* --------------------------------------------------
   1. VARIABLES & THEME DEFINITIONS
   -------------------------------------------------- */

/* :root contains the default (Day Mode) theme colors */
:root {
    --text-primary: #333;
    --text-secondary: #555;
    --bg-primary: #fcfcfc;
    --bg-secondary: #f5f5f5;
    --border-color: #eee;
    --accent-primary: #007BFF;
    --accent-primary-bg: #e9f7ff;
    --accent-primary-text: #004085;
    --tag-bg: #e9ecef;
    --tag-text: #495057;
}

/* .nightMode overrides the variables for a dark theme */
.nightMode {
    --text-primary: #e0e0e0;
    --text-secondary: #b0b0b0;
    --bg-primary: #2c2c2c;
    --bg-secondary: #3a3a3a;
    --border-color: #444;
    --accent-primary: #58a6ff;
    --accent-primary-bg: #1c3d5e;
    --accent-primary-text: #a8d1ff;
    --tag-bg: #4f5b66;
    --tag-text: #d8dee4;
}

/* --------------------------------------------------
   2. GLOBAL & CARD STYLES
   -------------------------------------------------- */

.card {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 18px;
    text-align: left;
    /* We now use our variables! */
    color: var(--text-primary);
    background-color: var(--bg-primary);
    line-height: 1.6;
}

.card-front, .card-back {
    padding: 25px;
}

pre {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 15px;
    border-radius: 5px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

code {
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 16px;
    /* Code text color needs to be set explicitly */
    color: var(--text-primary);
}

/* --------------------------------------------------
   3. COMPONENT STYLES
   -------------------------------------------------- */

.problem-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.problem-title a {
    text-decoration: none;
    color: inherit;
    font-size: 24px;
    font-weight: 600;
}

.problem-difficulty {
    font-size: 14px;
    padding: 4px 10px;
    border-radius: 15px;
    font-weight: 500;
    color: white; /* White text works on all these backgrounds */
}

/* Difficulty colors are fine as-is */
.difficulty-Easy { background-color: #4CAF50; }
.difficulty-Medium { background-color: #FFC107; }
.difficulty-Hard { background-color: #F44336; }

.problem-description {
    margin-bottom: 20px;
}

/* A more subtle prompt on the front */
.solution-prompt {
    margin-top: 25px;
    padding: 10px 0;
    border-top: 1px solid var(--border-color);
    font-style: italic;
    color: var(--text-secondary);
}

.solution-section {
    margin-bottom: 20px;
    border-left: 3px solid var(--accent-primary);
    padding-left: 15px;
}

.solution-section h3 {
    font-size: 20px;
    color: var(--text-primary);
    margin-top: 0;
}

.solution-tags {
    margin-top: 25px;
    border-top: 1px solid var(--border-color);
    padding-top: 15px;
}

.tag {
    display: inline-block;
    background-color: var(--tag-bg);
    color: var(--tag-text);
    padding: 4px 10px;
    border-radius: 5px;
    font-size: 14px;
    margin-right: 8px;
}
"""

# Define the Anki model for LeetCode cards
leetcode_model = genanki.Model(
    1607392319,  # Fixed unique model ID
    "LeetCode Problem Model",
    fields=[
        {'name': 'ProblemID'},
        {'name': 'Title'},
        {'name': 'URL'},
        {'name': 'Difficulty'},
        {'name': 'ProblemDescription'},
        {'name': 'SolutionType'},
        {'name': 'KeyInsight'},
        {'name': 'Strategy'},
        {'name': 'Code'},
        {'name': 'Complexity'},
        {'name': 'Tags'},
    ],
    templates=[
        {
            'name': 'LeetCode Card',
            'qfmt': '''
                <div class="card-front">
                    <div class="problem-header">
                        <div class="problem-title">
                            <a href="{{URL}}">{{ProblemID}}. {{Title}}</a>
                        </div>
                        <div class="problem-difficulty difficulty-{{Difficulty}}">{{Difficulty}}</div>
                    </div>
                    <div class="problem-description">
                        {{ProblemDescription}}
                    </div>
                    <div class="solution-prompt">
                        Your Task: Try to solve this using a <strong>{{SolutionType}}</strong> approach.
                    </div>
                </div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="card-back">
                    <div class="solution-section">
                        <h3>Solution: {{SolutionType}}</h3>
                    </div>
                    <div class="solution-section">
                        <h3>Key Insight</h3>
                        {{text:KeyInsight}}
                    </div>
                    <div class="solution-section">
                        <h3>Strategy</h3>
                        {{Strategy}}
                    </div>
                    <div class="solution-section">
                        <h3>Implementation</h3>
                        <pre><code>{{Code}}</code></pre>
                    </div>
                    <div class="solution-section">
                        <h3>Complexity</h3>
                        {{Complexity}}
                    </div>
                    <div class="solution-tags">
                        {{Tags}}
                    </div>
                </div>
            ''',
        },
    ],
    css=LEETCODE_CSS,
)



class LeetCodeNote(genanki.Note):
    """Custom Note class with unique GUID generation for LeetCode cards."""
    
    @property
    def guid(self):
        # Create unique ID based on problem ID and code
        return genanki.guid_for(self.fields[0], self.fields[5])


def create_leetcode_note(card: AnkiLeetcodeCard) -> LeetCodeNote:
    """
    Convert an AnkiLeetcodeCard to a genanki Note.
    
    Args:
        card: AnkiLeetcodeCard object with all the solution data
        
    Returns:
        LeetCodeNote ready for adding to an Anki deck
    """
    # Format tags for HTML display
    tags_html = "".join(f'<span class="tag">{tag}</span>' for tag in card.tags)
    
    # Convert line breaks to HTML <br> tags for proper Anki display
    problem_description_html = card.problem_description.replace('\n', '<br>')
    strategy_html = card.strategy.replace('\n', '<br>')
    
    return LeetCodeNote(
        model=leetcode_model,
        fields=[
            card.problem_id,
            card.title,
            card.description_url,
            card.difficulty,
            problem_description_html,
            card.solution_type,
            card.key_insight,
            strategy_html,
            card.code,
            card.complexity,
            tags_html
        ]
    )


def load_anki_cards_from_json(json_file_path: str) -> List[AnkiLeetcodeCard]:
    """
    Load AnkiLeetcodeCard objects from a JSON file.
    
    Args:
        json_file_path: Path to the JSON file containing AnkiLeetcodeCard data
        
    Returns:
        List of validated AnkiLeetcodeCard objects
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        ValidationError: If any card data doesn't match the expected schema
    """
    file_path = Path(json_file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Anki cards file not found: {json_file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Validate each card against the schema
    validated_cards = []
    for i, card_dict in enumerate(raw_data):
        try:
            card = AnkiLeetcodeCard(**card_dict)
            validated_cards.append(card)
        except Exception as e:
            print(f"❌ Failed to validate card at index {i}: {e}")
            print(f"   Card data: {card_dict}")
            continue
    
    print(f"✅ Successfully loaded {len(validated_cards)} out of {len(raw_data)} cards")
    return validated_cards


def create_leetcode_anki_deck(cards: List[AnkiLeetcodeCard], deck_name: str, output_filename: str):
    """
    Create an Anki .apkg file from a list of AnkiLeetcodeCard objects.
    
    Args:
        cards: List of AnkiLeetcodeCard objects
        deck_name: Name for the Anki deck
        output_filename: Path to save the .apkg file
    """
    # Create the deck with a random ID
    deck_id = random.randrange(1 << 30, 1 << 31)
    leetcode_deck = genanki.Deck(deck_id, deck_name)
    
    # Convert each card to a Note and add to deck
    for card in cards:
        note = create_leetcode_note(card)
        leetcode_deck.add_note(note)
    
    # Create the package and save
    anki_package = genanki.Package(leetcode_deck)
    anki_package.models = [leetcode_model]
    
    # Ensure output directory exists
    output_path = Path(output_filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    anki_package.write_to_file(output_filename)
    print(f"✅ Successfully created Anki deck: {output_filename}")
    print(f"📊 Deck contains {len(cards)} cards")
    
    # Show breakdown by solution type
    solution_types = {}
    for card in cards:
        solution_types[card.solution_type] = solution_types.get(card.solution_type, 0) + 1
    
    print(f"🎯 Solution type breakdown:")
    for sol_type, count in sorted(solution_types.items()):
        print(f"   {sol_type}: {count} cards")


def main():
    """Example usage - create deck from NeetCode 150 Anki cards."""
    input_file = "data/neetcode/neetcode_150_anki_cards.json"
    output_file = "data/neetcode/neetcode_150.apkg"
    deck_name = "NeetCode 150 - LeetCode Problems"
    
    try:
        print("📂 Loading Anki cards from JSON...")
        cards = load_anki_cards_from_json(input_file)
        
        if not cards:
            print("❌ No valid cards found!")
            return
        
        print("🎴 Creating Anki deck...")
        create_leetcode_anki_deck(cards, deck_name, output_file)
        
        print("✅ Deck creation completed successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Make sure to run neetcode_pipeline.py first to generate the cards")
    except Exception as e:
        print(f"❌ Deck creation failed: {e}")
        raise


if __name__ == "__main__":
    main()