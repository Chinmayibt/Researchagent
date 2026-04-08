from __future__ import annotations

from pathlib import Path

from app.models.pipeline import ReportOutput
from app.pipeline.llm import ask_json
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event
from app.services.report import export_pdf


def report_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "report", "Generating final report.")
    insights = state.get("insights")
    if not insights:
        report = ReportOutput(markdown="# Empty report", title=state["topic"])
        return {"report": report}

    fallback = {
        "title": f"Literature Review: {state['topic']}",
        "markdown": "",
    }
    prompt = (
        "Write a structured literature review markdown with sections: intro, trends, gaps, contradictions, key papers, open problems. "
        f"Topic: {state['topic']}. Insights: {insights.model_dump_json()}"
    )
    generated = ask_json(prompt, fallback=fallback)
    markdown = generated.get("markdown") or ""
    if not markdown:
        lines = [
            f"# Literature Review: {state['topic']}",
            "",
            "## Trends",
            *[f"- {x}" for x in insights.trends],
            "",
            "## Gaps",
            *[f"- {x}" for x in insights.gaps],
            "",
            "## Contradictions",
            *[f"- {x}" for x in insights.contradictions],
            "",
            "## Key Papers",
            *[f"- [{k['title']}]({k['url']}) - {k['why_important']}" for k in insights.key_papers],
        ]
        markdown = "\n".join(lines)

    pdf_path = Path("reports") / f"{state['job_id']}.pdf"
    export_pdf(markdown, pdf_path)
    report = ReportOutput(
        markdown=markdown,
        title=generated.get("title", fallback["title"]),
        citations=[k["title"] for k in insights.key_papers[:20]],
        asset_refs=[a.asset_id for a in state.get("extracted_assets", [])[:50]],
        report_uri=str(pdf_path),
    )
    emit_event(state, "report", "Report generated and saved.", {"report_uri": str(pdf_path)})
    return {"report": report}
