"""
Anki card templates for DTZ Goethe B1 German-Polish deck.
Based on the original DTZ deck structure.
"""

DTZ_MODEL_FIELDS = [
    {'name': 'full_d'},
    {'name': 'base_e'},
    {'name': 'base_d'},
    {'name': 'artikel_d'},
    {'name': 'plural_d'},
    {'name': 'audio_text_d'},
    {'name': 's1'},
    {'name': 's1e'},
    {'name': 's2'},
    {'name': 's2e'},
    {'name': 's3'},
    {'name': 's3e'},
    {'name': 's4'},
    {'name': 's4e'},
    {'name': 's5'},
    {'name': 's5e'},
    {'name': 's6'},
    {'name': 's6e'},
    {'name': 's7'},
    {'name': 's7e'},
    {'name': 's8'},
    {'name': 's8e'},
    {'name': 's9'},
    {'name': 's9e'},
    {'name': 'original_order'},
    {'name': 'base_a'},
    {'name': 's1a'},
    {'name': 's2a'},
    {'name': 's3a'},
    {'name': 's4a'},
    {'name': 's5a'},
    {'name': 's6a'},
    {'name': 's7a'},
    {'name': 's8a'},
    {'name': 's9a'},
]

DTZ_CARD_TEMPLATES = [
    {
        'name': 'German to Polish',
        'qfmt': '{{base_d}}{{base_a}}',
        'afmt': '''{{base_e}}<br>
{{full_d}}{{base_a}}
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<hr id=answer>

<div style='font-family: Arial; font-size: 16px;'>{{s1}}{{s1a}}{{hint:s1e}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s2}}{{s2a}}{{hint:s2e}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s3}}{{s3a}}{{hint:s3e}}</div><br>
<div style='font-family: Arial; font-size: 16px;'>{{s4}}{{s4a}}{{hint:s4e}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s5}}{{s5a}}{{hint:s5e}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s6}}{{s6a}}{{hint:s6e}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s7}}{{s7a}}{{hint:s7e}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s8}}{{s8a}}{{hint:s8e}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s9}}{{s9a}}{{hint:s9e}}</div>''',
    },
    {
        'name': 'Polish to German',
        'qfmt': '{{base_e}}',
        'afmt': '''{{full_d}}{{base_a}}<br>
{{base_e}}
<div style="display:none">[sound:_1-minute-of-silence.mp3]</div>

<hr id=answer>

<div style='font-family: Arial; font-size: 16px;'>{{s1e}}{{s1a}}{{hint:s1}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s2e}}{{s2a}}{{hint:s2}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s3e}}{{s3a}}{{hint:s3}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s4e}}{{s4a}}{{hint:s4}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s5e}}{{s5a}}{{hint:s5}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s6e}}{{s6a}}{{hint:s6}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s7e}}{{s7a}}{{hint:s7}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s8e}}{{s8a}}{{hint:s8}}</div>
<div style='font-family: Arial; font-size: 16px;'>{{s9e}}{{s9a}}{{hint:s9}}</div>''',
    }
]

DTZ_CARD_CSS = '''
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
'''