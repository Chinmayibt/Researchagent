from app.models.pipeline import PaperRecord
from app.pipeline.nodes.graph_builder_node import graph_builder_node


def test_graph_builder_produces_edges(monkeypatch):
    papers = [
        PaperRecord(id="p1", title="Vision Transformer in medicine", abstract="benchmark dataset A", citation_count=25),
        PaperRecord(id="p2", title="Medical ViT benchmark", abstract="dataset A benchmark", citation_count=12),
        PaperRecord(id="p3", title="Transformer for radiology", abstract="dataset B comparison", citation_count=5),
    ]

    def fake_encode_texts(_texts):
        import numpy as np

        return np.array(
            [
                [1.0, 0.1, 0.0],
                [0.95, 0.1, 0.0],
                [0.7, 0.2, 0.1],
            ]
        )

    class DummyStore:
        def upsert_papers(self, _papers):
            return None

        def upsert_edges(self, _edges):
            return None

    monkeypatch.setattr("app.pipeline.nodes.graph_builder_node.encode_texts", fake_encode_texts)
    monkeypatch.setattr("app.pipeline.nodes.graph_builder_node.Neo4jGraphStore", lambda *args, **kwargs: DummyStore())

    result = graph_builder_node({"papers": papers})
    assert result["graph_summary"]["nodes"] == 3
    assert result["graph_summary"]["edges"] > 0
    assert len(result["graph_edges"]) > 0
