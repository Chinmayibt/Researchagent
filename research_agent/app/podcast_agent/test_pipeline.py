from app.podcast_agent.services.pdf_service import extract_text
from app.podcast_agent.pipeline.chunking import chunk_text
from app.podcast_agent.services.embedding_service import embed_chunks
from app.podcast_agent.services.vector_store import build_index, search

import os


def main():
    # -------------------------------
    # Path setup
    # -------------------------------
    base_dir = os.getcwd()
    pdf_path = os.path.join(base_dir, "data", "sample.pdf")

    print(f"Using PDF path: {pdf_path}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    # -------------------------------
    # STEP 1: Extract
    # -------------------------------
    text = extract_text(pdf_path)
    print("\n✅ Extraction successful")

    # -------------------------------
    # STEP 2: Chunk
    # -------------------------------
    chunks = chunk_text(text)
    print(f"✅ Chunking successful | Total chunks: {len(chunks)}")

    # -------------------------------
    # STEP 3: Embeddings
    # -------------------------------
    embeddings = embed_chunks(chunks)
    print(f"\n✅ Embeddings generated | Shape: {embeddings.shape}")

    # -------------------------------
    # STEP 4: FAISS Index
    # -------------------------------
    index = build_index(embeddings)
    print("✅ FAISS index built")

    # -------------------------------
    # STEP 5: Retrieval
    # -------------------------------
    query = "What is the transformer model?"
    results = search(query, chunks, index, top_k=3)

    print("\n--- Retrieved Chunks ---\n")
    for i, r in enumerate(results):
        print(f"[{i+1}] {r[:200]}\n")


if __name__ == "__main__":
    main()