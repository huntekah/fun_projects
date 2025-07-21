"""
Anki card templates for DTZ Goethe B1 German-Polish deck.
Based on the original DTZ deck structure.
"""

DTZ_MODEL_FIELDS = [
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
