from __future__ import annotations

from app.models.pipeline import QueryPlan
from app.pipeline.debug_log import dbg
from app.pipeline.llm import ask_json
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event


def planner_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "planner", "Planning search strategy.")
    topic = state["topic"]
    fallback = {
        "sub_themes": [f"{topic} architecture", f"{topic} benchmarks", f"{topic} applications"],
        "queries": [topic, f"{topic} survey", f"{topic} benchmark", f"{topic} limitations"],
        "sequence": ["planner", "search", "pdf_extract", "asset_store", "structuring", "memory", "graph", "insight", "report"],
    }
    prompt = (
        "You are planner agent. Return strict JSON with keys sub_themes, queries, sequence. "
        f"Topic: {topic}"
    )
    plan_json = ask_json(prompt, fallback=fallback)
    plan = QueryPlan(
        sub_themes=plan_json.get("sub_themes", fallback["sub_themes"]),
        queries=plan_json.get("queries", fallback["queries"]),
        sequence=plan_json.get("sequence", fallback["sequence"]),
    )
    # region agent log
    dbg(
        run_id="pre-fix",
        hypothesis_id="H3",
        location="planner_node.py:29",
        message="planner produced query plan",
        data={"plan_type": type(plan).__name__, "query_count": len(plan.queries)},
    )
    # endregion
    emit_event(state, "planner", f"Prepared {len(plan.queries)} search queries.", {"query_count": len(plan.queries)})
    return {"query_plan": plan, "status": "running"}
