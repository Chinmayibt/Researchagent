import React from "react";
import { formatConfidence } from "../../lib/formatConfidence";
import { labelStage } from "../../lib/stageLabels";

type RunStatus = "idle" | "running" | "completed";

type Props = {
  sourcesAnalyzed: number;
  stageKey: string;
  confidenceRaw: string;
  runStatus: RunStatus;
};

function statusLabel(s: RunStatus): string {
  if (s === "running") return "Running";
  if (s === "completed") return "Completed";
  return "Idle";
}

export default function LiveMetricsStrip({ sourcesAnalyzed, stageKey, confidenceRaw, runStatus }: Props) {
  const { display: confDisplay, title: confTitle } = formatConfidence(confidenceRaw);
  const statusClass = `status status-${statusLabel(runStatus).toLowerCase()}`;

  return (
    <section className="kpi-grid" aria-label="Live run metrics">
      <div className="card kpi-card">
        <p className="muted">Run status</p>
        <p className={`kpi-value ${statusClass}`}>{statusLabel(runStatus)}</p>
      </div>
      <div className="card kpi-card">
        <p className="muted">Sources analyzed</p>
        <p className="kpi-value">{sourcesAnalyzed}</p>
      </div>
      <div className="card kpi-card">
        <p className="muted">Processing stage</p>
        <p className="kpi-value kpi-value--stage">{labelStage(stageKey)}</p>
      </div>
      <div className="card kpi-card">
        <p className="muted">Confidence</p>
        <p className="kpi-value" title={confTitle}>
          {confDisplay}
        </p>
        <p className="kpi-hint muted">{confTitle}</p>
      </div>
    </section>
  );
}
