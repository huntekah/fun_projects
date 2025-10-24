"""
Tests for atomic_chunker module.

Simple tests focusing on retry functionality and basic behavior.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestRetryFunctionality:
    """Test retry functionality using mock objects."""
    
    @patch('src.processing.atomic_chunker.LLMClient')
    @patch('src.processing.atomic_chunker.clean_anki_text', return_value="cleaned text")
    def test_fix_formatting_retries_on_error(self, mock_clean, mock_llm_class):
        """Test that retry decorator works on LLM errors."""
        # Import here to avoid dependency issues during collection
        from src.processing.atomic_chunker import fix_formatting
        from src.models.cards import QACard
        
        test_card = QACard(type="Q&A", q="Test question", a="Test answer")
        
        mock_client = MagicMock()
        mock_llm_class.return_value = mock_client
        
        # First two calls raise TypeError, third succeeds
        mock_client.generate.side_effect = [
            TypeError("Expected Pydantic response of type Union, but got NoneType"),
            TypeError("Expected Pydantic response of type Union, but got NoneType"), 
            test_card  # Success on third try
        ]
        
        result = fix_formatting(test_card)
        
        # Should retry twice and succeed on third attempt
        assert mock_client.generate.call_count == 3
        assert result == test_card