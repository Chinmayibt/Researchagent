from __future__ import annotations

from collections import Counter

from app.models.pipeline import InsightEvidence, InsightOutput, InsightStatement
from app.pipeline.llm import ask_json
from app.pipeline.state import PipelineStateDict


def _paper_index(papers):
    return {p.id: p for p in papers}


def _build_fallback_insights(state: PipelineStateDict, top_papers) -> InsightOutput:
    topic = state["topic"]
    papers = state.get("papers", [])
    tokens = Counter()
    for p in papers:
        for w in (p.title + " " + p.abstract).lower().split():
            cleaned = w.strip(".,:;()[]{}")
            if len(cleaned) > 5:
                tokens[cleaned] += 1

    common = [w for w, _ in tokens.most_common(6)]
    key0 = common[0] if common else "methods"
    key1 = common[1] if len(common) > 1 else "benchmarks"

    def evidence_for(p):
        return InsightEvidence(paper_id=p.id, title=p.title, url=p.url or "")

    trend_items = []
    gap_items = []
    contradiction_items = []
    if top_papers:
        trend_items.append(
            InsightStatement(
                text=f"In {topic}, top-ranked papers emphasize {key0} and {key1}.",
                supporting_papers=[evidence_for(p) for p in top_papers[:2]],
            )
        )
        gap_items.append(
            InsightStatement(
                text=f"Across the collected corpus, reporting around {key1} is inconsistent across studies.",
                supporting_papers=[evidence_for(p) for p in top_papers[:2]],
            )
        )
        contradiction_items.append(
            InsightStatement(
                text="Papers with similar problem settings report varying gains, indicating unresolved evaluation variance.",
                supporting_papers=[evidence_for(p) for p in top_papers[:2]],
            )
        )

    return InsightOutput(
        trends=[x.text for x in trend_items],
        gaps=[x.text for x in gap_items],
        contradictions=[x.text for x in contradiction_items],
        trend_items=trend_items,
        gap_items=gap_items,
        contradiction_items=contradiction_items,
        research_fronts=[key0, key1],
        open_problems=["cross-paper comparability", "dataset shift robustness"],
        key_papers=[
            {
                "paper_id": p.id,
                "title": p.title,
                "url": p.url,
                "why_important": f"Relevance {p.relevance_score:.2f}, citations {p.citation_count}",
            }
            for p in top_papers
        ],
    )


def insight_node(state: PipelineStateDict) -> PipelineStateDict:
    papers = state.get("papers", [])
    if not papers:
        return {"insights": InsightOutput()}

    top = sorted(papers, key=lambda p: (p.relevance_score, p.citation_count), reverse=True)[:8]
    tokens = Counter()
    for p in papers:
        for w in (p.title + " " + p.abstract).lower().split():
            if len(w) > 5:
                tokens[w.strip(".,:;()[]{}")] += 1

    facts = state.get("structured_facts", [])
    fact_lines = [
        f"{f.paper_id}: model={f.model_name}, dataset={f.dataset}, metric={f.metric}, value={f.value}" for f in facts[:40]
    ]
    paper_lines = [
        f"{p.id}|{p.title}|year={p.year}|citations={p.citation_count}|score={p.relevance_score:.3f}" for p in top
    ]
    fallback = _build_fallback_insights(state, top)
    prompt = (
        "Return STRICT JSON with keys trends,gaps,contradictions,research_fronts,open_problems where each of "
        "trends/gaps/contradictions is an array of objects {text,supporting_papers:[{paper_id,title}]}. "
        f"Topic={state['topic']}. Top papers={paper_lines}. Facts={fact_lines}. "
        f"Keywords={', '.join([k for k, _ in tokens.most_common(12)])}"
    )
    generated = ask_json(prompt, fallback={})
    paper_lookup = _paper_index(papers)

    def to_statements(items, fallback_items):
        statements = []
        for item in items or []:
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            supports = []
            for sp in item.get("supporting_papers", [])[:4]:
                pid = str(sp.get("paper_id", ""))
                paper = paper_lookup.get(pid)
                supports.append(
                    InsightEvidence(
                        paper_id=pid or (paper.id if paper else ""),
                        title=str(sp.get("title", "")) or (paper.title if paper else ""),
                        url=paper.url if paper else "",
                    )
                )
            statements.append(InsightStatement(text=text, supporting_papers=supports))
        return statements if statements else fallback_items

    trend_items = to_statements(generated.get("trends"), fallback.trend_items)
    gap_items = to_statements(generated.get("gaps"), fallback.gap_items)
    contradiction_items = to_statements(generated.get("contradictions"), fallback.contradiction_items)

    insights = InsightOutput(
        trends=[x.text for x in trend_items],
        gaps=[x.text for x in gap_items],
        contradictions=[x.text for x in contradiction_items],
        trend_items=trend_items,
        gap_items=gap_items,
        contradiction_items=contradiction_items,
        research_fronts=generated.get("research_fronts", fallback.research_fronts),
        open_problems=generated.get("open_problems", fallback.open_problems),
        key_papers=fallback.key_papers,
    )
    return {"insights": insights}
