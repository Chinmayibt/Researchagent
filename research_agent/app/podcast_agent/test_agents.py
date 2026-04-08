from app.podcast_agent.services.pdf_service import extract_text
from app.podcast_agent.pipeline.chunking import chunk_text
from app.podcast_agent.services.embedding_service import embed_chunks
from app.podcast_agent.services.vector_store import build_index, search

from app.podcast_agent.agents.planner import generate_plan
from app.podcast_agent.agents.writer import generate_script
from app.podcast_agent.agents.critic import review_script

import os


def main():
    # -------------------------------
    # Load PDF
    # -------------------------------
    base_dir = os.getcwd()
    pdf_path = os.path.join(base_dir, "data", "sample.pdf")

    print(f"Using PDF: {pdf_path}")

    text = extract_text(pdf_path)
    chunks = chunk_text(text, max_words=400)

    # -------------------------------
    # Embeddings + Retrieval
    # -------------------------------
    embeddings = embed_chunks(chunks)
    index = build_index(embeddings)

    queries = [
        "Transformer architecture explanation",
        "self-attention mechanism",
        "encoder decoder transformer",
        "key contributions of transformer paper"
    ]

    retrieved_chunks = []

    for q in queries:
        results = search(q, chunks, index, top_k=2)
        retrieved_chunks.extend(results)

    # Remove duplicates
    retrieved_chunks = list(set(retrieved_chunks))
    context = "\n\n".join(retrieved_chunks)

    print("\n--- CONTEXT ---\n")
    print(context[:1000])

    # -------------------------------
    # Planner
    # -------------------------------
    plan = generate_plan(context)
    print("\n--- PLAN ---\n")
    print(plan)

    # -------------------------------
    # Writer
    # -------------------------------
    script = generate_script(context, plan)
    print("\n--- RAW SCRIPT ---\n")
    print(script)

    # -------------------------------
    # Critic
    # -------------------------------
    final_script = review_script(script, context)
    print("\n--- FINAL SCRIPT ---\n")
    print(final_script)

    # -------------------------------
    # Word Count Check
    # -------------------------------
    word_count = len(final_script.split())
    print(f"\n✅ Word Count: {word_count} words")


if __name__ == "__main__":
    main()