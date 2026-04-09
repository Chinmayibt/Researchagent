from __future__ import annotations

from pathlib import Path

from app.models.pipeline import PaperRecord, ReportOutput
from app.pipeline.llm import ask_json
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event
from app.services.report import export_pdf


def _corpus_digest(papers: list[PaperRecord], limit: int = 20, abstract_cap: int = 400) -> str:
    if not papers:
        return "(no papers in corpus)"
    ranked = sorted(papers, key=lambda p: (p.relevance_score, p.citation_count), reverse=True)[:limit]
    lines: list[str] = []
    for p in ranked:
        ex = (p.abstract or "").replace("\n", " ").strip()
        if len(ex) > abstract_cap:
            ex = ex[: abstract_cap - 1] + "…"
        lines.append(
            f"- [{p.id}] {p.title} (year={p.year}, rel={p.relevance_score:.3f}, cites={p.citation_count})\n  excerpt: {ex}"
        )
    return "\n".join(lines)


def _fallback_markdown(topic: str, insights, papers: list[PaperRecord]) -> str:
    lines = [
        f"# Literature review: {topic}",
        "",
        "## Abstract",
        "",
        f"This document summarizes retrieved literature on **{topic}** ({len(papers)} papers in corpus). "
        "Structured insights below list dominant themes, gaps, and tensions.",
        "",
        "## Key findings",
        "",
        *[f"- {x}" for x in insights.trends],
        "",
        "## Methodology",
        "",
        "Corpus was assembled via autonomous retrieval and ranking; graph and insight stages aggregate evidence across abstracts.",
        "",
        "## Gaps noted",
        *[f"- {x}" for x in insights.gaps],
        "",
        "## Contradictions",
        *[f"- {x}" for x in insights.contradictions],
        "",
        "## Key papers",
        *[f"- [{k['title']}]({k['url']}) — {k['why_important']}" for k in insights.key_papers],
    ]
    return "\n".join(lines)


def report_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "report", "Generating final report.")
    insights = state.get("insights")
    papers: list[PaperRecord] = state.get("papers") or []
    if not insights:
        report = ReportOutput(markdown="# Empty report", title=state["topic"])
        return {"report": report}

    title_fallback = f"Literature Review: {state['topic']}"
    fallback_body = {
        "title": title_fallback,
        "markdown": _fallback_markdown(state["topic"], insights, papers),
    }
    digest = _corpus_digest(papers)
    prompt = (
        'Return STRICT JSON with keys "title" and "markdown" only. '
        "The markdown must be a literature review in Markdown. "
        "Use these level-2 headings in this order (optional ## Introduction before Abstract and ## Conclusion after Methodology): "
        "## Abstract\n\n## Key findings\n\n## Methodology\n\n"
        "Rules: (1) Each of Abstract, Key findings, and Methodology must contain at least two substantial paragraphs of prose "
        "(bullets allowed sparingly). (2) Synthesize across the corpus—recurring themes, methods, disagreements—not only the JSON bullets. "
        "(3) Refer to patterns implied by multiple papers where possible.\n\n"
        f"Topic: {state['topic']}\n\n"
        f"Structured insights (JSON): {insights.model_dump_json()}\n\n"
        f"Corpus (top papers by relevance, with abstract excerpts):\n{digest}"
    )
    generated = ask_json(prompt, fallback=fallback_body)
    markdown = (generated.get("markdown") or "").strip()
    if not markdown:
        markdown = fallback_body["markdown"]

    pdf_path = Path("reports") / f"{state['job_id']}.pdf"
    export_pdf(markdown, pdf_path)
    report = ReportOutput(
        markdown=markdown,
        title=str(generated.get("title") or title_fallback),
        citations=[k["title"] for k in insights.key_papers[:20]],
        asset_refs=[a.asset_id for a in state.get("extracted_assets", [])[:50]],
        report_uri=str(pdf_path),
    )
    emit_event(state, "report", "Report generated and saved.", {"report_uri": str(pdf_path)})
    return {"report": report}
