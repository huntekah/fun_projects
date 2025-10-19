from difflib import SequenceMatcher
from typing import List
from connectors.llm.structured_gemini import LLMClient


def merge_overlapping_chunks(chunk1: str, chunk2: str, overlap_size: int) -> str:
    """
    Merges two potentially slightly different, overlapping text chunks.

    This is designed for cases where a non-deterministic process (like an LLM)
    has cleaned or altered the chunks, so the overlapping text may not be identical.
    It uses SequenceMatcher to find the best point of alignment.
    """
    search_window = min(len(chunk1), len(chunk2), overlap_size)

    overlap1 = chunk1[-search_window:]
    overlap2 = chunk2[:search_window]

    matcher = SequenceMatcher(None, overlap1, overlap2, autojunk=False)
    match = matcher.find_longest_match(0, len(overlap1), 0, len(overlap2))

    min_match_threshold = 20
    if match.size < min_match_threshold:
        llm_client = LLMClient()
        chunk1_unique = chunk1[:-search_window]
        prompt = f"""You are a text-cleaning assistant. The following text are two consecutive chunks extracted from a PDF. They should be overlapping, but for some reason automatic merge mechanism failed.
It may contain formatting errors like random headers, footers, and unnecessary line breaks that interrupt sentences.

Your task is to:
1. Join two chunks into one continuous text.
The beginning of the chapter may not be included in this chunk, so only add chapter headers if they are clearly indicated. Do not worry about cutting off (or starting) mid-sentence when working on those chunks, as they will be merged to another chunks.

Do not change the wording or summarize the content. Simply return the merged text.

Here is the first chunk:
\"\"\"
{overlap1}
\"\"\"
Here is the second chunk:
\"\"\"
{overlap2}
\"\"\"
"""

        unified_overlap = llm_client.generate(prompt, schema=str)
        merged_text = chunk1_unique + unified_overlap + chunk2[search_window:]
        print(f"used llm to merge, common fragment length: {len(unified_overlap)}")
        return merged_text

    cut_point_in_chunk1 = len(chunk1) - search_window + match.a
    start_point_in_chunk2 = match.b

    merged_text = chunk1[:cut_point_in_chunk1] + chunk2[start_point_in_chunk2:]
    print(f"common fragment length: {match.size}")
    return merged_text


def merge_chunks(cleaned_chunks: List[str], overlap: int) -> str:
    """Merge a list of cleaned chunks into a single document."""
    if not cleaned_chunks:
        return ""
    
    if len(cleaned_chunks) == 1:
        return cleaned_chunks[0]

    merged_document = cleaned_chunks[0]

    for i in range(1, len(cleaned_chunks)):
        merged_document = merge_overlapping_chunks(merged_document, cleaned_chunks[i], overlap)

    return merged_document