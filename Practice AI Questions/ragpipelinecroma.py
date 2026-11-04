import streamlit as st
import wikipedia
import chromadb
import numpy as np
import re
import os

from dataclasses import dataclass
from typing import List, Dict

from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline,
)

# import streamlit as st
# import wikipedia
# import chromadb
# import numpy as np
# import re
# import os

# 🚀 ADD THIS LINE IMMEDIATELY AFTER IMPORTS TO FIX THE WIKIPEDIA ERROR:
wikipedia.set_user_agent("MyRagApp/1.0 (contact: your_email@example.com)")

# ============================================================
# 1. STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Production-Style RAG",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Production-Style RAG Pipeline")
st.caption(
    "Wikipedia → Chunking → Embeddings → ChromaDB → Reranking → LLM"
)


# ============================================================
# 2. CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
GENERATION_MODEL = "google/flan-t5-base"

TOP_K_RETRIEVAL = 10
TOP_K_RERANK = 4

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


# ============================================================
# 3. DATA MODEL
# ============================================================

@dataclass
class DocumentChunk:
    """
    Represents one chunk of a document.
    """
    chunk_id: int
    text: str
    source: str
    title: str


# ============================================================
# 4. LOAD EMBEDDING MODEL
# ============================================================

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


# ============================================================
# 5. LOAD RERANKER
# ============================================================

@st.cache_resource
def load_reranker():
    return CrossEncoder(RERANKER_MODEL)


# ============================================================
# 6. LOAD GENERATION MODEL
# ============================================================

# @st.cache_resource
# def load_generation_model():
#     tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL)
#     model = AutoModelForCausalLM.from_pretrained(GENERATION_MODEL)
    
#     generator = pipeline(
#         "text2text-generation",
#         model=model,
#         tokenizer=tokenizer,
#         max_new_tokens=200,
#     )
#     return generator

# ============================================================
# 6. LOAD GENERATION MODEL
# ============================================================

@st.cache_resource
def load_generation_model():
    tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL)

    # Update this line to use Seq2SeqLM
    model = AutoModelForSeq2SeqLM.from_pretrained(GENERATION_MODEL)

    generator = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=200,
    )
    return generator


# ============================================================
# 7. LOAD WIKIPEDIA DOCUMENT
# ============================================================

def load_wikipedia_document(topic: str):
    try:
        page = wikipedia.page(topic, auto_suggest=False)
        return {
            "title": page.title,
            "text": page.content,
            "url": page.url,
        }
    except wikipedia.exceptions.PageError:
        st.error(f"No Wikipedia page found for '{topic}'.")
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        st.error("The topic is ambiguous. Try one of these:")
        st.write(e.options[:10])
        return None
    except Exception as e:
        st.error(f"Error loading Wikipedia page: {e}")
        return None


# ============================================================
# 8. CLEAN DOCUMENT
# ============================================================

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


# ============================================================
# 9. SENTENCE-AWARE CHUNKING
# ============================================================

def chunk_document(
    text: str,
    title: str,
    source: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[DocumentChunk]:
    text = clean_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_chunk = []
    current_length = 0
    chunk_id = 0

    for sentence in sentences:
        words = sentence.split()
        sentence_length = len(words)

        if current_length + sentence_length > chunk_size and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    source=source,
                    title=title,
                )
            )
            chunk_id += 1

            overlap_words = []
            current_words = " ".join(current_chunk).split()
            if len(current_words) > overlap:
                overlap_words = current_words[-overlap:]

            current_chunk = overlap_words
            current_length = len(overlap_words)

        current_chunk.extend(words)
        current_length += sentence_length

    if current_chunk:
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=" ".join(current_chunk),
                source=source,
                title=title,
            )
        )
    return chunks


# ============================================================
# 10. CREATE CHROMA VECTOR INDEX (Fixed for ChromaDB)
# ============================================================

def create_vector_index(chunks: List[DocumentChunk], embedding_model):
    """
    Initializes an in-memory ChromaDB collection and adds text embeddings.
    """
    # 1. Initialize an ephemeral (in-memory) Chroma client
    chroma_client = chromadb.EphemeralClient()
    
    # 2. Create or reset a collection configured for Cosine similarity
    collection = chroma_client.create_collection(
        name="rag_pipeline_collection",
        metadata={"hnsw:space": "cosine"}
    )
    
    # 3. Extract text blocks and generate embeddings via SentenceTransformers
    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()  # Chroma expects Python lists, not raw numpy arrays

    # 4. Construct metadata structures for metadata-filtering capabilities
    metadatas = [
        {"source": chunk.source, "title": chunk.title, "chunk_id": chunk.chunk_id}
        for chunk in chunks
    ]
    ids = [f"id_{chunk.chunk_id}" for chunk in chunks]
    
    # 5. Populate Chroma DB collection
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    return collection, embeddings


# ============================================================
# 11. RETRIEVE DOCUMENTS (Fixed for ChromaDB)
# ============================================================

def retrieve_documents(
    query: str,
    collection,
    chunks: List[DocumentChunk],
    embedding_model,
    top_k: int = TOP_K_RETRIEVAL,
):
    """
    Queries ChromaDB utilizing precomputed sentence embeddings.
    """
    # 1. Generate text query vector representation
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()

    # 2. Extract relative documents through nearest neighbor searching
    query_results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, len(chunks))
    )
    
    results = []
    
    # 3. Flatten structural mapping back into unified document blocks
    if query_results and "documents" in query_results and query_results["documents"]:
        # Extract returned components safely
        documents = query_results["documents"][0]
        distances = query_results["distances"][0]
        metadatas = query_results["metadatas"][0]
        
        for doc, distance, meta in zip(documents, distances, metadatas):
            # Chroma returns distance metrics. For cosine space, similarity = 1 - distance
            similarity_score = 1.0 - float(distance)
            
            # Construct a transient object mirroring your original setup
            matched_chunk = DocumentChunk(
                chunk_id=meta["chunk_id"],
                text=doc,
                source=meta["source"],
                title=meta["title"]
            )
            
            results.append({
                "chunk": matched_chunk,
                "score": similarity_score
            })
            
    return results


# ============================================================
# 12. RERANK DOCUMENTS
# ============================================================

def rerank_documents(
    query: str,
    retrieved_documents: List[Dict],
    reranker,
    top_k: int = TOP_K_RERANK,
):
    if not retrieved_documents:
        return []

    # Format data blocks cleanly for cross-encoder inference processing
    pairs = [[query, doc["chunk"].text] for doc in retrieved_documents]
    rerank_scores = reranker.predict(pairs)

    for doc, score in zip(retrieved_documents, rerank_scores):
        doc["rerank_score"] = float(score)

    # Sort results in descending order by rerank scores
    sorted_docs = sorted(
        retrieved_documents, 
        key=lambda x: x["rerank_score"], 
        reverse=True
    )
    
    return sorted_docs[:top_k]


# ============================================================
# 13. MAIN STREAMLIT UI IMPLEMENTATION INTERACTION
# ============================================================

# if __name__ == "__main__":
#     # Initialize basic model loading resources dynamically inside streamlit frame
#     with st.spinner("Initializing models..."):
#         embed_mod = load_embedding_model()
#         rerank_mod = load_reranker()
#         gen_mod = load_generation_model()

#     # Sidebar inputs layout configuration
#     st.sidebar.header("Data Source Configuration")
#     wiki_topic = st.sidebar.text_input("Wikipedia Search Topic", value="Artificial Intelligence")
    
#     if st.sidebar.button("Fetch and Process Document"):
#         with st.spinner("Extracting content from Wikipedia..."):


# ============================================================
# 13. MAIN STREAMLIT UI IMPLEMENTATION INTERACTION
# ============================================================

if __name__ == "__main__":
    # Initialize basic model loading resources dynamically inside streamlit frame
    with st.spinner("Initializing models..."):
        embed_mod = load_embedding_model()
        rerank_mod = load_reranker()
        gen_mod = load_generation_model()

    # Sidebar inputs layout configuration
    st.sidebar.header("Data Source Configuration")
    wiki_topic = st.sidebar.text_input("Wikipedia Search Topic", value="Artificial Intelligence")
    
    if st.sidebar.button("Fetch and Process Document"):
        with st.spinner("Extracting content from Wikipedia..."):
            wiki_data = load_wikipedia_document(wiki_topic)
            
        if wiki_data:
            st.session_state["wiki_title"] = wiki_data["title"]
            st.session_state["wiki_source"] = wiki_data["url"]
            
            with st.spinner("Processing structural text breakdown into sentences..."):
                processed_chunks = chunk_document(
                    text=wiki_data["text"],
                    title=wiki_data["title"],
                    source=wiki_data["url"]
                )
                st.session_state["chunks"] = processed_chunks
                
            with st.spinner("Building Chroma vector index..."):
                index, embeddings = create_vector_index(processed_chunks, embed_mod)
                st.session_state["vector_index"] = index
                st.success(f"Successfully processed {len(processed_chunks)} document blocks!")

    # Check if index metadata exists before serving searching prompt layout block
    if "vector_index" in st.session_state and "chunks" in st.session_state:
        st.subheader(f"Query Knowledge Base: *{st.session_state.get('wiki_title')}*")
        user_query = st.text_input("Enter your question based on document resources:")
        
        if user_query:
            with st.spinner("Retrieving from vector workspace..."):
                raw_retrieved = retrieve_documents(
                    query=user_query,
                    collection=st.session_state["vector_index"],
                    chunks=st.session_state["chunks"],
                    embedding_model=embed_mod
                )
                
            with st.spinner("Reranking relevant search nodes..."):
                reranked_results = rerank_documents(
                    query=user_query,
                    retrieved_documents=raw_retrieved,
                    reranker=rerank_mod
                )
            
            # 🚨 FIX 1: Truncate context to keep total tokens under FLAN-T5's 512-token limit
            # Only use the top 1 or 2 reranked chunks to prevent overflow
            safe_results = reranked_results[:2] 
            context_string = "\n\n".join([f"Source [{doc['chunk'].title}]: {doc['chunk'].text}" for doc in safe_results])
            
            input_prompt = f"Answer the following question explicitly using the provided reference source context.\n\nContext:\n{context_string}\n\nQuestion: {user_query}\nAnswer:"
            
            with st.spinner("Generating targeted response..."):
                llm_output = gen_mod(input_prompt)
                
                # 🚨 FIX 2: Correctly unpack the list index from the pipeline output
                if isinstance(llm_output, list) and len(llm_output) > 0:
                    generated_text = llm_output[0]["generated_text"]
                else:
                    generated_text = "Error: Model failed to generate a response structure."
                
            # Render layout presentation blocks
            st.markdown("### 🤖 Model Response")
            st.write(generated_text)
            
            with st.expander("🔍 View Retrieved and Reranked Context Blocks"):
                for idx, item in enumerate(reranked_results):
                    st.markdown(f"**Rank {idx + 1}** | Chroma Score: `{item['score']:.4f}` | Rerank Score: `{item['rerank_score']:.4f}`")
                    st.info(item["chunk"].text)

        
        # if user_query:
        #     with st.spinner("Retrieving from vector workspace..."):
        #         raw_retrieved = retrieve_documents(
        #             query=user_query,
        #             collection=st.session_state["vector_index"],
        #             chunks=st.session_state["chunks"],
        #             embedding_model=embed_mod
        #         )
                
        #     with st.spinner("Reranking relevant search nodes..."):
        #         reranked_results = rerank_documents(
        #             query=user_query,
        #             retrieved_documents=raw_retrieved,
        #             reranker=rerank_mod
        #         )
            
        #     # Format combined system context injection parameters
        #     context_string = "\n\n".join([f"Source [{doc['chunk'].title}]: {doc['chunk'].text}" for doc in reranked_results])
        #     input_prompt = f"Answer the following question explicitly using the provided reference source context.\n\nContext:\n{context_string}\n\nQuestion: {user_query}\nAnswer:"
            
        #     with st.spinner("Generating targeted response..."):
        #         llm_output = gen_mod(input_prompt)
        #         generated_text = llm_output["generated_text"]
                
        #     # Render layout presentation blocks
        #     st.markdown("### 🤖 Model Response")
        #     st.write(generated_text)
            
        #     with st.expander("🔍 View Retrieved and Reranked Context Blocks"):
        #         for idx, item in enumerate(reranked_results):
        #             st.markdown(f"**Rank {idx + 1}** | Chroma Score: `{item['score']:.4f}` | Rerank Score: `{item['rerank_score']:.4f}`")
        #             st.info(item["chunk"].text)
