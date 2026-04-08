from __future__ import annotations

import numpy as np

from app.core.config import get_settings
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event
from app.repositories.adapters.faiss_store import FaissVectorStore
from app.services.embeddings import encode_texts


def memory_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "memory", "Indexing papers and facts in vector memory.")
    settings = get_settings()
    store = FaissVectorStore(settings.faiss_index_path, settings.faiss_metadata_path)
    papers = state.get("papers", [])
    if not papers:
        return {}

    paper_texts = [(p.title + " " + p.abstract).strip() for p in papers]
    vectors = encode_texts(paper_texts)
    ids = [p.id for p in papers]
    meta = [{"kind": "paper", "title": p.title, "year": p.year} for p in papers]
    store.upsert(ids, np.array(vectors), meta)

    facts = state.get("structured_facts", [])
    if facts:
        fact_texts = [f"{f.model_name} {f.dataset} {f.metric} {f.value}" for f in facts]
        fact_vectors = encode_texts(fact_texts)
        fact_ids = [f"fact:{i}:{f.paper_id}" for i, f in enumerate(facts)]
        fact_meta = [{"kind": "fact", "paper_id": f.paper_id, "metric": f.metric} for f in facts]
        store.upsert(fact_ids, np.array(fact_vectors), fact_meta)

    emit_event(state, "memory", f"Indexed {len(ids)} papers and {len(facts)} facts.")
    return {"debug": {"memory": f"indexed {len(ids)} papers and {len(facts)} facts"}}
