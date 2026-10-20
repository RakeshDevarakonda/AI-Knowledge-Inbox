from typing import List

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    """
    Splits text into chunks of `chunk_size` characters with `overlap`.
    
    Why overlap?
    If an important sentence gets cut in half across a chunk boundary, 
    the overlap ensures the meaning is preserved in both chunks.
    """
    text = text.strip()
    if not text:
        return []

    # If shorter than chunk size, return single chunk
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks
