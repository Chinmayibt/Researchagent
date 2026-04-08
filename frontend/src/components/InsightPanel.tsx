import React from "react";
import { Insights } from "../services/api";

type Props = {
  insights?: Insights;
};

export default function InsightPanel({ insights }: Props) {
  if (!insights) {
    return (
      <div className="card">
        <h3>Insights</h3>
        <p className="muted">Run research to view trends, gaps, and key papers.</p>
      </div>
    );
  }

  const sections = [
    {
      label: "Trends",
      items: insights.trend_items?.length
        ? insights.trend_items
        : insights.trends.map((text) => ({ text, supporting_papers: [] })),
    },
    {
      label: "Research gaps",
      items: insights.gap_items?.length
        ? insights.gap_items
        : insights.gaps.map((text) => ({ text, supporting_papers: [] })),
    },
    {
      label: "Contradictions",
      items: insights.contradiction_items?.length
        ? insights.contradiction_items
        : insights.contradictions.map((text) => ({ text, supporting_papers: [] })),
    },
  ];

  return (
    <div className="card">
      <h3>Insights</h3>
      <div className="insight-grid">
        {sections.map((section) => (
          <section key={section.label} className="insight-block">
            <h4>{section.label}</h4>
            {!section.items.length ? (
              <p className="muted">No items</p>
            ) : (
              <ul>
                {section.items.map((item, i) => (
                  <li key={`${section.label}-${i}`}>
                    <div>{item.text}</div>
                    {item.supporting_papers?.length ? (
                      <p className="muted">
                        Sources:{" "}
                        {item.supporting_papers.map((sp, idx) => (
                          <React.Fragment key={`${sp.paper_id}-${idx}`}>
                            {sp.url ? (
                              <a href={sp.url} target="_blank" rel="noreferrer">
                                {sp.title || sp.paper_id}
                              </a>
                            ) : (
                              <span>{sp.title || sp.paper_id}</span>
                            )}
                            {idx < item.supporting_papers.length - 1 ? ", " : ""}
                          </React.Fragment>
                        ))}
                      </p>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </div>
      <section className="insight-block">
        <h4>Key papers</h4>
        {!insights.key_papers.length ? (
          <p className="muted">No highlighted papers yet.</p>
        ) : (
          <ul>
            {insights.key_papers.map((paper, i) => (
              <li key={`paper-${i}`}>
                <a href={paper.url} target="_blank" rel="noreferrer">
                  {paper.title}
                </a>
                <p className="muted">{paper.why_important}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
