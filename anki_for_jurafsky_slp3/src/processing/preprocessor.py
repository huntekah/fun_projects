from pathlib import Path
from connectors.llm.structured_gemini import LLMClient
from pydantic import BaseModel




def create_text_cleaning_prompt(chapter_name: str, text: str) -> str:
    if chapter_name.startswith("chapter_"):
        chapter_id = chapter_name.replace("chapter_", "Chapter ")
    elif chapter_name.startswith("appendix_"):
        chapter_id = chapter_name.replace("appendix_", "Appendix ")
    else:
        chapter_id = chapter_name
    
    prompt = f"""You are a text-cleaning assistant. The following text is a chunk of {chapter_id} extracted from a PDF. It contains formatting errors like random headers, footers, and unnecessary line breaks that interrupt sentences.

Your task is to:
1. Remove any headers or footers (e.g., "Chapter 5," if its not the beginning of the chapter, page numbers, publication titles).
2. Join sentences that have been split across multiple lines.
3. Ensure paragraphs are properly formatted.
4. Make sure each chapter, sub-chapter is defined with proper markdown like `# Chapter 5`, `## 8.1 Attention` or `### 13.2.1 RNN in production`. 
The beginning of the chapter may not be included in this chunk, so only add chapter headers if they are clearly indicated. Since chunks will be merged later, do not worry about cutting off mid-sentence when working on this chunk.
5. If an array or a sample starts with literal `#` like an array row  `# e x e c u t i o n` or a python comment fragment, then escape the `#` with a backslash like `\\# e x e c u t i o n` so it is not interpreted as a header.

Do not change the wording or summarize the content. Simply return the cleaned, corrected text.

Here is the text:
\"\"\"
{text}
\"\"\"
"""
    
    return prompt


def clean_chapter_text(chapter_name: str, raw_text: str) -> str:
    llm_client = LLMClient()
    prompt = create_text_cleaning_prompt(chapter_name, raw_text)
    result = llm_client.generate(prompt,str)
    return result

