from typing import Generator


def split_to_chunks(text: str, window_size: int, overlap: int) -> Generator[str, None, None]:
    """Split text into overlapping chunks."""
    step = window_size - overlap
    for i in range(0, len(text), step):
        yield text[i:i + window_size]