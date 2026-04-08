import faiss
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

# ✅ LOAD ONCE (GLOBAL)
_model = SentenceTransformer("all-MiniLM-L6-v2")


def build_index(embeddings: np.ndarray):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def search(query: str, chunks: List[str], index, top_k: int = 4) -> List[str]:
    query_embedding = _model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]