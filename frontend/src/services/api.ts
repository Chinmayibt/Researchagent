export type RunRequest = {
  topic: string;
  max_papers: number;
  max_iterations: number;
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

export type LoopLog = {
  iteration: number;
  query: string;
  fetched: number;
  accepted: number;
  novelty_ratio: number;
  stop_reason: string | null;
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
  key_papers: InsightKeyPaper[];
  trend_items?: InsightStatement[];
  gap_items?: InsightStatement[];
  contradiction_items?: InsightStatement[];
};

export type RunResearchResponse = {
  topic: string;
  papers: Paper[];
  loop_logs: LoopLog[];
  graph_nodes: GraphNode[];
  graph_edges: GraphEdge[];
  clusters: Record<string, string[]>;
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

export async function runResearch(payload: RunRequest): Promise<RunResearchResponse> {
  const job = await createResearchJob(payload);

  let status: JobStatusResponse | null = null;
  for (let i = 0; i < 240; i++) {
    status = await fetchJobStatus(job.job_id);
    if (status.status === "failed") {
      throw new Error(status.errors?.join("; ") || "Pipeline failed");
    }
    if (status.status === "completed" || status.status === "partial_success") {
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  if (!status || (status.status !== "completed" && status.status !== "partial_success")) {
    throw new Error("Timed out waiting for research job");
  }

  const result = await fetchJobResults(job.job_id);

  return {
    topic: result.topic,
    papers: result.papers,
    loop_logs: [
      {
        iteration: 1,
        query: payload.topic,
        fetched: result.papers.length,
        accepted: result.papers.length,
        novelty_ratio: 1,
        stop_reason: null,
      },
    ],
    graph_nodes: result.graph_nodes ?? [],
    graph_edges: result.graph_edges ?? [],
    clusters: {},
    insights: result.insights,
    report_markdown: result.report.markdown,
    job_id: job.job_id,
  };
}

export function reportUrl(jobId: string) {
  return `${API_BASE}/research/report/${jobId}.pdf`;
}
