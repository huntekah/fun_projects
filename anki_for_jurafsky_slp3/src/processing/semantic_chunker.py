import mistune
import re
from typing import List, Dict, Any


def sanitize_filename(name: str) -> str:
    """Removes invalid characters from a string to make it a valid filename."""
    name = re.sub(r'^[#\s]+', '', name)
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s]+', '_', name)
    return name


class SectionSplitter(mistune.BaseRenderer):
    """A mistune renderer that splits a Markdown document into sections based on headings."""
    
    def __init__(self):
        super().__init__()
        self.sections: List[Dict[str, Any]] = []
        self._current_section = None
        self._capture_buffer = []

    def heading(self, text: str, level: int):
        self._finalize_section()
        self._current_section = {'heading': text, 'level': level}
        return ''

    def paragraph(self, text: str):
        self._capture_buffer.append(text)
        return ''

    def list(self, text: str, ordered: bool, level: int):
        self._capture_buffer.append(text)
        return ''

    def block_code(self, code: str, info: str = None):
        self._capture_buffer.append(f"```\n{code}\n```")
        return ''

    def block_quote(self, text: str):
        self._capture_buffer.append(f"> {text}")
        return ''
    
    def thematic_break(self):
        self._capture_buffer.append('---')
        return ''

    def _finalize_section(self):
        """Saves the content captured in the buffer to the current section."""
        if self._current_section and self._capture_buffer:
            self._current_section['content'] = '\n\n'.join(self._capture_buffer).strip()
            self.sections.append(self._current_section)
        self._capture_buffer = []

    def finalize(self):
        """Call this after parsing to save the very last section."""
        self._finalize_section()
        return self.sections


def split_markdown_into_sections(markdown_text: str) -> List[Dict[str, Any]]:
    """Parses a markdown string and splits it into a list of sections."""
    renderer = SectionSplitter()
    parser = mistune.create_markdown(renderer=renderer)
    parser(markdown_text)
    return renderer.finalize()