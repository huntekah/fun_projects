import re
from typing import List, Dict, Any

def sanitize_filename(name: str) -> str:
    """Removes invalid characters from a string to make it a valid filename."""
    name = re.sub(r'^[#\s]+', '', name)
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s]+', '_', name)
    return name[:20]

def split_markdown_into_sections(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Parses a markdown string using regex and splits it into a list of sections
    based on headers. Handles literal \n characters in text.
    """
    # First convert literal \n to actual newlines
    text = markdown_text.replace('\\n', '\n')
    
    # This pattern splits the text by lines that start with '#' (headers)
    # The parentheses in the pattern ensure the headers are kept in the output
    split_pattern = r'(^#+\s+.*$)'
    
    # Split the text by the header pattern. re.MULTILINE is key here.
    parts = re.split(split_pattern, text, flags=re.MULTILINE)
    
    sections = []
    # The first item in `parts` is anything before the first header. We skip it.
    # Then, we iterate through the list in pairs: (header, content).
    for i in range(1, len(parts), 2):
        header_line = parts[i].strip()
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        
        # Determine the header level by counting the '#' characters at the start.
        level = 0
        for char in header_line:
            if char == '#':
                level += 1
            else:
                break
        
        # The heading is the header line without the '#' characters.
        heading = header_line.lstrip('#').strip()
        
        sections.append({
            'level': level,
            'heading': heading,
            'content': content,
        })
        
    return sections

# Example Usage:
if __name__ == '__main__':
    markdown_input = """
This text comes before the first header and will be ignored.

# Section 1
This is the content for the first section.

## Subsection 1.1
This content belongs to subsection 1.1.
It can have multiple lines.

# Section 2
- This is the second section.
- It contains a list.
"""
    try:
        extracted = split_markdown_into_sections(markdown_input)
        import json
        print("✅ Success! Extracted sections:")
        print(json.dumps(extracted, indent=2))
    except Exception as e:
        print(f"❌ An error occurred: {e}")