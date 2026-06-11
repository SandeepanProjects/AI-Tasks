from pydantic import BaseModel


class DocumentChunk(BaseModel):

    chunk_id: str

    text: str

    metadata: dict