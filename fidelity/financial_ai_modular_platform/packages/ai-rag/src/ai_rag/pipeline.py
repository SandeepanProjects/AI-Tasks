from .models import Chunk

def fixed_size_chunks(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks

def chunks_from_document(document_id: str, text: str) -> list[Chunk]:
    return [
        Chunk(chunk_id=f"{document_id}:{i}", document_id=document_id, text=value)
        for i, value in enumerate(fixed_size_chunks(text))
    ]
