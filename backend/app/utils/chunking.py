"""
Text chunking utilities with Chinese language support
"""
from typing import List
import re

def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
    separators: List[str] = None
) -> List[str]:
    """
    Split text into chunks with overlap, optimized for Chinese text

    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks
        separators: List of separators to use for splitting (default: Chinese-optimized)

    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []

    # Default separators optimized for Chinese text
    if separators is None:
        separators = [
            "\n\n",  # Paragraph breaks
            "\n",    # Line breaks
            "。",    # Chinese period
            "！",    # Chinese exclamation
            "？",    # Chinese question mark
            "；",    # Chinese semicolon
            ".",     # English period
            "!",     # English exclamation
            "?",     # English question mark
            " ",     # Space
            ""       # Character-level fallback
        ]

    chunks = []
    current_chunk = ""

    # Split by separators recursively
    def split_recursive(text: str, seps: List[str]) -> List[str]:
        if not seps:
            # No more separators, split by character
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]

        separator = seps[0]
        remaining_seps = seps[1:]

        if not separator:
            # Empty separator means character-level split
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]

        # Split by current separator
        splits = text.split(separator)
        result = []

        for i, split in enumerate(splits):
            # Add separator back (except for last split)
            if i < len(splits) - 1:
                split = split + separator

            if len(split) > chunk_size:
                # Split is too large, use next separator
                result.extend(split_recursive(split, remaining_seps))
            else:
                result.append(split)

        return result

    # Get initial splits
    splits = split_recursive(text, separators)

    # Merge small splits and create chunks with overlap
    for split in splits:
        if not split.strip():
            continue

        # If adding this split would exceed chunk_size, save current chunk
        if len(current_chunk) + len(split) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())

            # Start new chunk with overlap from previous chunk
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + split
            else:
                current_chunk = split
        else:
            current_chunk += split

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunk_text_by_sentences(
    text: str,
    max_sentences: int = 5,
    overlap_sentences: int = 1
) -> List[str]:
    """
    Split text into chunks by sentences (Chinese and English)

    Args:
        text: Text to chunk
        max_sentences: Maximum number of sentences per chunk
        overlap_sentences: Number of sentences to overlap

    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []

    # Split by sentence endings (Chinese and English)
    sentence_pattern = r'[。！？\.!?]+[\s]*'
    sentences = re.split(sentence_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return [text]

    chunks = []
    i = 0

    while i < len(sentences):
        # Take max_sentences sentences
        chunk_sentences = sentences[i:i + max_sentences]
        chunk = " ".join(chunk_sentences)
        chunks.append(chunk)

        # Move forward by (max_sentences - overlap_sentences)
        i += max(1, max_sentences - overlap_sentences)

    return chunks


def create_chunks_with_metadata(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
    document_id: str = None,
    filename: str = None
) -> List[dict]:
    """
    Create chunks with metadata

    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks
        document_id: Document ID for metadata
        filename: Filename for metadata

    Returns:
        List of dictionaries with 'text' and 'metadata' keys
    """
    chunks = chunk_text(text, chunk_size, overlap)

    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            'text': chunk,
            'metadata': {
                'chunk_index': i,
                'total_chunks': len(chunks),
                'document_id': document_id,
                'filename': filename,
                'char_count': len(chunk)
            }
        })

    return result
