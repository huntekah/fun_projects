#!/usr/bin/env python3
"""
Research TTS options for Polish and German audio generation.
Calculate costs based on our character counts.
"""

from pathlib import Path
from utilities import load_anki_deck


def calculate_tts_costs():
    """Calculate TTS costs for different services based on our character counts."""
    
    # Load character counts from our deck
    deck_path = Path("data/DTZ_Goethe_B1_DE_PL_Sample.apkg")
    deck = load_anki_deck(deck_path)
    
    # Count characters we need for TTS
    german_chars = 0
    polish_chars = 0
    
    for card in deck.cards:
        # German: base_source + all sentence sources
        if card.base_source:
            german_chars += len(card.base_source)
        for i in range(1, 10):
            field_value = getattr(card, f"s{i}_source", "")
            if field_value:
                german_chars += len(field_value)
        
        # Polish: base_target + all sentence targets  
        if card.base_target:
            polish_chars += len(card.base_target)
        for i in range(1, 10):
            field_value = getattr(card, f"s{i}_target", "")
            if field_value:
                polish_chars += len(field_value)
    
    total_chars = german_chars + polish_chars
    
    print(f"🎯 TTS CHARACTER REQUIREMENTS:")
    print(f"   German text: {german_chars:,} characters")
    print(f"   Polish text: {polish_chars:,} characters") 
    print(f"   Total needed: {total_chars:,} characters")
    print(f"   Free tier usage: {total_chars/1_000_000:.1%} of 1M chars")
    
    # TTS Service Analysis
    services = {
        "Google Cloud TTS": {
            "standard": {"free": 4_000_000, "price_per_m": 4.00},
            "wavenet": {"free": 1_000_000, "price_per_m": 16.00},
            "neural2": {"free": 1_000_000, "price_per_m": 16.00},
            "studio": {"free": 1_000_000, "price_per_m": 160.00}
        },
        "Amazon Polly": {
            "standard": {"free": 5_000_000, "price_per_m": 4.00}, 
            "neural": {"free": 1_000_000, "price_per_m": 16.00},
            "generative": {"free": 100_000, "price_per_m": 30.00}
        },
        "Microsoft Azure": {
            "standard": {"free": 500_000, "price_per_m": 4.00},
            "neural": {"free": 500_000, "price_per_m": 16.00}
        },
        "ElevenLabs": {
            "starter": {"free": 10_000, "price_per_m": 22.00},
            "creator": {"free": 30_000, "price_per_m": 22.00}
        },
        "OpenAI TTS": {
            "tts-1": {"free": 0, "price_per_m": 15.00},
            "tts-1-hd": {"free": 0, "price_per_m": 30.00}
        }
    }
    
    print(f"\n💰 TTS SERVICE COST ANALYSIS:")
    
    for service_name, tiers in services.items():
        print(f"\n🔊 {service_name}:")
        
        for tier_name, pricing in tiers.items():
            free_chars = pricing["free"]
            price_per_m = pricing["price_per_m"]
            
            if total_chars <= free_chars:
                cost = 0.00
                status = "✅ FREE"
            else:
                excess_chars = total_chars - free_chars
                cost = (excess_chars / 1_000_000) * price_per_m
                status = f"💸 ${cost:.2f}"
            
            print(f"   {tier_name.capitalize()}: {status} (free: {free_chars/1_000_000:.1f}M chars)")
    
    # Language support analysis
    print(f"\n🌐 LANGUAGE SUPPORT ANALYSIS:")
    
    language_support = {
        "Google Cloud TTS": {
            "german": "✅ Excellent (multiple voices, dialects)",
            "polish": "✅ Excellent (multiple voices)",
            "quality": "High quality WaveNet/Neural2 voices"
        },
        "Amazon Polly": {
            "german": "✅ Excellent (standard + neural)",
            "polish": "✅ Good (Ewa, Maja voices)",
            "quality": "High quality Neural voices"
        },
        "Microsoft Azure": {
            "german": "✅ Excellent (many voices)",
            "polish": "✅ Good (Agnieszka, Marek)", 
            "quality": "High quality Neural voices"
        },
        "ElevenLabs": {
            "german": "✅ Excellent (custom voices)",
            "polish": "✅ Good (fewer options)",
            "quality": "Very high quality, realistic"
        },
        "OpenAI TTS": {
            "german": "✅ Good (6 voices)",
            "polish": "✅ Good (6 voices)",
            "quality": "Good quality, fast generation"
        }
    }
    
    for service, support in language_support.items():
        print(f"\n🎙️  {service}:")
        print(f"   German: {support['german']}")
        print(f"   Polish: {support['polish']}")
        print(f"   Quality: {support['quality']}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"\n1. 🥇 BEST FREE OPTION: Amazon Polly Standard")
    print(f"   ✅ 5M free chars (our needs: {total_chars/1_000_000:.1f}M)")
    print(f"   ✅ Excellent German & Polish support")
    print(f"   ✅ Good quality standard voices")
    print(f"   💰 Cost: FREE")
    
    print(f"\n2. 🥈 BEST QUALITY: Google Cloud Neural2")
    print(f"   ✅ 1M free chars (covers {min(1_000_000/total_chars*100, 100):.0f}% of needs)")
    print(f"   ✅ Superior voice quality")
    print(f"   💰 Cost: ${((total_chars-1_000_000)/1_000_000*16):.2f} for excess")
    
    print(f"\n3. 🚀 FASTEST SETUP: OpenAI TTS")
    print(f"   ⚠️  No free tier")
    print(f"   ✅ Simple API, fast generation")
    print(f"   💰 Cost: ${(total_chars/1_000_000*15):.2f} (tts-1)")
    
    return {
        'german_chars': german_chars,
        'polish_chars': polish_chars,
        'total_chars': total_chars
    }


if __name__ == "__main__":
    stats = calculate_tts_costs()