"""
Tests for text processing utilities.

This module tests the text cleaning functions for Anki card content,
including HTML escaping, MathJax operator spacing, and MathJax/Cloze conflicts.
"""

import pytest
from src.utils.text_processing import (
    escape_html_operators,
    fix_mathjax_operator_spacing,
    fix_mathjax_cloze_conflicts,
    clean_anki_text
)


class TestEscapeHtmlOperators:
    """Test HTML operator escaping functionality."""
    
    def test_escape_basic_operators(self):
        """Test basic < and > escaping."""
        assert escape_html_operators("x < 5") == "x &lt; 5"
        assert escape_html_operators("y > 3") == "y &gt; 3"
        assert escape_html_operators("x < 5 and y > 3") == "x &lt; 5 and y &gt; 3"
    
    def test_preserve_valid_html_tags(self):
        """Test that valid HTML tags are preserved."""
        assert escape_html_operators("<b>bold</b>") == "<b>bold</b>"
        assert escape_html_operators("<i>italic</i>") == "<i>italic</i>"
        assert escape_html_operators("<code>code</code>") == "<code>code</code>"
        assert escape_html_operators("<pre>preformatted</pre>") == "<pre>preformatted</pre>"
    
    def test_mixed_html_and_operators(self):
        """Test mixed valid HTML and stray operators."""
        assert escape_html_operators("x < 5 and <b>bold</b>") == "x &lt; 5 and <b>bold</b>"
        assert escape_html_operators("<i>text</i> > 10") == "<i>text</i> &gt; 10"
    
    def test_edge_cases(self):
        """Test edge cases like empty strings and None."""
        assert escape_html_operators("") == ""
        assert escape_html_operators(None) == ""
        assert escape_html_operators("no operators") == "no operators"


class TestFixMathjaxOperatorSpacing:
    """Test MathJax operator spacing functionality."""
    
    def test_basic_operator_spacing(self):
        """Test basic operator spacing fixes."""
        # Main test case from the original example
        assert fix_mathjax_operator_spacing(r'\(\hatw_t\)') == r'\(\hat w_t\)'
        assert fix_mathjax_operator_spacing(r'\(\sinx\)') == r'\(\sin x\)'
        assert fix_mathjax_operator_spacing(r'\(\vecv\)') == r'\(\vec v\)'
    
    def test_no_processing_outside_mathjax(self):
        """Test that operators outside MathJax blocks are ignored."""
        assert fix_mathjax_operator_spacing(r'This is \hatw_t') == r'This is \hatw_t'
    
    def test_complex_expressions(self):
        """Test complex mathematical expressions."""
        input_text = r'\[\sin(x) + \frac{1}{n} \haty_i \cdot \limx\to 0 \vecv\]'
        expected = r'\[\sin(x) + \frac{1}{n} \hat y_i \cdot \lim x\to 0 \vec v\]'
        assert fix_mathjax_operator_spacing(input_text) == expected
    
    def test_already_correct_spacing(self):
        """Test that already correct spacing is preserved."""
        assert fix_mathjax_operator_spacing(r'\(\hat w_t\)') == r'\(\hat w_t\)'
        assert fix_mathjax_operator_spacing(r'\(\sin x\)') == r'\(\sin x\)'
    
    def test_operators_not_followed_by_letters(self):
        """Test operators not followed by letters are unchanged."""
        assert fix_mathjax_operator_spacing(r'\(\hat(w_t)\)') == r'\(\hat(w_t)\)'
        assert fix_mathjax_operator_spacing(r'\(\sin(x)\)') == r'\(\sin(x)\)'
    
    def test_longest_operator_first(self):
        """Test that longest operators are matched first to avoid conflicts."""
        assert fix_mathjax_operator_spacing(r'\(\overlinexy + \over y\)') == r'\(\overline xy + \over y\)'
    
    def test_cloze_with_operators(self):
        """Test operator spacing inside cloze deletions."""
        input_text = r'{{c1:\[\hatw \frac{1}{2} \sqrtn\]}}'
        expected = r'{{c1:\[\hat w \frac{1}{2} \sqrt n\]}}'
        assert fix_mathjax_operator_spacing(input_text) == expected
    
    def test_dots_operator_not_split(self):
        """Test that \dots operator is not incorrectly split into \dot s."""
        input_text = r'\(t^2_i = \text{MultiHeadAttention}(t^1_i, [t^1_1, \dots, t^1_N])\)'
        # \dots should NOT be changed to \dot s
        result = fix_mathjax_operator_spacing(input_text)
        assert r'\dots' in result
        assert r'\dot s' not in result
    
    def test_dot_vs_dots_comprehensive(self):
        """Test comprehensive dot vs dots operator handling."""
        # Test \dot followed by letter (should add space)
        assert fix_mathjax_operator_spacing(r'\(\dotx\)') == r'\(\dot x\)'
        
        # Test \dots followed by letter (should add space) 
        assert fix_mathjax_operator_spacing(r'\(\dotsx\)') == r'\(\dots x\)'
        
        # Test \dot followed by comma (current behavior: adds space)
        assert fix_mathjax_operator_spacing(r'\(\dot,\)') == r'\(\dot ,\)'
        
        # Test \dots followed by comma (current behavior: adds space)
        assert fix_mathjax_operator_spacing(r'\(\dots,\)') == r'\(\dots ,\)'
        
        # Test \dots in original failing case
        input_text = r'\(\dots, t^1_N\)'
        result = fix_mathjax_operator_spacing(input_text)
        assert r'\dots ,' in result
        assert r'\dot s' not in result
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert fix_mathjax_operator_spacing("") == ""
        assert fix_mathjax_operator_spacing(None) == ""
        assert fix_mathjax_operator_spacing("no math here") == "no math here"


class TestFixMathjaxClozeConflicts:
    """Test MathJax/Cloze conflict resolution functionality."""
    
    def test_basic_brace_spacing(self):
        """Test basic brace spacing in MathJax blocks."""
        input_text = r'\(\frac{1}{2}\)'
        expected = r'\(\frac { 1 }  { 2 } \)'
        assert fix_mathjax_cloze_conflicts(input_text) == expected
    
    def test_complex_formula_with_cloze(self):
        """Test complex formula inside cloze deletion."""
        input_text = r'By applying the chain rule... {{c1:\[\sqrt[n]{\prod_{i=1}^{n} \frac{1}{P_\theta(w_i|w_{<i})}}\]}}'
        expected = r'By applying the chain rule... {{c1:\[\sqrt[n] { \prod_ { i=1 } ^ { n }  \frac { 1 }  { P_\theta(w_i|w_ { <i } ) }  } \]}}'
        assert fix_mathjax_cloze_conflicts(input_text) == expected
    
    def test_escaped_braces_preserved(self):
        """Test that escaped braces (\\{) are not spaced."""
        # Escaped braces should NOT be spaced
        assert fix_mathjax_cloze_conflicts(r'\( \{a, b, c\} \)') == r'\( \{a, b, c\} \)'
        assert fix_mathjax_cloze_conflicts(r'\(\{\}\)') == r'\(\{\}\)'
    
    def test_no_braces_unchanged(self):
        """Test text without braces is unchanged."""
        assert fix_mathjax_cloze_conflicts(r'\(a + b\)') == r'\(a + b\)'
    
    def test_non_mathjax_unchanged(self):
        """Test that non-MathJax content is unchanged."""
        assert fix_mathjax_cloze_conflicts('{{c1::This is a test}}') == '{{c1::This is a test}}'
        assert fix_mathjax_cloze_conflicts('regular text') == 'regular text'
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert fix_mathjax_cloze_conflicts("") == ""
        assert fix_mathjax_cloze_conflicts(None) == ""


class TestCleanAnkiText:
    """Test the high-level clean_anki_text function that combines all fixes."""
    
    def test_html_escaping_only(self):
        """Test cases that only need HTML escaping."""
        assert clean_anki_text("x < 5 and y > 3") == "x &lt; 5 and y &gt; 3"
    
    def test_operator_spacing_only(self):
        """Test cases that only need operator spacing."""
        assert clean_anki_text(r'\(\hatw_t\)') == r'\(\hat w_t\)'
    
    def test_brace_conflicts_only(self):
        """Test cases that only need brace conflict resolution."""
        assert clean_anki_text(r'\(\frac{1}{2}\)') == r'\(\frac { 1 }  { 2 } \)'
    
    def test_combined_fixes(self):
        """Test cases that need multiple fixes applied."""
        # HTML escaping + operator spacing + brace conflicts
        input_text = r'Formula: x < 5, \(\hatw\frac{1}{2}\)'
        expected = r'Formula: x &lt; 5, \(\hat w\frac { 1 }  { 2 } \)'
        assert clean_anki_text(input_text) == expected
    
    def test_order_of_operations(self):
        """Test that fixes are applied in the correct order."""
        # This ensures HTML escaping happens first, then operator spacing, then brace conflicts
        input_text = r'x < 5 with \(\hatw\frac{1}{2}\) formula'
        result = clean_anki_text(input_text)
        
        # Should have HTML escaping
        assert '&lt;' in result
        # Should have operator spacing
        assert r'\hat w' in result
        # Should have brace spacing
        assert r'\frac { 1 }' in result
    
    def test_complex_real_world_example(self):
        """Test a complex real-world example."""
        input_text = r'The perplexity is < infinity when \(\hatw_t \cdot \frac{1}{P_\theta(w_i|w_{<i})}\)'
        result = clean_anki_text(input_text)
        
        # Check all fixes are applied
        assert '&lt; infinity' in result  # HTML escaping
        assert r'\hat w_t' in result       # Operator spacing
        assert r'\frac { 1 }' in result    # Brace conflicts
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert clean_anki_text("") == ""
        assert clean_anki_text(None) == ""
        assert clean_anki_text("simple text") == "simple text"


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases across all functions."""
    
    def test_preserve_valid_html_in_complex_math(self):
        """Test that valid HTML is preserved even in complex mathematical content."""
        input_text = r'<b>Bold</b>: x < 5 and \(\hatw\frac{1}{2}\)'
        result = clean_anki_text(input_text)
        
        assert '<b>Bold</b>' in result  # HTML preserved
        assert '&lt; 5' in result       # Stray < escaped
        assert r'\hat w' in result      # Operator spaced
        assert r'\frac { 1 }' in result # Braces spaced
    
    def test_multiple_mathjax_blocks(self):
        """Test handling of multiple MathJax blocks in one string."""
        input_text = r'First: \(\hatw\) and second: \[\sinx + \frac{1}{2}\]'
        result = clean_anki_text(input_text)
        
        assert r'\(\hat w\)' in result
        assert r'\[\sin x + \frac { 1 }  { 2 } \]' in result
    
    def test_nested_structures(self):
        """Test complex nested structures."""
        input_text = r'{{c1::\[\hatw_t < \frac{1}{P_\theta(w_i|w_{<i})}\]}}'
        result = clean_anki_text(input_text)
        
        # Should handle all transformations correctly
        assert '&lt;' in result                # HTML escaping
        assert r'\hat w_t' in result           # Operator spacing  
        assert r'\frac { 1 }' in result        # Brace spacing
        assert r'w_ { &lt;i }' in result       # Complex brace spacing with HTML escaping