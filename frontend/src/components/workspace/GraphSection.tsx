import React, { useCallback, useEffect, useMemo, useState } from "react";
import GraphView from "../GraphView";
import { buildResearchMapGraph, starPaperIdsFromInsights } from "../../lib/buildResearchMapGraph";
import {
  clusterLabelsFromGraph,
  clusterThemeColors,
  trendingClusterId,
} from "../../lib/graphClusterMeta";
import type { GraphEdge, GraphNode, Insights, Paper } from "../../services/api";

const CURRENT_YEAR = new Date().getFullYear();

function abstractSnippet(text: string, maxLen = 360): string {
  const t = (text || "").replace(/\s+/g, " ").trim();
  if (t.length <= maxLen) return t;
  return `${t.slice(0, maxLen - 1)}…`;
}

type Props = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  papers: Paper[];
  insights?: Insights;
  selectedNode: string | null;
  onSelectNode: (id: string | null) => void;
};

export default function GraphSection({ nodes, edges, papers, insights, selectedNode, onSelectNode }: Props) {
  const [expandedClusters, setExpandedClusters] = useState<Set<number>>(() => new Set());
  const [showAllEdges, setShowAllEdges] = useState(false);
  const [graphSearch, setGraphSearch] = useState("");
  const [minYear, setMinYear] = useState<number | "">("");
  const [maxYear, setMaxYear] = useState<number | "">("");
  const [minCitations, setMinCitations] = useState(0);
  const [minRelevance, setMinRelevance] = useState(0);
  const [topicFilter, setTopicFilter] = useState("");
  const [playOn, setPlayOn] = useState(false);
  const [playIndex, setPlayIndex] = useState(0);
  const [fitSignal, setFitSignal] = useState(0);

  const topicOptions = useMemo(() => {
    const s = new Set<string>();
    for (const p of papers) {
      for (const t of p.topics ?? []) {
        const k = t.trim();
        if (k) s.add(k);
      }
    }
    return [...s].sort((a, b) => a.localeCompare(b));
  }, [papers]);

  const filteredPapers = useMemo(() => {
    return papers.filter((p) => {
      if (minYear !== "" && (p.year ?? 0) < minYear) return false;
      if (maxYear !== "" && (p.year ?? CURRENT_YEAR + 1) > maxYear) return false;
      if (p.citation_count < minCitations) return false;
      if (p.relevance_score < minRelevance) return false;
      if (topicFilter.trim()) {
        const q = topicFilter.toLowerCase();
        if (!p.topics.some((x) => x.toLowerCase().includes(q))) return false;
      }
      return true;
    });
  }, [papers, minYear, maxYear, minCitations, minRelevance, topicFilter]);

  const visiblePaperIds = useMemo(() => new Set(filteredPapers.map((p) => p.id)), [filteredPapers]);

  const graphNodesFiltered = useMemo(
    () => nodes.filter((n) => visiblePaperIds.has(n.id)),
    [nodes, visiblePaperIds]
  );
  const graphEdgesFiltered = useMemo(
    () =>
      edges.filter((e) => visiblePaperIds.has(e.source) && visiblePaperIds.has(e.target)),
    [edges, visiblePaperIds]
  );

  useEffect(() => {
    setExpandedClusters((prev) => {
      const clustersPresent = new Set(graphNodesFiltered.map((n) => n.cluster));
      const next = new Set<number>();
      for (const c of prev) {
        if (clustersPresent.has(c)) next.add(c);
      }
      return next;
    });
  }, [graphNodesFiltered]);

  const clusterLabels = useMemo(
    () => clusterLabelsFromGraph(graphNodesFiltered, filteredPapers),
    [graphNodesFiltered, filteredPapers]
  );
  const clusterColors = useMemo(() => clusterThemeColors(clusterLabels), [clusterLabels]);
  const trendingId = useMemo(() => trendingClusterId(graphNodesFiltered), [graphNodesFiltered]);
  const startHereLabel = trendingId !== null ? (clusterLabels.get(trendingId) ?? null) : null;

  const starPaperIds = useMemo(() => {
    const s = starPaperIdsFromInsights(filteredPapers, insights);
    const sorted = [...filteredPapers].sort(
      (a, b) => b.relevance_score - a.relevance_score || b.citation_count - a.citation_count
    );
    for (const p of sorted.slice(0, 3)) s.add(p.id);
    return s;
  }, [filteredPapers, insights]);

  const keyPaperIdSet = useMemo(() => {
    const s = new Set<string>();
    if (!insights?.key_papers?.length) return s;
    for (const kp of insights.key_papers) {
      if (kp.paper_id && visiblePaperIds.has(kp.paper_id)) s.add(kp.paper_id);
      else {
        const p = filteredPapers.find((x) => x.title === kp.title || (kp.url && x.url === kp.url));
        if (p) s.add(p.id);
      }
    }
    return s;
  }, [insights, filteredPapers, visiblePaperIds]);

  const { rfNodes, rfEdges } = useMemo(() => {
    const built = buildResearchMapGraph({
      graphNodes: graphNodesFiltered,
      graphEdges: graphEdgesFiltered,
      papers: filteredPapers,
      expandedClusters,
      showAllEdges,
      clusterLabels,
      clusterColors,
      trendingClusterId: trendingId,
      starPaperIds,
      filterText: graphSearch,
    });
    return { rfNodes: built.nodes, rfEdges: built.edges };
  }, [
    graphNodesFiltered,
    graphEdgesFiltered,
    filteredPapers,
    expandedClusters,
    showAllEdges,
    clusterLabels,
    clusterColors,
    trendingId,
    starPaperIds,
    graphSearch,
  ]);

  const clusterIdList = useMemo(
    () => [...new Set(graphNodesFiltered.map((n) => n.cluster))].sort((a, b) => a - b),
    [graphNodesFiltered]
  );
  const clusterListKey = useMemo(() => clusterIdList.join(","), [clusterIdList]);

  const narrativeLines = useMemo(() => {
    const fromInsights = [...(insights?.trends ?? []), ...(insights?.gaps ?? []).slice(0, 3)];
    return fromInsights.map((x) => x.trim()).filter(Boolean);
  }, [insights]);
  const playNarrative =
    playOn && narrativeLines.length > 0
      ? narrativeLines[playIndex % narrativeLines.length]
      : null;

  useEffect(() => {
    setPlayIndex(0);
  }, [clusterListKey]);

  useEffect(() => {
    if (!playOn || clusterIdList.length === 0) return;
    const id = window.setInterval(() => {
      setPlayIndex((i) => (i + 1) % clusterIdList.length);
    }, 4200);
    return () => window.clearInterval(id);
  }, [playOn, clusterListKey, clusterIdList.length]);

  useEffect(() => {
    if (!playOn || clusterIdList.length === 0) return;
    const cid = clusterIdList[playIndex % clusterIdList.length];
    if (cid === undefined) return;
    setExpandedClusters(new Set([cid]));
    setFitSignal((f) => f + 1);
  }, [playOn, playIndex, clusterListKey, clusterIdList]);

  const onToggleCluster = useCallback((clusterId: number) => {
    setPlayOn(false);
    setExpandedClusters((prev) => {
      const next = new Set(prev);
      if (next.has(clusterId)) next.delete(clusterId);
      else next.add(clusterId);
      return next;
    });
    setFitSignal((f) => f + 1);
  }, []);

  const onSelectPaper = useCallback(
    (paperId: string) => {
      setPlayOn(false);
      onSelectNode(paperId);
    },
    [onSelectNode]
  );

  const selectedPaper = selectedNode ? filteredPapers.find((p) => p.id === selectedNode) : undefined;
  const isKeyPaper = selectedNode ? keyPaperIdSet.has(selectedNode) : false;

  const relatedPapers = useMemo(() => {
    if (!selectedNode) return [];
    const neighbor = new Set<string>([selectedNode]);
    for (const e of graphEdgesFiltered) {
      if (e.source === selectedNode) neighbor.add(e.target);
      if (e.target === selectedNode) neighbor.add(e.source);
    }
    return filteredPapers.filter((p) => neighbor.has(p.id) && p.id !== selectedNode).slice(0, 12);
  }, [selectedNode, graphEdgesFiltered, filteredPapers]);

  const clearThemeOverview = () => {
    setExpandedClusters(new Set());
    setPlayOn(false);
    setFitSignal((f) => f + 1);
  };

  return (
    <section className="card graph-section graph-section--explorer" aria-label="Research map">
      {startHereLabel && expandedClusters.size === 0 ? (
        <p className="graph-start-hint muted">
          Start here: <strong>{startHereLabel}</strong> has the highest average relevance in this view. Click a theme to open papers.
        </p>
      ) : null}

      <div className="graph-toolbar">
        <label className="graph-toolbar__search">
          <span className="sr-only">Focus map by keyword</span>
          <input
            type="search"
            placeholder="Search title, authors, topics…"
            value={graphSearch}
            onChange={(e) => setGraphSearch(e.target.value)}
            aria-label="Focus map by keyword"
          />
        </label>
        <button type="button" className="button-ghost" onClick={clearThemeOverview}>
          Theme overview
        </button>
        <label className="graph-toolbar__toggle">
          <input
            type="checkbox"
            checked={showAllEdges}
            onChange={(e) => setShowAllEdges(e.target.checked)}
          />
          Show all similarity links
        </label>
        <label className="graph-toolbar__toggle">
          <input
            type="checkbox"
            checked={playOn}
            onChange={(e) => {
              const on = e.target.checked;
              setPlayOn(on);
              if (on && clusterIdList.length) {
                setPlayIndex(0);
                setExpandedClusters(new Set([clusterIdList[0]!]));
                setFitSignal((f) => f + 1);
              }
            }}
          />
          Play themes
        </label>
      </div>

      <details className="graph-filters-advanced">
        <summary className="graph-filters-advanced__summary">Corpus filters (year, citations, relevance, topic)</summary>
        <div className="graph-filters-toolbar" role="group" aria-label="Corpus filters">
          <label>
            Min year
            <input
              type="number"
              min={1900}
              max={CURRENT_YEAR + 1}
              value={minYear === "" ? "" : minYear}
              onChange={(e) => setMinYear(e.target.value === "" ? "" : Number(e.target.value))}
              placeholder="any"
            />
          </label>
          <label>
            Max year
            <input
              type="number"
              min={1900}
              max={CURRENT_YEAR + 1}
              value={maxYear === "" ? "" : maxYear}
              onChange={(e) => setMaxYear(e.target.value === "" ? "" : Number(e.target.value))}
              placeholder="any"
            />
          </label>
          <label>
            Min citations
            <input
              type="number"
              min={0}
              value={minCitations}
              onChange={(e) => setMinCitations(Number(e.target.value) || 0)}
            />
          </label>
          <label>
            Min relevance
            <input
              type="number"
              min={0}
              max={1}
              step={0.05}
              value={minRelevance}
              onChange={(e) => setMinRelevance(Math.min(1, Math.max(0, Number(e.target.value) || 0)))}
            />
          </label>
          <label>
            Topic contains
            <select value={topicFilter} onChange={(e) => setTopicFilter(e.target.value)}>
              <option value="">Any</option>
              {topicOptions.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
        </div>
      </details>

      <details className="graph-legend-wrap">
        <summary className="graph-legend-wrap__summary">Map legend</summary>
        <div className="graph-legend" role="note">
          <span>
            <span className="graph-legend__swatch graph-legend__swatch--cite" /> Citation (arrow)
          </span>
          <span>
            <span className="graph-legend__swatch graph-legend__swatch--sim" /> Similarity (thicker = stronger; dashed = weak)
          </span>
          <span>
            <span className="graph-legend__swatch graph-legend__swatch--cluster" /> Themes (colored by inferred keywords — not citation strength)
          </span>
        </div>
      </details>

      {playNarrative ? (
        <p className="graph-play-narrative muted" role="status">
          <strong>Play mode:</strong> {playNarrative}
        </p>
      ) : null}

      <div className="graph-section__split">
        <div className="graph-section__main">
          <div className="graph-wrap graph-wrap--tall">
            <div className="graph-header">
              <div>
                <h4>Research map</h4>
                <p className="muted">
                  Theme-first layout: open a cluster to see papers and within-theme links. Pan and zoom to explore.
                </p>
              </div>
            </div>
            <GraphView
              nodes={rfNodes}
              edges={rfEdges}
              onSelectPaper={onSelectPaper}
              onToggleCluster={onToggleCluster}
              fitViewSignal={fitSignal}
            />
          </div>
        </div>
        <aside className="graph-side-panel" aria-label="Selection detail">
          {selectedNode && !selectedPaper ? (
            <p className="muted">
              This paper is hidden by current filters. Clear filters or pick another node to see details.
            </p>
          ) : null}
          {selectedPaper ? (
            <>
              <h4>Paper detail</h4>
              {isKeyPaper ? <span className="badge badge--key-paper">Key paper (insights)</span> : null}
              <h5 className="graph-side-panel__title">{selectedPaper.title}</h5>
              <p className="graph-side-panel__meta muted">
                {selectedPaper.year ?? "n/a"} · {selectedPaper.citation_count} citations · relevance{" "}
                {selectedPaper.relevance_score.toFixed(2)}
              </p>
              <p className="graph-side-panel__abstract">{abstractSnippet(selectedPaper.abstract)}</p>
              {selectedPaper.url ? (
                <a className="graph-side-panel__link" href={selectedPaper.url} target="_blank" rel="noreferrer">
                  Open source
                </a>
              ) : null}
              <h4 className="graph-side-panel__related-heading">Related papers</h4>
              {relatedPapers.length ? (
                <ul className="graph-side-panel__related">
                  {relatedPapers.map((paper) => (
                    <li key={paper.id}>
                      <button type="button" className="linkish" onClick={() => onSelectNode(paper.id)}>
                        {paper.title}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No neighbors in the filtered graph.</p>
              )}
            </>
          ) : null}
          {!selectedNode ? (
            <p className="muted">
              Click a <strong>theme</strong> to expand papers, then a <strong>paper</strong> for abstract and related work.
            </p>
          ) : null}
        </aside>
      </div>
    </section>
  );
}
