from __future__ import annotations

from app.models.pipeline import StructuredFact
from app.pipeline.llm import ask_json
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event


def structuring_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "structuring", "Extracting benchmark facts.")
    facts: list[StructuredFact] = []
    for asset in state.get("extracted_assets", []):
        if asset.asset_type not in {"table", "text_chunk"}:
            continue
        snippet = (asset.content_text or "")[:1200]
        if not snippet:
            continue
        fallback = {"facts": []}
        prompt = (
            "Extract benchmark facts as JSON: {facts:[{model_name,dataset,metric,value,year}]}. "
            f"Text: {snippet}"
        )
        parsed = ask_json(prompt, fallback=fallback)
        for item in parsed.get("facts", [])[:6]:
            facts.append(
                StructuredFact(
                    paper_id=asset.paper_id,
                    model_name=str(item.get("model_name", "unknown")),
                    dataset=str(item.get("dataset", "unknown")),
                    metric=str(item.get("metric", "unknown")),
                    value=str(item.get("value", "unknown")),
                    year=int(item["year"]) if isinstance(item.get("year"), int) else None,
                    evidence_asset_id=asset.asset_id,
                )
            )
    emit_event(state, "structuring", f"Structured {len(facts)} facts.", {"fact_count": len(facts)})
    return {"structured_facts": facts}
