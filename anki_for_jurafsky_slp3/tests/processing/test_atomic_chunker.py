"""
Tests for atomic_chunker module.

Simple tests focusing on retry functionality and basic behavior.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock

# Mock the problematic imports before they're loaded
sys.modules['google.genai'] = MagicMock()
sys.modules['connectors.llm.structured_gemini'] = MagicMock()


class TestRetryFunctionality:
    """Test retry functionality using mock objects."""
    
    def test_retry_decorator_exists(self):
        """Simple test that retry decorators are applied."""
        from src.processing.atomic_chunker import fix_formatting
        
        # Check that the function has the retry wrapper
        assert hasattr(fix_formatting, 'retry')
        
    @patch('src.processing.atomic_chunker.LLMClient')
    @patch('src.processing.atomic_chunker.clean_anki_text', return_value="cleaned text")  
    def test_fix_formatting_basic_function(self, mock_clean, mock_llm_class):
        """Test basic fix_formatting function behavior."""
        from src.processing.atomic_chunker import fix_formatting
        from src.models.cards import QACard
        
        test_card = QACard(type="Q&A", q="Test question", a="Test answer")
        
        mock_client = MagicMock()
        mock_llm_class.return_value = mock_client
        mock_client.generate.return_value = "formatted text"
        
        result = fix_formatting(test_card)
        
        # Should call the LLM client
        assert mock_llm_class.called
        assert result == test_card