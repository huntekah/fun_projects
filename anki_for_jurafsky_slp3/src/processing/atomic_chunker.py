from typing import List
from connectors.llm.structured_gemini import LLMClient
from src.models.cards import AtomicCards, CardType, ClozeCard, QACard, EnumerationCard
from src.utils.text_processing import clean_anki_text


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

Active Recall: All flashcards must be framed to force the user to retrieve information from memory. This is best achieved with:
1.  **Cloze Deletions (Preferred):** For facts, definitions, and key components of a concept.
2.  **Q&A :** For high-level 'why' or 'how' explanations that cannot be naturally framed as a cloze.

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
- MathJax Formatting: All mathematical formulas, equations, and variables MUST be formatted using MathJax. Use \(\) for inline math (e.g., \(E=mc^2\)) and \[\] for display/block math.

EXAMPLES OF FILTERING IN ACTION

Input Sentence: "A large system that uses a BPE tokenizer is OpenAI GPT4o."
Decision: Discard. This is a specific instance, not a general principle. It fails the "Prefer General Principles" rule.

Input Sentence: "The original ELIZA-like program's domain was a Rogerian psychologist."
Decision: Discard. This is historical trivia and fails the "Job Interview Test."

Input Sentence: "Because a byte has only 256 possible values, BPE on UTF-8 encoded text will result in no unknown tokens."
Decision: Keep. This explains a key benefit and technical detail ("why") of using BPE on byte-level data. This is a high-value, foundational concept. **Defaulting to Cloze format.**
Generated Card: {{"type": "Cloze", "text": "A key advantage of BPE on UTF-8 encoded text is that since a byte only has 256 possible values, it will result in {{{{c1::no unknown tokens}}}}."}}

Input Sentence: "The core intuition behind using multi-head attention is that each attention head can specialize in attending to different aspects of the input, allowing the model to jointly attend to information from different representation subspaces."
Decision: Keep. This information explains the high-level "why" or "intuition" behind a complex architectural choice. It is not a simple fact. Attempting to force this into a cloze would lose the nuance and atomicity. 
Generated Card:
{{
  "type": "Q&A",
  "q": "What is the core intuition behind using multi-head attention?",
  "a": "Each attention head can specialize in attending to different aspects of the input, allowing the model to jointly attend to information from different representation subspaces."
}}

Input Sentence: "The similarity score in an attention mechanism is the scaled dot-product, calculated as (qi ⋅ kj) / √dk."
Decision: Keep. This is a foundational formula. The formula itself is the key to understanding how attention mechanism works.

Generated Card:
{{
  "type": "Cloze",
  "text": "The similarity score in a Transformer's self-attention is calculated using the scaled dot-product: {{{{c1::\\(\\frac{{q_i \\cdot k_j}}{{\\sqrt{{d_k}}}}\\)}}}}."
}}


BEGIN PROMPT
Based on all the rules and examples above, process the following text chunk:

{chunk}"""

    result = llm_client.generate(prompt, AtomicCards)
    return result.cards


def fix_content(source: str, card: CardType) -> CardType:
    """
    Fix a card using two-stage improvement: content refinement followed by formatting.

    Args:
        source: Original source text for verification
        card: Card to be improved

    Returns:
        Improved flashcard with better content and formatting
    """
    llm_client = LLMClient(model="gemini-2.5-flash")
    
    # Stage 1: Content improvement
    content_prompt = f"""You are a meticulous Senior Machine Learning Engineer and expert educator, acting as a content reviewer for flashcards. 
    Your task is to review and improve a single flashcard by cross-referencing it against its original source text to ensure it is technically flawless, clear, and maximally effective for learning.

You must analyze the given flashcard based on the following **Content Principles**:

1.  **Technical Accuracy & Precision (Verified by Source):**
    * Does the terminology in the card **perfectly align** with the source text?
    * Use the source to correct any imprecise terms (e.g., change "context vectors" to "value vectors" if the source specifies the latter).
    * Ensure all formulas and variables are correctly transcribed from the source, using proper MathJax formatting  Use \\(\\) for inline math (e.g., \\( E = mc^2 \\) ) and \\[\\] for display/block math.
    * You can use basic HTML tags for formatting where appropriate (e.g., `<b>`, `<i>`, `<code>`, `<pre>`).

2.  **Clarity & Conciseness:**
    * Is the card as simple and direct as possible without losing critical meaning from the source?
    * Remove redundant words or awkward phrasing. The final card should be a distilled, learnable fact from the source.

3.  **Preservation of Atomicity:**
    * Does the card still test only ONE discrete piece of information? Do not add new, separate facts from the source.

4.  **Contextual Self-Sufficiency:**
    * Can the card be understood on its own? If the source provides critical context that makes the card understandable, add it.

**TASK:**
1. Carefully read the source text as ground truth
2. Review the input card for content accuracy and clarity
3. Return an improved version focusing on content.

<Source Text>
{source}
</Source Text>

<Input Card>
{card.model_dump_json()}
</Input Card>
"""

    # Get content-improved card
    fixed_card: CardType = llm_client.generate(content_prompt, CardType)
    
    return fixed_card

def fix_formatting(card: CardType) -> CardType:
    """
    Fix the formatting of a flashcard to ensure it is visually clear and professional.

    Args:
        card: Card to be formatted

    Returns:
        Formatted flashcard
    """
    smaller_client = LLMClient(model="gemini-2.5-flash-lite")

    formatting_prompt = f"""You are an expert in educational formatting and presentation for ANKI flashcards. Your task is to take a technically accurate flashcard and apply proper formatting to make it visually clear and professional.

Focus ONLY on formatting improvements:

1. **MathJax Formatting:**
   * Use \\(\\) for inline math (e.g., \\(E=mc^2\\))
   * Use \\[\\] for display/block math for complex formulas
   * Ensure all mathematical notation is properly formatted
   * IMPORTANT \\lt \\gt &lt; &gt; &le; &ge; need to be used instead of < and > symbols inside math equations - using literal `<` and `>` will break HTML rendering.

2. Cloze Conflicts
Cloze deletions are terminated with }}}}, which can conflict with a }}}} appearing in your LaTeX. To prevent LaTeX from being interpreted as a closing cloze marker, you can put a space between any double closing braces that do not indicate the end of the cloze, so

{{{{c1::[$]\frac{{foo}}{{\frac{{bar}}{{baz}}}}[/$] blah blah blah.}}}}
will not work, but

{{{{c1::[$]\frac{{foo}}{{\frac{{bar}}{{baz}} }}[/$] blah blah blah.}}}}
will (and LaTeX ignores spaces in math mode, so your equation will render the same). If you want to avoid adding the extra space into the rendered text (for example, when you are making Cloze cards for learning programming languages), another option is to use a HTML comment when editing the card in HTML mode:

{{{{c1::[$]\frac{{foo}}{{\frac{{bar}}{{baz}}<!-- -->}}[/$] blah blah blah.}}}}
You may use either workaround if you need to use the :: character sequence within the Cloze-deleted text. The first card generated for the following note text will read [type] in C++ is a type-safe union:

{{{{c1::std:<!-- -->:variant::~type~}}}} in C++ is a {{{{c2::type-safe union}}}}


2. **HTML Formatting - Convert ALL formatting to HTML:**
   Always use HTML tags instead of Markdown. Here are the key conversions:
   
   **Common formatting:**
   * Use <b>bold text</b> instead of **bold text**
   * Use <i>italicized text</i> instead of *italicized text*
   * Use <code>code</code> instead of `code`
   * Use <pre><code>multi-line code</code></pre> for code blocks
   * Use the HTML entities &lt;, &gt; and &amp; to encode these characters so that the browser will not interpret them, but MathJax will.
   
eg: "The vocabulary \\(V(p)\\) in <b>top-p sampling</b> is defined as the smallest set of words satisfying the condition: {{{{c1::\\sum_{{w \\in V(p)}} P(w|w_{{&lt;t}}) \\geq p}}}}"
or "P(w|w_{{ \\lt t}}) \\geq p"
or "P(w|w_{{ &lt;t}}) \\geq p"
in case it is really hard to avoid using the literal < character, wrap it with spaces around it.
   
   Same goes for other markdown elements. We aim to use their HTML equivalents like <h1>, <h2>, <ul>, <ol>, <li>, <a>, <hr>, <blockquote>, etc.

3. **Structure & Readability:**
   * Apply consistent formatting throughout the card
   * Make important concepts stand out visually
   * Ensure the formatting enhances learning without being distracting

**IMPORTANT:** Do NOT change the content, meaning, or technical accuracy. Only apply formatting improvements.

<Input Card>
{card.model_dump_json()}
</Input Card>
"""


    fixed_card: CardType = smaller_client.generate(formatting_prompt, CardType)
    
    # Apply all text fixes (HTML escaping and MathJax/Cloze conflicts)
    match fixed_card:
        case QACard():
            fixed_card.q = clean_anki_text(fixed_card.q)
            fixed_card.a = clean_anki_text(fixed_card.a)
        case ClozeCard():
            fixed_card.text = clean_anki_text(fixed_card.text)
        case EnumerationCard():
            fixed_card.prompt = clean_anki_text(fixed_card.prompt)
            fixed_card.items = [clean_anki_text(item) for item in fixed_card.items]
    
    return fixed_card
