"""
Text processing utilities for Anki card content.

This module provides functions to clean and fix text content for Anki flashcards,
handling common issues like stray HTML operators and MathJax/Cloze conflicts.
"""

import re
from typing import Optional

# --- HTML Escaping ---

# Regex to identify valid HTML tags vs stray < > characters
HTML_TAG_PATTERN = re.compile(r'(</?\w+.*?>)|(<)|(>)')

def _html_replacer(match: re.Match) -> str:
    """Replace stray < > characters while preserving valid HTML tags."""
    if match.group(1):
        # Valid HTML tag - keep unchanged
        return match.group(1)
    elif match.group(2):
        # Stray < character
        return '&lt;'
    elif match.group(3):
        # Stray > character
        return '&gt;'
    else:
        raise ValueError("Unexpected match group in HTML pattern")

def escape_html_operators(text: Optional[str]) -> str:
    """
    Escape stray '<' and '>' characters while preserving valid HTML tags.
    
    This is essential for Anki cards where mathematical notation (like "x < 5")
    might be mixed with HTML formatting.
    
    Args:
        text: Input text that may contain stray HTML operators
        
    Returns:
        Text with stray operators escaped as &lt; and &gt;
        
    Examples:
        >>> escape_html_operators("x < 5 and <b>bold</b>")
        "x &lt; 5 and <b>bold</b>"
    """
    if not text:
        return ""
    
    return HTML_TAG_PATTERN.sub(_html_replacer, text)

# --- MathJax/Cloze Conflict Resolution ---

# Regex to find MathJax blocks (inline \(...\) and display \[...\])
MATHJAX_BLOCK_PATTERN = re.compile(r'(\\\(.*?\\\))|(\\\[.*?\\\])', re.DOTALL)

def _mathjax_brace_spacer(match: re.Match) -> str:
    """Add spaces around braces inside MathJax blocks to prevent Cloze conflicts."""
    full_match = match.group(0)
    
    # Extract delimiters and content
    delimiter_open = full_match[:2]   # \( or \[
    delimiter_close = full_match[-2:]  # \) or \]
    content = full_match[2:-2]
    
    # Space non-escaped braces: { becomes " { ", but \{ stays \{
    content = re.sub(r'(?<!\\){', ' { ', content)
    content = re.sub(r'(?<!\\)}', ' } ', content)
    
    return f"{delimiter_open}{content}{delimiter_close}"

def fix_mathjax_cloze_conflicts(text: Optional[str]) -> str:
    """
    Fix conflicts between MathJax braces and Anki cloze deletions.
    
    Anki's cloze parser can misinterpret }} in MathJax formulas like \frac{1}{2}
    as the end of a cloze deletion {{c1::...}}. This function adds spaces around
    braces inside MathJax blocks to prevent this.
    
    Args:
        text: Text containing MathJax formulas and potentially cloze deletions
        
    Returns:
        Text with spaced braces inside MathJax blocks
        
    Examples:
        >>> fix_mathjax_cloze_conflicts(r"\\(\frac{1}{2}\\)")
        r"\\( \frac { 1 } { 2 } \\)"
    """
    if not text:
        return ""
    
    return MATHJAX_BLOCK_PATTERN.sub(_mathjax_brace_spacer, text)

# --- High-Level API ---

def clean_anki_text(text: Optional[str]) -> str:
    """
    Apply all text cleaning operations for Anki card content.
    
    This is the main entry point for cleaning text that will be used in Anki cards.
    It applies multiple fixes in the correct order:
    1. Escape stray HTML operators (< and >)
    2. Fix MathJax/Cloze conflicts by spacing braces
    
    Args:
        text: Raw text content for an Anki card
        
    Returns:
        Cleaned text ready for Anki card use
        
    Examples:
        >>> clean_anki_text("Formula: x < 5, \\(\\frac{1}{2}\\)")
        "Formula: x &lt; 5, \\( \\frac { 1 } { 2 } \\)"
    """
    if not text:
        return ""
    
    # Apply HTML escaping first
    cleaned = escape_html_operators(text)
    
    # Then fix MathJax/Cloze conflicts
    cleaned = fix_mathjax_cloze_conflicts(cleaned)
    
    return cleaned

