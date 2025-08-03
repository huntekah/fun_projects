#!/usr/bin/env python3
"""
Validation script to ensure existing functionality works after directory restructure.
Run this script to verify all core components are still functional.
"""

def test_imports():
    """Test that all core modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        import schema
        print("✅ schema.py - Core data models")
        assert hasattr(schema, 'AnkiCard')
        assert hasattr(schema, 'AnkiDeck')
    except Exception as e:
        print(f"❌ schema.py failed: {e}")
        return False
    
    try:
        from csv_export import export_deck_to_csv, load_deck_from_csv
        print("✅ csv_export.py - CSV handling")
    except Exception as e:
        print(f"❌ csv_export.py failed: {e}")
        return False
    
    try:
        from tts_engine import TTSGenerator
        print("✅ tts_engine.py - TTS functionality")
    except Exception as e:
        print(f"❌ tts_engine.py failed: {e}")
        return False
    
    try:
        from utilities import load_anki_deck, save_anki_deck
        print("✅ utilities.py - APKG handling")
    except Exception as e:
        print(f"❌ utilities.py failed: {e}")
        return False
    
    try:
        from frequency_sort import load_frequency_list
        print("✅ frequency_sort.py - Frequency sorting")
    except Exception as e:
        print(f"❌ frequency_sort.py failed: {e}")
        return False
    
    return True

def test_new_structure():
    """Test that new directory structure exists."""
    print("\n🏗️  Testing new directory structure...")
    
    from pathlib import Path
    
    expected_dirs = [
        "configs",
        "src/anki_deck_factory",
        "src/anki_deck_factory/builders",
        "src/anki_deck_factory/config", 
        "src/anki_deck_factory/connectors/llm",
        "src/anki_deck_factory/connectors/tts",
        "src/anki_deck_factory/domain",
        "src/anki_deck_factory/io",
        "src/anki_deck_factory/processing",
        "tests"
    ]
    
    for dir_path in expected_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - missing")
            return False
    
    return True

if __name__ == "__main__":
    print("🔍 TASK 001.2 - Validating existing functionality")
    print("=" * 50)
    
    imports_ok = test_imports()
    structure_ok = test_new_structure()
    
    print("\n📊 Summary:")
    if imports_ok and structure_ok:
        print("🎉 All validations passed! Ready for next task.")
        exit(0)
    else:
        print("❌ Some validations failed. Fix issues before proceeding.")
        exit(1)