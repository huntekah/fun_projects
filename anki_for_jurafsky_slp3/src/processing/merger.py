from difflib import SequenceMatcher
from typing import List


def merge_overlapping_chunks(chunk1: str, chunk2: str, overlap_size: int) -> str:
    """
    Merges two potentially slightly different, overlapping text chunks.

    This is designed for cases where a non-deterministic process (like an LLM)
    has cleaned or altered the chunks, so the overlapping text may not be identical.
    It uses SequenceMatcher to find the best point of alignment.
    """
    print(f"{len(chunk1)=}, {len(chunk2)=}, {overlap_size=}")
    search_window = min(len(chunk1), len(chunk2), overlap_size)

    overlap1 = chunk1[-search_window:]
    overlap2 = chunk2[:search_window]

    matcher = SequenceMatcher(None, overlap1, overlap2, autojunk=False)
    match = matcher.find_longest_match(0, len(overlap1), 0, len(overlap2))

    min_match_threshold = 20
    if match.size < min_match_threshold:
        raise ValueError(
            f"Could not find a reliable overlap (best match: {match.size} chars). "
            "Chunks may be too dissimilar or the overlap is too small."
        )

    cut_point_in_chunk1 = len(chunk1) - search_window + match.a
    start_point_in_chunk2 = match.b

    merged_text = chunk1[:cut_point_in_chunk1] + chunk2[start_point_in_chunk2:]
    print(f"Merged length: {len(merged_text)}")
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