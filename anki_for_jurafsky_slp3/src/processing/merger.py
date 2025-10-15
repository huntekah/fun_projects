from difflib import SequenceMatcher
from typing import List


def merge_overlapping_chunks(chunk1: str, chunk2: str, overlap_size: int) -> str:
    """Merges two overlapping text chunks by finding the longest common substring."""
    overlap1 = chunk1[-overlap_size:]
    overlap2 = chunk2[:overlap_size]

    matcher = SequenceMatcher(None, overlap1, overlap2)
    match = matcher.find_longest_match(0, len(overlap1), 0, len(overlap2))

    if match.size < 20:
        raise ValueError("Could not find a reliable overlap to merge chunks.")

    start_of_match_in_chunk1_overlap = match.a
    cut_off_point_in_chunk1 = len(chunk1) - overlap_size + start_of_match_in_chunk1_overlap
    
    merged_text = chunk1[:cut_off_point_in_chunk1] + chunk2
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