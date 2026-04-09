import React from "react";

type TopbarProps = {
  topic: string;
  onTopicChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  canSubmit: boolean;
  reportPdfHref: string | null;
};

export default function Topbar({
  topic,
  onTopicChange,
  onSubmit,
  loading,
  canSubmit,
  reportPdfHref,
}: TopbarProps) {
  return (
    <header className="topbar">
      <div className="topbar-copy">
        <p className="muted topbar-tagline">Mantis · Autonomous research workspace</p>
        <h1>Enter a topic, AI does the rest</h1>
      </div>
      <div className="topbar-actions">
        <label htmlFor="topic-search" className="sr-only">
          Research topic
        </label>
        <input
          id="topic-search"
          value={topic}
          onChange={(e) => onTopicChange(e.target.value)}
          placeholder="Search topic (e.g. graph neural networks in healthcare)"
          aria-label="Research topic"
        />
        <div className="topbar-run-row">
          <button type="button" className="primary" onClick={onSubmit} disabled={!canSubmit}>
            {loading ? "Running..." : "Run research"}
          </button>
          {reportPdfHref ? (
            <a className="button-link topbar-pdf-link" href={reportPdfHref} target="_blank" rel="noreferrer">
              Download PDF report
            </a>
          ) : (
            <span className="topbar-pdf-hint muted" title="Complete a research run to generate a PDF">
              PDF after run
            </span>
          )}
        </div>
      </div>
    </header>
  );
}
