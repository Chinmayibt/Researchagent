import React, { useMemo, useState } from "react";
import { Insights } from "../services/api";

type Props = {
  insights?: Insights;
};

type TabId = "trends" | "gaps" | "conflicts" | "methods" | "emerging" | "papers";

const TAB_HINTS: Record<TabId, string> = {
  trends:
    "Cross-paper themes: what the corpus keeps doing, measuring, or claiming most often—and why that matters for the field.",
  gaps:
    "Open questions or weak spots: missing comparisons, datasets, or reporting that limit what we can conclude.",
  conflicts:
    "Tensions or contradictions: results or claims that disagree, and the most likely methodological reasons.",
  methods:
    "Recurring experimental or theoretical approaches inferred from titles and abstracts in this run.",
  emerging:
    "Newer directions or keywords that appear as the corpus evolves (heuristic from this retrieval set).",
  papers:
    "Papers the pipeline ranked as especially central or well supported—open links for full context.",
};

export default function InsightPanel({ insights }: Props) {
  const [tab, setTab] = useState<TabId>("trends");

  const sections = useMemo(() => {
    if (!insights) return null;
    return {
      trends:
        insights.trend_items?.length
          ? insights.trend_items
          : insights.trends.map((text) => ({ text, supporting_papers: [] })),
      gaps:
        insights.gap_items?.length
          ? insights.gap_items
          : insights.gaps.map((text) => ({ text, supporting_papers: [] })),
      conflicts:
        insights.contradiction_items?.length
          ? insights.contradiction_items
          : insights.contradictions.map((text) => ({ text, supporting_papers: [] })),
    };
  }, [insights]);

  if (!insights || !sections) {
    return (
      <div className="card insight-panel">
        <h3>Insights</h3>
        <p className="muted">Run research to view trends, gaps, and key papers.</p>
      </div>
    );
  }

  const tabs: { id: TabId; label: string }[] = [
    { id: "trends", label: "Trends" },
    { id: "gaps", label: "Gaps" },
    { id: "conflicts", label: "Conflicts" },
    { id: "methods", label: "Methods" },
    { id: "emerging", label: "Emerging" },
    { id: "papers", label: "Key papers" },
  ];

  const renderStatements = (items: typeof sections.trends) => (
    <ul className="insight-statement-list">
      {!items.length ? (
        <li className="muted">No items</li>
      ) : (
        items.map((item, i) => (
          <li key={i} className="insight-statement">
            <div>{item.text}</div>
            {item.supporting_papers?.length ? (
              <p className="muted insight-sources">
                Sources:{" "}
                {item.supporting_papers.map((sp, idx) => (
                  <span key={`${sp.paper_id}-${idx}`}>
                    {sp.url ? (
                      <a href={sp.url} target="_blank" rel="noreferrer">
                        {sp.title || sp.paper_id}
                      </a>
                    ) : (
                      <span>{sp.title || sp.paper_id}</span>
                    )}
                    {idx < (item.supporting_papers?.length ?? 0) - 1 ? ", " : ""}
                  </span>
                ))}
              </p>
            ) : null}
          </li>
        ))
      )}
    </ul>
  );

  return (
    <div className="card insight-panel">
      <h3>Insights</h3>
      <div className="insight-tabs" role="tablist" aria-label="Insight categories">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            className={`insight-tab ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <p className="insight-tab-hint" id={`insight-hint-${tab}`}>
        {TAB_HINTS[tab]}
      </p>

      <div className="insight-tab-panel" role="tabpanel" aria-describedby={`insight-hint-${tab}`}>
        {tab === "trends" && renderStatements(sections.trends)}
        {tab === "gaps" && renderStatements(sections.gaps)}
        {tab === "conflicts" && renderStatements(sections.conflicts)}
        {tab === "methods" && (
          <ul className="insight-chip-list">
            {insights.methodologies?.length ? (
              insights.methodologies.map((item, idx) => <li key={`m-${idx}`}>{item}</li>)
            ) : (
              <li className="muted">No methodology signals yet.</li>
            )}
          </ul>
        )}
        {tab === "emerging" && (
          <ul className="insight-chip-list">
            {insights.emerging_approaches?.length ? (
              insights.emerging_approaches.map((item, idx) => <li key={`e-${idx}`}>{item}</li>)
            ) : (
              <li className="muted">No emerging approach signals yet.</li>
            )}
          </ul>
        )}
        {tab === "papers" && (
          <ul className="insight-statement-list">
            {!insights.key_papers.length ? (
              <li className="muted">No highlighted papers yet.</li>
            ) : (
              insights.key_papers.map((paper, i) => (
                <li key={`paper-${i}`}>
                  <a href={paper.url} target="_blank" rel="noreferrer">
                    {paper.title}
                  </a>
                  <p className="muted">{paper.why_important}</p>
                </li>
              ))
            )}
          </ul>
        )}
      </div>
    </div>
  );
}
