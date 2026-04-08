import React, { useMemo, useState } from "react";
import GraphView from "../components/GraphView";
import InsightPanel from "../components/InsightPanel";
import PaperTable from "../components/PaperTable";
import RightPanel from "../components/layout/RightPanel";
import Topbar from "../components/layout/Topbar";
import { PipelineEvent, reportUrl, RunResearchResponse, runResearch } from "../services/api";

export default function Home() {
  const [topic, setTopic] = useState("retrieval augmented generation");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<RunResearchResponse | null>(null);
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [stage, setStage] = useState("idle");
  const [sourcesAnalyzed, setSourcesAnalyzed] = useState(0);
  const [confidence, setConfidence] = useState("n/a");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const canSubmit = !loading && topic.trim().length >= 3;

  const relatedPapers = useMemo(() => {
    if (!selectedNode || !data) {
      return [];
    }
    const neighborIds = new Set<string>([selectedNode]);
    for (const edge of data.graph_edges) {
      if (edge.source === selectedNode) neighborIds.add(edge.target);
      if (edge.target === selectedNode) neighborIds.add(edge.source);
    }
    return data.papers.filter((paper) => neighborIds.has(paper.id)).slice(0, 6);
  }, [selectedNode, data]);

  const reportPreview = useMemo(() => {
    if (!data?.report_markdown) {
      return { abstract: "", findings: "", methods: "" };
    }
    const markdown = data.report_markdown;
    const abstractMatch = markdown.match(/##\s*Abstract([\s\S]*?)(##|$)/i);
    const findingsMatch = markdown.match(/##\s*(Key findings|Trends)([\s\S]*?)(##|$)/i);
    const methodsMatch = markdown.match(/##\s*(Methodology|Methods)([\s\S]*?)(##|$)/i);
    return {
      abstract: (abstractMatch?.[1] ?? markdown.slice(0, 280)).trim(),
      findings: (findingsMatch?.[2] ?? "").trim(),
      methods: (methodsMatch?.[2] ?? "").trim(),
    };
  }, [data?.report_markdown]);

  const submit = async () => {
    setLoading(true);
    setError("");
    setEvents([]);
    setStage("queued");
    setSourcesAnalyzed(0);
    setConfidence("n/a");
    try {
      const result = await runResearch(
        { topic },
        {
          onEvent: (evt) => {
            setEvents((prev) => [...prev, evt]);
            setStage(evt.stage || "running");
            const sourceCount = Number(evt.meta?.sources_analyzed);
            if (!Number.isNaN(sourceCount) && sourceCount > 0) {
              setSourcesAnalyzed(sourceCount);
            }
          },
          onProgress: (progress) => {
            if (progress.stage) setStage(progress.stage);
            if (progress.sources_analyzed) setSourcesAnalyzed(Number(progress.sources_analyzed) || 0);
            if (progress.confidence) setConfidence(progress.confidence);
          },
        }
      );
      setData(result);
      setStage("completed");
      setSourcesAnalyzed(result.papers.length);
      window.localStorage.setItem(
        "researchReports",
        JSON.stringify([
          { jobId: result.job_id, topic: result.topic, finishedAt: new Date().toISOString() },
          ...JSON.parse(window.localStorage.getItem("researchReports") ?? "[]"),
        ].slice(0, 40))
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to run research");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <main className="workspace">
        <Topbar
          topic={topic}
          onTopicChange={setTopic}
          onSubmit={submit}
          loading={loading}
          canSubmit={canSubmit}
        />

        <section className="card command-card">
          <div className="command-row single">
            <button type="button" className="primary" onClick={submit} disabled={!canSubmit}>
              {loading ? "Running..." : "Run autonomous review"}
            </button>
          </div>
          {data?.job_id ? (
            <a className="button-link" href={reportUrl(data.job_id)} target="_blank" rel="noreferrer">
              Download PDF report
            </a>
          ) : null}
          {error ? <p className="error">{error}</p> : null}
        </section>

        <section className="kpi-grid">
          <div className="card">
            <p className="muted">Sources analyzed</p>
            <p className="kpi-value">{sourcesAnalyzed || data?.papers.length || 0}</p>
          </div>
          <div className="card">
            <p className="muted">Processing stage</p>
            <p className="kpi-value">{stage}</p>
          </div>
          <div className="card">
            <p className="muted">Confidence</p>
            <p className="kpi-value">{confidence}</p>
          </div>
        </section>

        <section className="grid">
          <InsightPanel insights={data?.insights} />
          <div className="card">
            <h3>Execution events</h3>
            {!events.length ? (
              <p className="muted">{loading ? "Thinking..." : "No events yet."}</p>
            ) : (
              <ul className="loop-list">
                {events.map((event) => (
                  <li key={event.seq}>
                    <strong>{event.stage}</strong>: {event.message}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <section className="card">
          <GraphView nodes={data?.graph_nodes ?? []} edges={data?.graph_edges ?? []} onSelectNode={setSelectedNode} />
          {selectedNode ? (
            <div className="related-papers">
              <h4>Related papers</h4>
              {relatedPapers.length ? (
                <ul>
                  {relatedPapers.map((paper) => (
                    <li key={paper.id}>
                      <a href={paper.url} target="_blank" rel="noreferrer">
                        {paper.title}
                      </a>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No related papers found for this node.</p>
              )}
            </div>
          ) : null}
        </section>

        <PaperTable papers={data?.papers} />
        <section className="card">
          <h3>Report preview</h3>
          <h4>Abstract</h4>
          <p>{reportPreview.abstract || "Run research to generate a report preview."}</p>
          <h4>Key findings</h4>
          <p>{reportPreview.findings || "No findings yet."}</p>
          <h4>Methodology summary</h4>
          <p>{reportPreview.methods || "No methodology summary yet."}</p>
          {data?.report_markdown ? (
            <button type="button" onClick={() => navigator.clipboard.writeText(data.report_markdown)}>
              Copy text
            </button>
          ) : null}
        </section>
      </main>

      <RightPanel
        data={data}
        loading={loading}
        reportLink={data?.job_id ? reportUrl(data.job_id) : null}
        stage={stage}
        sourcesAnalyzed={sourcesAnalyzed || data?.papers.length || 0}
        confidence={confidence}
      />
    </>
  );
}
