import React, { useMemo, useState } from "react";
import { extractKeyPoints } from "../lib/extractKeyPoints";
import { Paper } from "../services/api";

export default function PaperTable({ papers }: { papers?: Paper[] }) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("all");
  const [sort, setSort] = useState<"desc" | "asc">("desc");
  const [toast, setToast] = useState("");

  const rows = useMemo(() => {
    const list = papers ?? [];
    return list
      .filter((p) => {
        const matchQuery = p.title.toLowerCase().includes(query.toLowerCase());
        const matchSource = source === "all" || p.source === source;
        return matchQuery && matchSource;
      })
      .sort((a, b) =>
        sort === "desc" ? b.relevance_score - a.relevance_score : a.relevance_score - b.relevance_score
      );
  }, [papers, query, source, sort]);

  const copyKeyPoints = async (paper: Paper) => {
    const bullets = extractKeyPoints(paper.abstract || "");
    const text = bullets.map((b) => `• ${b}`).join("\n");
    try {
      await navigator.clipboard.writeText(text);
      setToast(`Copied key points: ${paper.title.slice(0, 40)}…`);
    } catch {
      setToast("Could not copy — select and copy manually.");
    }
    window.setTimeout(() => setToast(""), 3200);
  };

  return (
    <div className="card sources-card">
      <h3>Sources</h3>
      <div className="sources-toolbar">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter by title"
          aria-label="Filter papers by title"
        />
        <select value={source} onChange={(e) => setSource(e.target.value)} aria-label="Filter papers by source">
          <option value="all">All sources</option>
          <option value="openalex">OpenAlex</option>
          <option value="crossref">Crossref</option>
          <option value="arxiv">arXiv</option>
        </select>
        <button type="button" onClick={() => setSort((v) => (v === "desc" ? "asc" : "desc"))}>
          Score: {sort === "desc" ? "High to low" : "Low to high"}
        </button>
      </div>
      <p className="sr-only" aria-live="polite">
        {toast}
      </p>
      {toast ? (
        <p className="toast-inline" aria-hidden="true">
          {toast}
        </p>
      ) : null}
      {!papers?.length ? (
        <p className="muted">No papers yet.</p>
      ) : (
        <div className="paper-grid">
          {rows.map((p, i) => (
            <article key={`${p.id}-${i}`} className="paper-card">
              <h4>{p.title}</h4>
              <p className="muted">
                {(p.authors || []).slice(0, 3).join(", ") || "Unknown authors"} | {p.year ?? "-"} |{" "}
                {p.citation_count} citations
              </p>
              <p className="paper-key-points-label">Key points</p>
              <ul className="paper-key-points-list">
                {extractKeyPoints(p.abstract || "").map((pt, idx) => (
                  <li key={idx}>{pt}</li>
                ))}
              </ul>
              {p.abstract && p.abstract.length > 80 ? (
                <details className="paper-abstract-details">
                  <summary className="paper-abstract-details__summary">Full abstract</summary>
                  <p className="paper-abstract-full muted">{p.abstract}</p>
                </details>
              ) : null}
              <div className="paper-actions">
                <a href={p.url} target="_blank" rel="noreferrer" className="button-link">
                  View paper
                </a>
                <button type="button" className="button-ghost paper-copy-kp" onClick={() => copyKeyPoints(p)}>
                  Copy key points
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
