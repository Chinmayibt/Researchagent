from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


JobStatus = Literal["queued", "running", "completed", "partial_success", "failed"]


class PipelineRequest(BaseModel):
    topic: str = Field(min_length=3)
    max_papers: int | None = Field(default=None, ge=10, le=100)
    max_iterations: int | None = Field(default=None, ge=1, le=8)


class QueryPlan(BaseModel):
    sub_themes: list[str] = []
    queries: list[str] = []
    sequence: list[str] = []


class PaperRecord(BaseModel):
    id: str
    title: str
    abstract: str = ""
    year: int | None = None
    citation_count: int = 0
    url: str = ""
    source: str = ""
    authors: list[str] = []
    topics: list[str] = []
    relevance_score: float = 0.0
    doi: str | None = None
    pdf_url: str | None = None


class ExtractedAsset(BaseModel):
    asset_id: str
    paper_id: str
    asset_type: Literal["image", "table", "text_chunk"]
    page_number: int
    caption: str = ""
    storage_uri: str | None = None
    content_text: str | None = None
    metadata: dict[str, str] = {}


class StructuredFact(BaseModel):
    paper_id: str
    model_name: str
    dataset: str
    metric: str
    value: str
    year: int | None = None
    evidence_asset_id: str | None = None


class GraphNodeRecord(BaseModel):
    id: str
    label: str
    year: int | None = None
    score: float = 0.0
    cluster: int = 0


class GraphEdgeRecord(BaseModel):
    source: str
    target: str
    weight: float
    edge_type: Literal["citation", "similarity"]


class InsightEvidence(BaseModel):
    paper_id: str
    title: str
    url: str = ""


class InsightStatement(BaseModel):
    text: str
    supporting_papers: list[InsightEvidence] = []


class InsightOutput(BaseModel):
    trends: list[str] = []
    gaps: list[str] = []
    contradictions: list[str] = []
    methodologies: list[str] = []
    emerging_approaches: list[str] = []
    key_papers: list[dict] = []
    trend_items: list[InsightStatement] = []
    gap_items: list[InsightStatement] = []
    contradiction_items: list[InsightStatement] = []
    research_fronts: list[str] = []
    open_problems: list[str] = []


class ReportOutput(BaseModel):
    markdown: str
    title: str
    citations: list[str] = []
    asset_refs: list[str] = []
    report_uri: str | None = None


class PipelineResult(BaseModel):
    topic: str
    papers: list[PaperRecord]
    insights: InsightOutput
    graph_nodes: list[GraphNodeRecord]
    graph_edges: list[GraphEdgeRecord]
    graph_summary: dict[str, int]
    report: ReportOutput
    assets: list[ExtractedAsset]


class PipelineState(BaseModel):
    job_id: str
    status: JobStatus = "queued"
    topic: str
    max_papers: int = 30
    max_iterations: int = 3
    errors: list[str] = []
    query_plan: QueryPlan | None = None
    papers: list[PaperRecord] = []
    extracted_assets: list[ExtractedAsset] = []
    structured_facts: list[StructuredFact] = []
    insights: InsightOutput | None = None
    report: ReportOutput | None = None
    graph_nodes: list[GraphNodeRecord] = []
    graph_edges: list[GraphEdgeRecord] = []
    graph_summary: dict[str, int] = {}
    debug: dict[str, str] = {}


class CreateJobResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    topic: str
    progress: dict[str, str] = {}
    errors: list[str] = []
    last_event_seq: int = 0

