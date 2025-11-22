"""
chunking.py

Lógica para dividir el texto en chunks manejables
para el modelo de embeddings / RAG.
"""

from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 200,
) -> List[str]:
    """
    Divide un texto largo en trozos con solapamiento.

    chunk_size: número aproximado de caracteres por chunk.
    chunk_overlap: caracteres que se repiten entre chunks consecutivos.
    """
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - chunk_overlap

    return chunks
