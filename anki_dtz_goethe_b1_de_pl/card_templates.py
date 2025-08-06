"""
Anki card templates for DTZ Goethe B1 German-Polish deck.
Based on the original DTZ deck structure, with an improved layout
and controlled audio autoplay, including Polish audio support.
"""

# Subdeck IDs for organizing cards
DECK_ID_MAIN = 1752932927500           # Main parent deck
DECK_ID_RECOGNITION = 1754301712001    # 01 Recognition (German → Polish)
DECK_ID_PRODUCTION =  1754301712002     # 02 Production (Polish → German)  
DECK_ID_LISTENING = 1754301712003      # 03 Listening Comprehension (Audio → Text)
DECK_ID_SENTENCE_PROD = 1754301712004  # 04 Sentence Production (Polish → German sentences)

# Updated fields list includes Polish audio fields
DTZ_MODEL_FIELDS = [
    {"name": "frequency_rank"},
    {"name": "full_source"},
    {"name": "base_target"},
    {"name": "base_source"},
    {"name": "artikel_d"},
    {"name": "plural_d"},
    {"name": "audio_text_d"},
    {"name": "s1_source"},
    {"name": "s1_target"},
    {"name": "s2_source"},
    {"name": "s2_target"},
    {"name": "s3_source"},
    {"name": "s3_target"},
    {"name": "s4_source"},
    {"name": "s4_target"},
    {"name": "s5_source"},
    {"name": "s5_target"},
    {"name": "s6_source"},
    {"name": "s6_target"},
    {"name": "s7_source"},
    {"name": "s7_target"},
    {"name": "s8_source"},
    {"name": "s8_target"},
    {"name": "s9_source"},
    {"name": "s9_target"},
    {"name": "original_order"},
    {"name": "full_source_audio"},
    {"name": "base_audio"},
    {"name": "s1_audio"},
    {"name": "s2_audio"},
    {"name": "s3_audio"},
    {"name": "s4_audio"},
    {"name": "s5_audio"},
    {"name": "s6_audio"},
    {"name": "s7_audio"},
    {"name": "s8_audio"},
    {"name": "s9_audio"},
    {"name": "base_target_audio"},
    {"name": "s1_target_audio"},
    {"name": "s2_target_audio"},
    {"name": "s3_target_audio"},
    {"name": "s4_target_audio"},
    {"name": "s5_target_audio"},
    {"name": "s6_target_audio"},
    {"name": "s7_target_audio"},
    {"name": "s8_target_audio"},
    {"name": "s9_target_audio"},
]

# === SEPARATE MODEL DEFINITIONS FOR EACH SUBDECK ===

# Recognition Model (German → Polish)
DTZ_RECOGNITION_TEMPLATES = [
    {
        "name": "German to Polish",
        # --- FRONT ---
        # Shows article/plural for nouns and a context sentence with audio.
        # {{base_audio}} will autoplay here.
        "qfmt": """
<div class="word-title">{{full_source}} {{full_source_audio}}</div>

<hr class="faint-hr">
<div class="hint">{{s1_source}} {{s1_audio}}</div>
""",
        # --- BACK ---
        # The main audio {{base_audio}} won't replay automatically because it was on the front.
        # The silence hack prevents the example sentence audio from autoplaying.
        "afmt": """
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<div class="main-info">
    <div class="word-title">{{full_source}}</div>
    <div class="answer">{{base_target}} {{base_target_audio}}</div>
</div>
<hr>
<div class="example-pair">
    <div class="example">{{s1_source}}</div>
    <div class="example-target">{{s1_target}} {{s1_target_audio}}</div>
</div>

{{#s2_source}}
<div class="example-pair">
    <div class="example">{{s2_source}} {{s2_audio}}</div>
    <div class="example-target">{{s2_target}} {{s2_target_audio}}</div>
</div>
{{/s2_source}}

{{#s3_source}}
<details>
    <summary>Więcej Przykładów (More Examples)</summary>
    <div class="examples-section">
        <div class="example-pair">
            <div class="example">{{s3_source}} {{s3_audio}}</div>
            <div class="example-target">{{s3_target}}</div>
        </div>
        {{#s4_source}}
            <div class="example-pair">
                <div class="example">{{s4_source}} {{s4_audio}}</div>
                <div class="example-target">{{s4_target}}</div>
            </div>
        {{/s4_source}}
        {{#s5_source}}
            <div class="example-pair">
                <div class="example">{{s5_source}} {{s5_audio}}</div>
                <div class="example-target">{{s5_target}}</div>
            </div>
        {{/s5_source}}
        {{#s6_source}}
            <div class="example-pair">
                <div class="example">{{s6_source}} {{s6_audio}}</div>
                <div class="example-target">{{s6_target}}</div>
            </div>
        {{/s6_source}}
        {{#s7_source}}
            <div class="example-pair">
                <div class="example">{{s7_source}} {{s7_audio}}</div>
                <div class="example-target">{{s7_target}}</div>
            </div>
        {{/s7_source}}
        {{#s8_source}}
            <div class="example-pair">
                <div class="example">{{s8_source}} {{s8_audio}}</div>
                <div class="example-target">{{s8_target}}</div>
            </div>
        {{/s8_source}}
        {{#s9_source}}
            <div class="example-pair">
                <div class="example">{{s9_source}} {{s9_audio}}</div>
                <div class="example-target">{{s9_target}}</div>
            </div>
        {{/s9_source}}
    </div>
</details>
{{/s3_source}}
""",
    },
]

# Production Model (Polish → German)  
DTZ_PRODUCTION_TEMPLATES = [
    {
        "name": "Polish to German",
        # --- FRONT ---
        # Polish text with audio and context sentence hint.
        "qfmt": """
<div class="question">{{base_target}} {{base_target_audio}}</div>

<div class="hint">Hint: "{{s1_target}}"</div>
""",
        # --- BACK ---
        # On this card, {{base_audio}} is new, so it will autoplay.
        # The silence hack is placed immediately after it to prevent the subsequent
        # example sentence audio files from autoplaying.
        "afmt": """
<div class="main-info">
    <div class="answer">{{full_source}} {{full_source_audio}}</div>
    <div style="display:none">[sound:_1-minute-of-silence.mp3]</div>
    <div class="hint">{{base_target}} {{base_target_audio}}</div>
</div>
<hr>
<div class="examples-section">
    <div class="section-title">Beispiel</div>
    {{#s1_source}}
        <div class="example">{{s1_source}} {{s1_audio}}</div>
    {{/s1_source}}
</div>
""",
    },
]

# Listening Comprehension Model (Audio → Text)
DTZ_LISTENING_TEMPLATES = []

# Generate listening templates for s1-s9
for i in range(1, 10):
    DTZ_LISTENING_TEMPLATES.append({
        "name": f"Listening S{i}",
        "qfmt": f"""
{{{{#s{i}_source}}}}
<div class="hint">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{{{s{i}_audio}}}}</div>
{{{{/s{i}_source}}}}
""",
        "afmt": f"""
{{{{#s{i}_source}}}}
<div class="listening-answer">
    <div class="answer">🇩🇪 {{{{s{i}_source}}}}</div>
    <div class="example-target">🇵🇱 {{{{s{i}_target}}}} {{{{s{i}_target_audio}}}}</div>
</div>
{{{{/s{i}_source}}}}
""",
    })

# Sentence Production Model (Polish → German sentences)
DTZ_SENTENCE_PRODUCTION_TEMPLATES = []

# Generate sentence production templates for s1-s9
for i in range(1, 10):
    DTZ_SENTENCE_PRODUCTION_TEMPLATES.append({
        "name": f"Sentence Production S{i}",
        "qfmt": f"""
{{{{#s{i}_target}}}}
<div class="hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{{{s{i}_target}}}} {{{{s{i}_target_audio}}}}</div>
{{{{/s{i}_target}}}}
""",
        "afmt": f"""
{{{{#s{i}_target}}}}
<div class="hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{{{s{i}_target}}}}</div>
<hr>
<div class="answer">🇩🇪 {{{{s{i}_source}}}} {{{{s{i}_audio}}}}</div>
{{{{/s{i}_target}}}}
""",
    })

# === LEGACY UNIFIED MODEL (for backwards compatibility) ===
DTZ_CARD_TEMPLATES = [
    {
        "name": "German to Polish",
        # --- FRONT ---
        # Shows article/plural for nouns and a context sentence with audio.
        # {{base_audio}} will autoplay here.
        "qfmt": """
<div class="german-word-title">{{full_source}} {{full_source_audio}}</div>

<hr class="faint-hr">
<div class="example-context">{{s1_source}} {{s1_audio}}</div>
""",
        # --- BACK ---
        # The main audio {{base_audio}} won't replay automatically because it was on the front.
        # The silence hack prevents the example sentence audio from autoplaying.
        "afmt": """
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<div class="main-info">
    <div class="german-word">{{full_source}}</div>
    <div class="polish-translation">{{base_target}} {{base_target_audio}}</div>
</div>
<hr>
<div class="example-pair">
    <div class="source-sentence">{{s1_source}}</div>
    <div class="target-sentence">{{s1_target}} {{s1_target_audio}}</div>
</div>

{{#s2_source}}
<div class="example-pair">
    <div class="source-sentence">{{s2_source}} {{s2_audio}}</div>
    <div class="target-sentence">{{s2_target}} {{s2_target_audio}}</div>
</div>
{{/s2_source}}

{{#s3_source}}
<details>
    <summary>Więcej Przykładów (More Examples)</summary>
    <div class="examples-section">
        <div class="example-pair">
            <div class="source-sentence">{{s3_source}} {{s3_audio}}</div>
            <div class="target-sentence">{{s3_target}}</div>
        </div>
        {{#s4_source}}
            <div class="example-pair">
                <div class="source-sentence">{{s4_source}} {{s4_audio}}</div>
                <div class="target-sentence">{{s4_target}}</div>
            </div>
        {{/s4_source}}
        {{#s5_source}}
            <div class="example-pair">
                <div class="source-sentence">{{s5_source}} {{s5_audio}}</div>
                <div class="target-sentence">{{s5_target}}</div>
            </div>
        {{/s5_source}}
        {{#s6_source}}
            <div class="example-pair">
                <div class="source-sentence">{{s6_source}} {{s6_audio}}</div>
                <div class="target-sentence">{{s6_target}}</div>
            </div>
        {{/s6_source}}
        {{#s7_source}}
            <div class="example-pair">
                <div class="source-sentence">{{s7_source}} {{s7_audio}}</div>
                <div class="target-sentence">{{s7_target}}</div>
            </div>
        {{/s7_source}}
        {{#s8_source}}
            <div class="example-pair">
                <div class="source-sentence">{{s8_source}} {{s8_audio}}</div>
                <div class="target-sentence">{{s8_target}}</div>
            </div>
        {{/s8_source}}
        {{#s9_source}}
            <div class="example-pair">
                <div class="source-sentence">{{s9_source}} {{s9_audio}}</div>
                <div class="target-sentence">{{s9_target}}</div>
            </div>
        {{/s9_source}}
    </div>
</details>
{{/s3_source}}
""",
        "did": DECK_ID_RECOGNITION,  # Cards go to Recognition subdeck
    },
    {
        "name": "Polish to German",
        # --- FRONT ---
        # Polish text with audio and context sentence hint.
        "qfmt": """
<div class="polish-translation-front">{{base_target}} {{base_target_audio}}</div>

<div class="example-context-pl">Hint: "{{s1_target}}"</div>
""",
        # --- BACK ---
        # On this card, {{base_audio}} is new, so it will autoplay.
        # The silence hack is placed immediately after it to prevent the subsequent
        # example sentence audio files from autoplaying.
        "afmt": """
<div class="main-info">
    <div class="german-word">{{full_source}} {{full_source_audio}}</div>
    <div style="display:none">[sound:_1-minute-of-silence.mp3]</div>
    <div class="polish-translation">{{base_target}} {{base_target_audio}}</div>
</div>
<hr>
<div class="examples-section">
    <div class="section-title">Beispiel</div>
    {{#s1_source}}
        <div class="source-sentence">{{s1_source}} {{s1_audio}}</div>
    {{/s1_source}}
</div>
""",
        "did": DECK_ID_PRODUCTION,   # Cards go to Production subdeck
    },
    
    # === LISTENING COMPREHENSION CARDS (Audio → Text) ===
    # 9 templates for s1-s9 sentences, only generated if sentence exists
    
    {
        "name": "Listening S1",
        "qfmt": """
{{#s1_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s1_audio}}</div>
{{/s1_source}}
""",
        "afmt": """
{{#s1_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s1_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s1_target}} {{s1_target_audio}}</div>
</div>
{{/s1_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S2", 
        "qfmt": """
{{#s2_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s2_audio}}</div>
{{/s2_source}}
""",
        "afmt": """
{{#s2_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s2_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s2_target}} {{s2_target_audio}}</div>
</div>
{{/s2_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S3",
        "qfmt": """
{{#s3_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s3_audio}}</div>
{{/s3_source}}
""",
        "afmt": """
{{#s3_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s3_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s3_target}} {{s3_target_audio}}</div>
</div>
{{/s3_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S4",
        "qfmt": """
{{#s4_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s4_audio}}</div>
{{/s4_source}}
""",
        "afmt": """
{{#s4_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s4_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s4_target}} {{s4_target_audio}}</div>
</div>
{{/s4_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S5",
        "qfmt": """
{{#s5_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s5_audio}}</div>
{{/s5_source}}
""",
        "afmt": """
{{#s5_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s5_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s5_target}} {{s5_target_audio}}</div>
</div>
{{/s5_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S6",
        "qfmt": """
{{#s6_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s6_audio}}</div>
{{/s6_source}}
""",
        "afmt": """
{{#s6_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s6_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s6_target}} {{s6_target_audio}}</div>
</div>
{{/s6_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S7",
        "qfmt": """
{{#s7_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s7_audio}}</div>
{{/s7_source}}
""",
        "afmt": """
{{#s7_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s7_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s7_target}} {{s7_target_audio}}</div>
</div>
{{/s7_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S8", 
        "qfmt": """
{{#s8_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s8_audio}}</div>
{{/s8_source}}
""",
        "afmt": """
{{#s8_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s8_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s8_target}} {{s8_target_audio}}</div>
</div>
{{/s8_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    {
        "name": "Listening S9",
        "qfmt": """
{{#s9_source}}
<div class="listening-instructions">🎧 Słuchaj i zidentyfikuj zdanie</div>
<div class="audio-only">{{s9_audio}}</div>
{{/s9_source}}
""",
        "afmt": """
{{#s9_source}}
<div class="listening-answer">
    <div class="german-sentence">🇩🇪 {{s9_source}}</div>
    <div class="polish-sentence">🇵🇱 {{s9_target}} {{s9_target_audio}}</div>
</div>
{{/s9_source}}
""",
        "did": DECK_ID_LISTENING,
    },
    
    # === SENTENCE PRODUCTION CARDS (Polish → German sentences) ===
    # 9 templates for s1-s9 sentences, only generated if sentence exists
    
    {
        "name": "Sentence Production S1",
        "qfmt": """
{{#s1_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s1_target}} {{s1_target_audio}}</div>
{{/s1_target}}
""",
        "afmt": """
{{#s1_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s1_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s1_source}} {{s1_audio}}</div>
{{/s1_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S2",
        "qfmt": """
{{#s2_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s2_target}} {{s2_target_audio}}</div>
{{/s2_target}}
""",
        "afmt": """
{{#s2_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s2_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s2_source}} {{s2_audio}}</div>
{{/s2_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S3",
        "qfmt": """
{{#s3_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s3_target}} {{s3_target_audio}}</div>
{{/s3_target}}
""",
        "afmt": """
{{#s3_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s3_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s3_source}} {{s3_audio}}</div>
{{/s3_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S4",
        "qfmt": """
{{#s4_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s4_target}} {{s4_target_audio}}</div>
{{/s4_target}}
""",
        "afmt": """
{{#s4_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s4_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s4_source}} {{s4_audio}}</div>
{{/s4_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S5",
        "qfmt": """
{{#s5_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s5_target}} {{s5_target_audio}}</div>
{{/s5_target}}
""",
        "afmt": """
{{#s5_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s5_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s5_source}} {{s5_audio}}</div>
{{/s5_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S6",
        "qfmt": """
{{#s6_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s6_target}} {{s6_target_audio}}</div>
{{/s6_target}}
""",
        "afmt": """
{{#s6_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s6_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s6_source}} {{s6_audio}}</div>
{{/s6_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S7",
        "qfmt": """
{{#s7_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s7_target}} {{s7_target_audio}}</div>
{{/s7_target}}
""",
        "afmt": """
{{#s7_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s7_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s7_source}} {{s7_audio}}</div>
{{/s7_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S8",
        "qfmt": """
{{#s8_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s8_target}} {{s8_target_audio}}</div>
{{/s8_target}}
""",
        "afmt": """
{{#s8_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s8_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s8_source}} {{s8_audio}}</div>
{{/s8_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
    {
        "name": "Sentence Production S9",
        "qfmt": """
{{#s9_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="sentence-question">{{s9_target}} {{s9_target_audio}}</div>
{{/s9_target}}
""",
        "afmt": """
{{#s9_target}}
<div class="sentence-hint">🇵🇱 → 🇩🇪 Przetłumacz to zdanie na niemiecki</div>
<div class="question">{{s9_target}}</div>
<hr>
<div class="sentence-answer">🇩🇪 {{s9_source}} {{s9_audio}}</div>
{{/s9_target}}
""",
        "did": DECK_ID_SENTENCE_PROD,
    },
]

# Unified CSS with semantic classes and consistent color palette
# Inspired by minimal Anki templates - simple, semantic, reusable
DTZ_CARD_CSS = """
/* --------------------------------------------------
   COLOR PALETTE & VARIABLES
   -------------------------------------------------- */
:root {
    --primary-color: #007aff;
    --secondary-color: #666;
    --hint-color: #999;
    --border-color: #ddd;
    --spacing-small: 10px;
    --spacing-medium: 20px;
    --spacing-large: 30px;
    --font-small: 16px;
    --font-medium: 20px;
    --font-large: 24px;
    --font-xlarge: 28px;
}

/* Night mode colors */
.nightMode {
    --primary-color: #58a6ff;
    --secondary-color: #888;
    --hint-color: #aaa;
    --border-color: #444;
}

/* --------------------------------------------------
   SEMANTIC STYLES
   -------------------------------------------------- */

/* Main card container */
.card {
    font-family: Arial, sans-serif;
    font-size: var(--font-medium);
    text-align: center;
    line-height: 1.4;
}

/* Hint text (instructions, directions) */
.hint {
    font-size: var(--font-small);
    color: var(--hint-color);
    font-weight: normal;
    margin-bottom: var(--spacing-medium);
}

/* Question text (what user should answer) */
.question {
    font-size: var(--font-large);
    color: var(--primary-color);
    font-weight: bold;
    margin: var(--spacing-medium) 0;
}

/* Context (repetition of question on answer side) */
.context {
    font-size: var(--font-medium);
    color: var(--primary-color);
    margin: var(--spacing-small) 0;
}

/* Answer text (correct response) */
.answer {
    font-size: var(--font-large);
    color: var(--primary-color);
    font-weight: bold;
    margin: var(--spacing-medium) 0;
}

/* Word/phrase headers */
.word-title {
    font-size: var(--font-xlarge);
    font-weight: bold;
    margin-bottom: var(--spacing-small);
}

/* Example sentences and secondary content */
.example {
    font-size: 18px;
    margin-bottom: 5px;
}

.example-target {
    font-size: 18px;
    color: var(--secondary-color);
    font-style: italic;
}

/* Dividers */
hr {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: var(--spacing-medium) 0;
}

.faint-hr {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: var(--spacing-small) 40px;
}

/* --------------------------------------------------
   LAYOUT COMPONENTS
   -------------------------------------------------- */

/* Main information sections */
.main-info {
    margin-bottom: var(--spacing-medium);
}

/* Example pairs */
.example-pair {
    margin-bottom: 15px;
}

/* Collapsible examples */
details {
    margin-top: var(--spacing-medium);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: var(--spacing-small);
}

summary {
    font-style: italic;
    cursor: pointer;
    color: var(--primary-color);
}

/* Audio-only content */
.audio-only {
    padding: var(--spacing-medium);
    margin: var(--spacing-small) 0;
}

/* Listening answers */
.listening-answer {
    max-width: 600px;
    margin: 0 auto;
}

/* Examples section */
.examples-section {
    margin-top: var(--spacing-medium);
}

.examples-section .section-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
}
"""