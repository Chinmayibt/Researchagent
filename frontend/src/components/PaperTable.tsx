import React, { useMemo, useState } from "react";
import { Paper } from "../services/api";

export default function PaperTable({ papers }: { papers?: Paper[] }) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("all");
  const [sort, setSort] = useState<"desc" | "asc">("desc");

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

  const highlightIdea = (paper: Paper) => {
    const sentence = (paper.abstract || "")
      .split(".")
      .map((x) => x.trim())
      .find((x) => x.length > 20);
    return sentence ? `${sentence}.` : "No key sentence available.";
  };

  return (
    <div className="card">
      <h3>Sources</h3>
      <div className="table-toolbar">
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
      {!papers?.length ? (
        <p>No papers yet.</p>
      ) : (
        <div className="paper-grid">
          {rows.map((p, i) => (
            <article key={`${p.id}-${i}`} className="paper-card">
              <h4>{p.title}</h4>
              <p className="muted">
                {(p.authors || []).slice(0, 3).join(", ") || "Unknown authors"} | {p.year ?? "-"} | {p.citation_count} citations
              </p>
              <p className="paper-summary">{(p.abstract || "No summary available.").slice(0, 220)}</p>
              <div className="paper-actions">
                <a href={p.url} target="_blank" rel="noreferrer" className="button-link">
                  View Paper
                </a>
                <button type="button" onClick={() => window.alert(highlightIdea(p))}>
                  Highlight key idea
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
