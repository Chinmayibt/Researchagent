from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

_model = None  # 🔥 lazy load


def get_model():
    global _model

    if _model is None:
        print("🔄 Loading embedding model...")

        _model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            cache_folder="./models"   # optional but recommended
        )

        print("✅ Model loaded")

    return _model


def embed_chunks(chunks: List[str]) -> np.ndarray:
    model = get_model()

    embeddings = model.encode(
        chunks,
        batch_size=16,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings