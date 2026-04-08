export type RunRequest = {
  topic: string;
};

export type Paper = {
  id: string;
  title: string;
  abstract: string;
  year: number | null;
  citation_count: number;
  url: string;
  source: "openalex" | "crossref" | "arxiv";
  authors: string[];
  topics: string[];
  relevance_score: number;
};

export type PipelineEvent = {
  seq: number;
  ts: string;
  stage: string;
  level: "info" | "warn";
  message: string;
  meta?: Record<string, unknown>;
};

export type GraphNode = {
  id: string;
  label: string;
  year: number | null;
  score: number;
  cluster: number;
};

export type GraphEdge = {
  source: string;
  target: string;
  weight: number;
  edge_type: "citation" | "similarity";
};

export type InsightKeyPaper = {
  title: string;
  why_important: string;
  url: string;
};

export type InsightEvidence = {
  paper_id: string;
  title: string;
  url?: string;
};

export type InsightStatement = {
  text: string;
  supporting_papers: InsightEvidence[];
};

export type Insights = {
  trends: string[];
  gaps: string[];
  contradictions: string[];
  methodologies?: string[];
  emerging_approaches?: string[];
  key_papers: InsightKeyPaper[];
  trend_items?: InsightStatement[];
  gap_items?: InsightStatement[];
  contradiction_items?: InsightStatement[];
};

export type RunResearchResponse = {
  topic: string;
  papers: Paper[];
  graph_nodes: GraphNode[];
  graph_edges: GraphEdge[];
  insights: Insights;
  report_markdown: string;
  job_id: string;
};

type CreateJobResponse = {
  job_id: string;
  status: "queued" | "running" | "completed" | "partial_success" | "failed";
};

type JobStatusResponse = {
  job_id: string;
  status: "queued" | "running" | "completed" | "partial_success" | "failed";
  topic: string;
  progress: Record<string, string>;
  errors: string[];
  last_event_seq: number;
};

type PipelineResult = {
  topic: string;
  papers: Paper[];
  insights: Insights;
  graph_nodes: GraphNode[];
  graph_edges: GraphEdge[];
  graph_summary: Record<string, number>;
  report: {
    markdown: string;
    title: string;
    citations: string[];
    asset_refs: string[];
    report_uri?: string | null;
  };
  assets: Array<{
    asset_id: string;
    paper_id: string;
    asset_type: "image" | "table" | "text_chunk";
    page_number: number;
    caption: string;
    storage_uri?: string | null;
    content_text?: string | null;
  }>;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function createResearchJob(payload: RunRequest): Promise<CreateJobResponse> {
  const res = await fetch(`${API_BASE}/v2/research/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to create job: ${await res.text()}`);
  }
  return res.json();
}

async function fetchJobStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/v2/research/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch job status: ${await res.text()}`);
  }
  return res.json();
}

async function fetchJobResults(jobId: string): Promise<PipelineResult> {
  const res = await fetch(`${API_BASE}/v2/research/jobs/${jobId}/results`);
  if (!res.ok) {
    throw new Error(`Failed to fetch job results: ${await res.text()}`);
  }
  return res.json();
}

type RunResearchOptions = {
  onEvent?: (event: PipelineEvent) => void;
  onProgress?: (progress: Record<string, string>) => void;
};

function createEventStream(jobId: string, onEvent?: (event: PipelineEvent) => void) {
  const stream = new EventSource(`${API_BASE}/v2/research/jobs/${jobId}/stream`);
  stream.onmessage = (msg) => {
    try {
      const parsed = JSON.parse(msg.data) as PipelineEvent;
      onEvent?.(parsed);
    } catch {
      // ignore malformed SSE payloads
    }
  };
  return stream;
}

export async function runResearch(payload: RunRequest, opts: RunResearchOptions = {}): Promise<RunResearchResponse> {
  const job = await createResearchJob(payload);
  const stream = createEventStream(job.job_id, opts.onEvent);

  let status: JobStatusResponse | null = null;
  for (let i = 0; i < 240; i++) {
    status = await fetchJobStatus(job.job_id);
    opts.onProgress?.(status.progress ?? {});
    if (status.status === "failed") {
      stream.close();
      throw new Error(status.errors?.join("; ") || "Pipeline failed");
    }
    if (status.status === "completed" || status.status === "partial_success") {
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  if (!status || (status.status !== "completed" && status.status !== "partial_success")) {
    stream.close();
    throw new Error("Timed out waiting for research job");
  }

  const result = await fetchJobResults(job.job_id);
  stream.close();

  return {
    topic: result.topic,
    papers: result.papers,
    graph_nodes: result.graph_nodes ?? [],
    graph_edges: result.graph_edges ?? [],
    insights: result.insights,
    report_markdown: result.report.markdown,
    job_id: job.job_id,
  };
}

export function reportUrl(jobId: string) {
  return `${API_BASE}/research/report/${jobId}.pdf`;
}
