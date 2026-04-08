from __future__ import annotations

import math

from app.core.config import get_settings
from app.models.pipeline import GraphEdgeRecord, GraphNodeRecord
from app.pipeline.state import PipelineStateDict
from app.repositories.adapters.neo4j_store import Neo4jGraphStore
from app.services.embeddings import encode_texts


def graph_builder_node(state: PipelineStateDict) -> PipelineStateDict:
    papers = state.get("papers", [])
    if not papers:
        return {"graph_nodes": [], "graph_edges": [], "graph_summary": {"nodes": 0, "edges": 0}}

    embeddings = encode_texts([(p.title + " " + p.abstract).strip() for p in papers])
    sim = embeddings @ embeddings.T
    edge_map: dict[tuple[str, str, str], GraphEdgeRecord] = {}
    sim_threshold = 0.45
    min_top_k = 2 if len(papers) > 2 else 1

    for i in range(len(papers)):
        candidates: list[tuple[int, float]] = []
        for j in range(len(papers)):
            if i == j:
                continue
            w = float(sim[i, j])
            candidates.append((j, w))
            if w >= sim_threshold:
                source, target = sorted([papers[i].id, papers[j].id])
                edge_map[(source, target, "similarity")] = GraphEdgeRecord(
                    source=source, target=target, weight=round(w, 4), edge_type="similarity"
                )

        candidates.sort(key=lambda item: item[1], reverse=True)
        for j, w in candidates[:min_top_k]:
            if w <= 0:
                continue
            source, target = sorted([papers[i].id, papers[j].id])
            key = (source, target, "similarity")
            if key not in edge_map:
                edge_map[key] = GraphEdgeRecord(source=source, target=target, weight=round(w, 4), edge_type="similarity")

    ranked = sorted(papers, key=lambda p: p.citation_count, reverse=True)
    for p in papers:
        if p.citation_count <= 0:
            continue
        if ranked and ranked[0].id != p.id:
            source, target = sorted([p.id, ranked[0].id])
            edge_map[(source, target, "citation")] = GraphEdgeRecord(
                source=source,
                target=target,
                weight=round(min(1.0, math.log10(p.citation_count + 1) / 2), 4),
                edge_type="citation",
            )

    graph_nodes = [
        GraphNodeRecord(id=p.id, label=p.title, year=p.year, score=p.relevance_score, cluster=i % 6)
        for i, p in enumerate(papers)
    ]
    graph_edges = list(edge_map.values())

    settings = get_settings()
    store = Neo4jGraphStore(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password, settings.neo4j_database)
    store.upsert_papers([p.model_dump() for p in papers])
    store.upsert_edges(
        [{"source": e.source, "target": e.target, "weight": e.weight, "kind": e.edge_type} for e in graph_edges]
    )
    return {
        "graph_nodes": graph_nodes,
        "graph_edges": graph_edges,
        "graph_summary": {"nodes": len(graph_nodes), "edges": len(graph_edges)},
    }
