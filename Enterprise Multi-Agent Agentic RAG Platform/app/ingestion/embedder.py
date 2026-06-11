from app.rag.embeddings import get_embeddings


def create_embeddings(chunks):

    embeddings = get_embeddings()

    texts = [
        chunk.page_content
        for chunk in chunks
    ]

    vectors = embeddings.embed_documents(texts)

    return texts, vectors