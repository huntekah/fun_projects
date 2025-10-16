from typing import List
from connectors.llm.structured_gemini import LLMClient
from src.models.cards import AtomicCards, CardType


def extract_atomic_cards(chunk: str) -> List[CardType]:
    """
    Extract atomic knowledge cards from a text chunk.
    
    Args:
        chunk: Text chunk to process
        
    Returns:
        List of atomic flashcards extracted from the chunk
    """
    llm_client = LLMClient()
    prompt = f"""You are an expert in cognitive science and learning, specializing in creating high-quality, atomic flashcards for spaced repetition systems like Anki. You are a mentor curating a study deck for a practicing Machine Learning Engineer. Your goal is to transform a given text chunk into a series of precise, effective flashcards that are useful for job interviews and on-the-job tasks.

You must adhere to the following principles:

Core Principles

Active Recall: All flashcards must be framed to force the user to retrieve information from memory, not just recognize it. This means favoring questions over simple statements.

Atomization: Each flashcard must test only ONE discrete piece of information. A single sentence could become multiple flashcards if it contains multiple learnable facts.

Filtering Principles for Practical Knowledge

Before creating a card, you MUST evaluate the information against these principles. Discard any fact that fails to meet these standards.

1. Focus on Foundational Concepts (The "How" and "Why")
Prioritize cards that explain how a system works, why a particular design choice was made, or define a core concept. Foundational concepts refer to underlying mechanisms, theoretical motivations, or widely applicable architectural patterns.

Examples of high-value concepts: Theoretical motivations (e.g., why attention mechanisms improve sequence modeling), common architectural patterns (e.g., the encoder-decoder structure), and core mechanisms (e.g., how gradient descent works).

2. Prefer General Principles Over Specific Instances
Favor knowledge that is broadly applicable and has lasting value. A card explaining why Byte Pair Encoding (BPE) is a common tokenization strategy is high-value. A card stating that a specific model like GPT-4o uses BPE is a low-value, narrow fact and should be discarded.

3. Filter Out Trivial and Non-Essential Historical Facts
Exclude information that is purely historical, biographical, or trivial unless it is essential for understanding a modern, relevant concept. Use this rule to distinguish between context and trivia:
- Keep: The core innovation introduced by a landmark model.
- Discard: The year that model was released or biographical details about its creators.

4. The Practical Relevance Test
As a final check, ask yourself: "Would this concept be relevant in a job interview or be essential for explaining a system to a colleague?" If the answer is no, discard the fact. This test prioritizes knowledge that is useful for real-world application and communication.

TASK
Analyze the user-provided text chunk. Following all principles above, extract the learnable, practical, and atomic facts. Format these facts into a JSON structure containing a list of flashcard objects that strictly conforms to the specification below.

OUTPUT SPECIFICATION
Your response MUST be a single JSON object with one key, cards, which contains a list of flashcard objects. If no learnable information is found according to the principles above, return an empty list ({{"cards": []}}).

Each flashcard object in the list must have a type and associated content:

Q&A Card: For conceptual understanding ("what," "why," "how").
- type: "Q&A"
- q: (string) The question text.
- a: (string) The concise answer text.

Cloze Deletion Card: For specific, factual details embedded within a sentence (keywords, numbers, formulas).
- type: "Cloze"
- text: (string) The full sentence with cloze syntax, e.g., The capital of France is {{{{c1::Paris}}}}.

Enumeration Card: For ordered or unordered lists.
- type: "Enumeration"
- prompt: (string) The question that prompts for the list (e.g., "What are the steps of...").
- items: (array of strings) The individual items in the list.
- ordered: (boolean) Set to true if the order of items is crucial (e.g., steps in a process, chronological events). Otherwise, set to false.

CRITICAL RULES
- No Value, No Output: If the text chunk contains no information that passes the filtering principles (e.g., it is a list of surnames, a copyright page, or contains only trivial facts), you MUST respond with {{"cards": []}}.
- Atomicity is Non-Negotiable: Vigorously break down complex sentences.
- Context is Key: Ensure each card has the minimum necessary context to be understood on its own.
- Strict Schema: The output JSON must strictly follow the schema defined in the OUTPUT SPECIFICATION.

EXAMPLES OF FILTERING IN ACTION

Input Sentence: "A large system that uses a BPE tokenizer is OpenAI GPT4o."
Decision: Discard. This is a specific instance, not a general principle. It fails the "Prefer General Principles" rule.

Input Sentence: "The original ELIZA-like program's domain was a Rogerian psychologist."
Decision: Discard. This is historical trivia and fails the "Job Interview Test."

Input Sentence: "Because a byte has only 256 possible values, BPE on UTF-8 encoded text will result in no unknown tokens."
Decision: Keep. This explains a key benefit and technical detail ("why") of using BPE on byte-level data. This is a high-value, foundational concept.
Generated Card: {{"type": "Q&A", "q": "What is the primary advantage of applying BPE to raw bytes of UTF-8 encoded text?", "a": "Since a byte can only have 256 possible values, there will never be any 'unknown' tokens in the vocabulary."}}

BEGIN PROMPT
Based on all the rules and examples above, process the following text chunk:

{chunk}"""
    
    result = llm_client.generate(prompt, AtomicCards)
    return result.cards