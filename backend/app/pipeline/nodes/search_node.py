from __future__ import annotations

import asyncio

from app.core.config import get_settings
from app.models.pipeline import PaperRecord
from app.pipeline.debug_log import dbg
from app.pipeline.search_clients import fetch_arxiv, fetch_crossref, fetch_openalex
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event


def _score(topic: str, paper: PaperRecord) -> float:
    t = set(topic.lower().split())
    p = set((paper.title + " " + paper.abstract).lower().split())
    if not t:
        return 0.0
    return round(len(t.intersection(p)) / len(t), 3)


async def _run_queries(topic: str, queries: list[str]) -> list[PaperRecord]:
    settings = get_settings()
    merged: dict[str, PaperRecord] = {}
    for q in queries:
        results = await asyncio.gather(
            fetch_openalex(q, limit=12, mailto=settings.openalex_email, timeout_seconds=settings.source_timeout_seconds),
            fetch_crossref(q, limit=10, mailto=settings.crossref_mailto, timeout_seconds=settings.source_timeout_seconds),
            fetch_arxiv(q, limit=8, timeout_seconds=settings.source_timeout_seconds),
            return_exceptions=True,
        )
        batch: list[PaperRecord] = []
        for r in results:
            if isinstance(r, Exception):
                continue
            batch.extend(r)
        for p in batch:
            key = p.doi or p.id or f"{p.title}:{p.year}"
            p.relevance_score = _score(topic, p)
            existing = merged.get(key)
            if not existing or p.relevance_score > existing.relevance_score:
                merged[key] = p
    ranked = sorted(merged.values(), key=lambda x: (x.relevance_score, x.citation_count), reverse=True)
    return ranked


def search_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "search", "Searching OpenAlex, Crossref, and arXiv.")
    # region agent log
    qp = state.get("query_plan")
    dbg(
        run_id="pre-fix",
        hypothesis_id="H1",
        location="search_node.py:49",
        message="search node inspecting query_plan",
        data={
            "query_plan_type": type(qp).__name__ if qp is not None else "NoneType",
            "query_plan_has_queries_attr": hasattr(qp, "queries") if qp is not None else False,
            "state_keys": sorted(list(state.keys())),
        },
    )
    # endregion
    queries = state["query_plan"].queries if state.get("query_plan") else [state["topic"]]
    papers = asyncio.run(_run_queries(state["topic"], queries))
    emit_event(state, "search", f"Retrieved {len(papers)} unique papers.", {"sources_analyzed": len(papers)})
    return {"papers": papers[: state.get("max_papers", 30)]}
