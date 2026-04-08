import re
from typing import List


def split_into_sentences(text: str) -> List[str]:
    """
    Basic sentence splitter using regex.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, max_words: int = 500) -> List[str]:
    """
    Create semantically meaningful chunks without breaking sentences.

    Args:
        text (str): Full document text
        max_words (int): Max words per chunk

    Returns:
        List[str]: List of chunks
    """
    sentences = split_into_sentences(text)

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        word_count = len(sentence.split())

        # If adding exceeds limit → push current chunk
        if current_word_count + word_count > max_words:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_word_count = word_count
        else:
            current_chunk.append(sentence)
            current_word_count += word_count

    # Add last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks