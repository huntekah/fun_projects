"""
Anki card templates for DTZ Goethe B1 German-Polish deck.
Based on the original DTZ deck structure, with an improved layout
and controlled audio autoplay, including Polish audio support.
"""

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
    <div class="target-sentence">{{s2_target}}</div>
</div>
{{/s2_source}}

<details>
    <summary>Więcej Przykładów (More Examples)</summary>
    <div class="examples-section">
        {{#s3_source}}
            <div class="example-pair">
                <div class="source-sentence">{{s3_source}} {{s3_audio}}</div>
                <div class="target-sentence">{{s3_target}}</div>
            </div>
        {{/s3_source}}
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
""",
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
    },
]

# Complete CSS with night mode support
DTZ_CARD_CSS = """
/* --- General Card Styling (Day Mode) --- */
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    background-color: #f9f9f9;
    color: #333;
}

.german-word-title {
    font-size: 28px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}

.faint-hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 10px 40px;
}

.german-word {
    font-size: 28px;
    font-weight: bold;
    color: #333;
    margin-bottom: 20px;
}

.polish-translation-front {
    font-size: 28px;
    font-weight: bold;
    color: #007aff;
    margin-bottom: 20px;
}

.example-context, .example-context-pl {
    font-size: 22px;
    color: #555;
    margin-top: 15px;
    padding: 0 10px;
}

.main-info .polish-translation {
    font-size: 24px;
    color: #007aff;
    font-weight: bold;
    margin-top: 10px;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 20px 0;
}

.examples-section .section-title {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 15px;
}

.example-pair {
    margin-bottom: 15px;
}

.source-sentence {
    font-size: 18px;
    color: #333;
    margin-bottom: 5px;
}

.target-sentence {
    font-size: 18px;
    color: #666;
    font-style: italic;
}

details {
    margin-top: 20px;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 10px;
}

summary {
    font-weight: bold;
    cursor: pointer;
    color: #007aff;
}

.play-icon { 
    cursor: pointer;
    font-size: 16px;
    color: #007aff;
}

/* --- Night Mode Overrides --- */

/*
By NOT defining rules for ".card.nightMode", we allow the card to correctly
inherit the default background (e.g., pure black for AMOLED) and base text color
(e.g., pure white) from the Anki application's settings.

We only override the colors of specific elements below to ensure readability
and maintain our color-coding against a dark background.
*/

/* German text elements in night mode can inherit the default white, so no rule is needed. */
/* We only need to style the secondary text colors. */

.nightMode .faint-hr,
.nightMode hr {
    border-top-color: #444; /* A subtle border for dark mode */
}

.nightMode .polish-translation-front,
.nightMode .main-info .polish-translation,
.nightMode summary,
.nightMode .play-icon {
    color: #58a6ff; /* A lighter, more readable blue for dark backgrounds */
}

.nightMode .example-context,
.nightMode .example-context-pl,
.nightMode .target-sentence {
    color: #888; /* A darker grey for secondary/italic text to be less bright */
}

.nightMode details {
    border-color: #444;
}
"""