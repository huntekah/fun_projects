from typing import Generator


def split_to_chunks(text: str, window_size: int, overlap: int) -> Generator[str, None, None]:
    """Split text into overlapping chunks, ensuring the last chunk is not shorter than overlap."""
    n = len(text)
    step = window_size - overlap
    i = 0

    while i + window_size < n:
        yield text[i:i + window_size]
        i += step

    i = _shift_start_backward(i, window_size, n, overlap)
    yield text[i:n]
    
def _shift_start_backward(pos: int, window_size: int, text_length: int, overlap: int) -> int:
    if text_length - pos < overlap and pos > 0:
        return max(0, text_length - window_size)
    return pos