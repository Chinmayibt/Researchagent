import React from "react";

type TopbarProps = {
  topic: string;
  onTopicChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  canSubmit: boolean;
};

export default function Topbar({ topic, onTopicChange, onSubmit, loading, canSubmit }: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <p className="muted">Autonomous Research AI Workspace</p>
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
        <button type="button" className="primary" onClick={onSubmit} disabled={!canSubmit}>
          {loading ? "Running..." : "Run research"}
        </button>
      </div>
    </header>
  );
}
