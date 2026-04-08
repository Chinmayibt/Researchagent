from app.models.pipeline import PaperRecord
from app.pipeline.nodes.insight_node import insight_node


def test_insight_contains_evidence_when_llm_empty(monkeypatch):
    papers = [
        PaperRecord(id="p1", title="Vision Transformers for Medical Imaging", abstract="clinical benchmark", citation_count=20, relevance_score=0.9, url="https://example.com/p1"),
        PaperRecord(id="p2", title="Medical Image Transformer Evaluation", abstract="benchmarking datasets", citation_count=11, relevance_score=0.8, url="https://example.com/p2"),
    ]

    monkeypatch.setattr("app.pipeline.nodes.insight_node.ask_json", lambda prompt, fallback: {})
    result = insight_node({"topic": "vision transformers medical imaging", "papers": papers, "structured_facts": []})
    insights = result["insights"]
    assert insights.trends
    assert insights.trend_items
    assert insights.trend_items[0].supporting_papers
