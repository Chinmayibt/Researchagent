import React, { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { extractReportSections } from "../../lib/reportSections";

type Props = {
  reportMarkdown: string | undefined;
  onCopyFull: () => void;
};

export default function ReportSection({ reportMarkdown, onCopyFull }: Props) {
  const sections = useMemo(() => extractReportSections(reportMarkdown ?? ""), [reportMarkdown]);
  const [copied, setCopied] = useState(false);
  const full = (reportMarkdown ?? "").trim();

  const handleCopy = () => {
    onCopyFull();
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="card report-section" aria-label="Report preview">
      <div className="report-section__header">
        <h3>Report</h3>
        {full ? (
          <button type="button" onClick={handleCopy} className="button-ghost" aria-live="polite">
            {copied ? "Copied" : "Copy full markdown"}
          </button>
        ) : null}
      </div>

      <div className="report-prose">
        <h4>Abstract</h4>
        <div className="markdown-body">
          <ReactMarkdown>
            {sections.abstract || "_Run research to generate a report preview._"}
          </ReactMarkdown>
        </div>

        <h4>Key findings</h4>
        <div className="markdown-body">
          <ReactMarkdown>{sections.findings || "_No findings section detected._"}</ReactMarkdown>
        </div>

        <h4>Methodology</h4>
        <div className="markdown-body">
          <ReactMarkdown>{sections.methods || "_No methodology section detected._"}</ReactMarkdown>
        </div>
      </div>

      {full ? (
        <details className="report-full-markdown">
          <summary className="report-full-markdown__summary">Full report (markdown)</summary>
          <div className="markdown-body report-full-markdown__body">
            <ReactMarkdown>{full}</ReactMarkdown>
          </div>
        </details>
      ) : null}
    </section>
  );
}
