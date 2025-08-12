# Changelog

All notable changes to the DTZ Goethe B1 German-Polish Anki deck project will be documented in this file.

## [2.0.0] - 2025-01-XX - 4-Subdeck Architecture

### 🚨 BREAKING CHANGE

**Major structural change**: The deck format has been completely redesigned from a single deck with 20 card types to **4 separate subdecks**. This deck allows you to focus on different learning areas when needed.

### ✨ New Structure

The deck is now organized into 4 specialized subdecks:

- **01 Recognition** (German → Polish) - 1 card type
- **02 Production** (Polish → German) - 1 card type  
- **03 Listening Comprehension** (Audio → Text) - Up to 9 cards per word
- **04 Sentence Production** (Polish → German sentences) - Up to 9 cards per word

### 🎯 Benefits

- **Focused Learning**: Study specific skills independently (vocabulary recognition, production, listening, or sentence building)
- **Better Organization**: Cleaner Anki interface with logical grouping
- **Flexible Scheduling**: Set different review intervals for different skill types
- **Progress Tracking**: Monitor improvement in specific areas

### 🔧 Technical Improvements

- **GUID Preservation**: Recognition cards maintain original study progress from single-deck versions
- **Smart Deduplication**: Improved handling of card generation and loading
- **Enhanced Templates**: Unified semantic CSS with better night mode support
- **Audio Field Fix**: Resolved `full_source_audio` field mapping bug

### ⚠️ Migration Notes

**For existing users:**
- This is a structural change that affects how cards are organized in Anki
- Your study progress will be preserved for recognition cards
- You may need to adjust your study routine to work with the new subdeck structure
- The total number of cards remains the same, but they're now distributed across 4 subdecks

### 📋 Compatibility

- **Anki Version**: Compatible with Anki 2.1.x
- **Import Settings**: Use "Update notes" and "Import study progress" when updating
- **Legacy Support**: Single-deck format still available via development tools

---

## [1.x.x] - Previous Versions

Previous versions used a single deck with 20 card types. See git history for detailed changes in the single-deck era.