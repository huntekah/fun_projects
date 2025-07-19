"""
Anki card templates for DTZ Goethe B1 German-Polish deck.
Based on the original DTZ deck structure.
"""

DTZ_MODEL_FIELDS = [
    {"name": "full_source"},     # Previously full_d
    {"name": "base_target"},     # Previously base_e  
    {"name": "base_source"},     # Previously base_d
    {"name": "artikel_d"},       # Keep German-specific naming
    {"name": "plural_d"},        # Keep German-specific naming
    {"name": "audio_text_d"},    # Keep German-specific naming
    {"name": "s1_source"},       # Previously s1
    {"name": "s1_target"},       # Previously s1e
    {"name": "s2_source"},       # Previously s2
    {"name": "s2_target"},       # Previously s2e
    {"name": "s3_source"},       # Previously s3
    {"name": "s3_target"},       # Previously s3e
    {"name": "s4_source"},       # Previously s4
    {"name": "s4_target"},       # Previously s4e
    {"name": "s5_source"},       # Previously s5
    {"name": "s5_target"},       # Previously s5e
    {"name": "s6_source"},       # Previously s6
    {"name": "s6_target"},       # Previously s6e
    {"name": "s7_source"},       # Previously s7
    {"name": "s7_target"},       # Previously s7e
    {"name": "s8_source"},       # Previously s8
    {"name": "s8_target"},       # Previously s8e
    {"name": "s9_source"},       # Previously s9
    {"name": "s9_target"},       # Previously s9e
    {"name": "original_order"},  # Keep same
    {"name": "base_audio"},      # Previously base_a
    {"name": "s1_audio"},        # Previously s1a
    {"name": "s2_audio"},        # Previously s2a
    {"name": "s3_audio"},        # Previously s3a
    {"name": "s4_audio"},        # Previously s4a
    {"name": "s5_audio"},        # Previously s5a
    {"name": "s6_audio"},        # Previously s6a
    {"name": "s7_audio"},        # Previously s7a
    {"name": "s8_audio"},        # Previously s8a
    {"name": "s9_audio"},        # Previously s9a
]

DTZ_CARD_TEMPLATES = [
    {
        "name": "German to Polish",
        "qfmt": "{{base_source}}{{base_audio}}",
        "afmt": """{{base_target}}<br>
{{full_source}}{{base_audio}}
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<hr id=answer>

<div style='font-family: Arial; font-size: 16px;'>{{s1_source}}{{s1_audio}}{{hint:s1_target}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s2_source}}{{s2_audio}}{{hint:s2_target}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s3_source}}{{s3_audio}}{{hint:s3_target}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s4_source}}{{s4_audio}}{{hint:s4_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s5_source}}{{s5_audio}}{{hint:s5_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s6_source}}{{s6_audio}}{{hint:s6_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s7_source}}{{s7_audio}}{{hint:s7_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s8_source}}{{s8_audio}}{{hint:s8_target}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s9_source}}{{s9_audio}}{{hint:s9_target}}</div>""",
    },
    {
        "name": "Polish to German", 
        "qfmt": "{{base_target}}",
        "afmt": """{{full_source}}{{base_audio}}<br>
{{base_target}}
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<hr id=answer>

<div style='font-family: Arial; font-size: 16px;'>{{s1_target}}{{s1_audio}}{{hint:s1_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s2_target}}{{s2_audio}}{{hint:s2_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s3_target}}{{s3_audio}}{{hint:s3_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s4_target}}{{s4_audio}}{{hint:s4_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s5_target}}{{s5_audio}}{{hint:s5_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s6_target}}{{s6_audio}}{{hint:s6_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s7_target}}{{s7_audio}}{{hint:s7_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s8_target}}{{s8_audio}}{{hint:s8_source}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s9_target}}{{s9_audio}}{{hint:s9_source}}</div>""",
    },
]

DTZ_CARD_CSS = """
.card {
    font-family: Arial, sans-serif;
    text-align: center;
    color: black;
    background-color: white;
}
.german {
    font-size: 20px;
    font-weight: bold;
    color: #2E86AB;
}
.polish {
    font-size: 18px;
    color: #A23B72;
}
.example {
    font-size: 14px;
    font-style: italic;
    color: #666;
    margin-top: 10px;
}
.example-pl {
    font-size: 14px;
    font-style: italic;
    color: #999;
}
"""
