from __future__ import annotations

from collections import Counter

from app.models.pipeline import InsightEvidence, InsightOutput, InsightStatement
from app.pipeline.llm import ask_json
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event


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
                text=(
                    f"Across works on {topic}, the retrieved corpus repeatedly centers on '{key0}' and '{key1}'. "
                    f"High-ranked papers tend to frame these as core levers for performance or validity. "
                    "This pattern suggests the field is converging on a shared vocabulary even when experimental setups differ."
                ),
                supporting_papers=[evidence_for(p) for p in top_papers[:2]],
            )
        )
        gap_items.append(
            InsightStatement(
                text=(
                    f"A recurring limitation is inconsistent reporting around '{key1}': datasets, splits, and baselines are not always comparable. "
                    "Readers should treat headline numbers cautiously until protocols standardize. "
                    "This gap matters for reproducibility and for fair comparison across institutions."
                ),
                supporting_papers=[evidence_for(p) for p in top_papers[:2]],
            )
        )
        contradiction_items.append(
            InsightStatement(
                text=(
                    "Several papers with overlapping problem settings report different gains, which often reflects "
                    "evaluation variance (metrics, data slices, or training budgets) rather than a single 'correct' result. "
                    "Until analyses isolate these factors, apparent disagreements may be partly methodological."
                ),
                supporting_papers=[evidence_for(p) for p in top_papers[:2]],
            )
        )

    return InsightOutput(
        trends=[x.text for x in trend_items],
        gaps=[x.text for x in gap_items],
        contradictions=[x.text for x in contradiction_items],
        methodologies=["systematic reviews", "benchmark comparisons"] if top_papers else [],
        emerging_approaches=[key0, key1],
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
    emit_event(state, "insight", "Generating evidence-backed insights.")
    papers = state.get("papers", [])
    if not papers:
        return {"insights": InsightOutput()}

    top = sorted(papers, key=lambda p: (p.relevance_score, p.citation_count), reverse=True)[:15]
    tokens = Counter()
    for p in papers:
        for w in (p.title + " " + p.abstract).lower().split():
            if len(w) > 5:
                tokens[w.strip(".,:;()[]{}")] += 1

    facts = state.get("structured_facts", [])
    fact_lines = [
        f"{f.paper_id}: model={f.model_name}, dataset={f.dataset}, metric={f.metric}, value={f.value}" for f in facts[:40]
    ]
    paper_blocks = []
    for p in top:
        excerpt = (p.abstract or "").replace("\n", " ").strip()[:360]
        paper_blocks.append(
            f"=== paper_id={p.id} | {p.title} | year={p.year} | score={p.relevance_score:.3f} | cites={p.citation_count} ===\n{excerpt}"
        )
    paper_context = "\n\n".join(paper_blocks)
    fallback = _build_fallback_insights(state, top)
    n_all = len(papers)
    min_items_rule = (
        "Provide at least 3 distinct objects in each of trends, gaps, and contradictions when the corpus has 5+ papers; "
        "otherwise provide as many well-grounded items as possible (minimum 1 each)."
        if n_all >= 5
        else "Provide as many well-grounded items as the corpus supports (minimum 1 each for trends, gaps, contradictions)."
    )
    prompt = (
        "Return STRICT JSON with keys trends,gaps,contradictions,methodologies,emerging_approaches,research_fronts,open_problems. "
        "Each of trends, gaps, contradictions must be an array of objects {\"text\": string, \"supporting_papers\": [{\"paper_id\", \"title\"}]}. "
        f"{min_items_rule} "
        'Each "text" value must be 2 to 5 complete sentences in plain language: briefly define specialized terms, '
        "name concrete comparisons or mechanisms where possible, and state why the point matters for a reader new to the subfield. "
        "Ground claims in the paper excerpts below and set supporting_papers to the paper_id values you rely on.\n\n"
        f"Topic: {state['topic']}\n"
        f"Structured facts (sample): {fact_lines}\n"
        f"Corpus keywords: {', '.join([k for k, _ in tokens.most_common(14)])}\n\n"
        f"PAPER EXCERPTS:\n{paper_context}"
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
        methodologies=generated.get("methodologies", []),
        emerging_approaches=generated.get("emerging_approaches", generated.get("research_fronts", fallback.research_fronts)),
        key_papers=fallback.key_papers,
    )
    emit_event(
        state,
        "insight",
        f"Generated {len(trend_items)} trends, {len(gap_items)} gaps, and {len(contradiction_items)} conflicting findings.",
    )
    return {"insights": insights}
