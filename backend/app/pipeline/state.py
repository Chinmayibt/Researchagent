from __future__ import annotations

from typing import TypedDict

from app.models.pipeline import (
    ExtractedAsset,
    GraphEdgeRecord,
    GraphNodeRecord,
    InsightOutput,
    PaperRecord,
    QueryPlan,
    ReportOutput,
    StructuredFact,
)


class PipelineStateDict(TypedDict, total=False):
    job_id: str
    status: str
    topic: str
    max_papers: int
    max_iterations: int
    errors: list[str]
    query_plan: QueryPlan
    papers: list[PaperRecord]
    extracted_assets: list[ExtractedAsset]
    structured_facts: list[StructuredFact]
    insights: InsightOutput
    report: ReportOutput
    graph_nodes: list[GraphNodeRecord]
    graph_edges: list[GraphEdgeRecord]
    graph_summary: dict[str, int]
    debug: dict[str, str]
