import React from "react";
import { Activity } from "lucide-react";
import { RunResearchResponse } from "../../services/api";

type RightPanelProps = {
  data: RunResearchResponse | null;
  loading: boolean;
  reportLink: string | null;
  stage: string;
  sourcesAnalyzed: number;
  confidence: string;
};

export default function RightPanel({ data, loading, reportLink, stage, sourcesAnalyzed, confidence }: RightPanelProps) {
  const statusLabel = loading ? "Running" : data ? "Completed" : "Idle";

  return (
    <aside className="right-panel card">
      <h2>
        <Activity size={16} /> Info
      </h2>
      <div className="panel-group">
        <p className="muted">Status</p>
        <p className={`status status-${statusLabel.toLowerCase()}`}>{statusLabel}</p>
      </div>

      <div className="panel-group">
        <p className="muted">Processing stage</p>
        <p className="metric">{stage || "idle"}</p>
      </div>

      <div className="panel-group">
        <p className="muted">Sources analyzed</p>
        <p className="metric">{sourcesAnalyzed}</p>
      </div>

      <div className="panel-group">
        <p className="muted">Confidence</p>
        <p className="metric">{confidence}</p>
      </div>

      {reportLink ? (
        <a className="button-link" href={reportLink} target="_blank" rel="noreferrer">
          Download PDF report
        </a>
      ) : (
        <button type="button" className="button-link disabled" disabled>
          PDF available after run
        </button>
      )}
    </aside>
  );
}
