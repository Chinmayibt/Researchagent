import React, { useMemo } from "react";
import { reportUrl } from "../services/api";

type StoredReport = {
  jobId: string;
  topic: string;
  finishedAt: string;
};

export default function Reports() {
  const reports = useMemo(() => {
    const raw = window.localStorage.getItem("researchReports");
    if (!raw) return [] as StoredReport[];
    try {
      return JSON.parse(raw) as StoredReport[];
    } catch {
      return [] as StoredReport[];
    }
  }, []);

  return (
    <main className="workspace">
      <section className="card">
        <h2>Reports</h2>
        {!reports.length ? (
          <p className="muted">No reports yet. Run a research topic to generate one.</p>
        ) : (
          <ul className="report-list">
            {reports.map((report) => (
              <li key={report.jobId} className="report-item">
                <div>
                  <p>{report.topic}</p>
                  <p className="muted">{new Date(report.finishedAt).toLocaleString()}</p>
                </div>
                <a className="button-link" href={reportUrl(report.jobId)} target="_blank" rel="noreferrer">
                  Download PDF
                </a>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
