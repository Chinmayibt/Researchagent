import React from "react";
import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";
import { GraphEdge, GraphNode } from "../services/api";

type Props = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onSelectNode?: (nodeId: string) => void;
};

function colorForCluster(cluster: number): string {
  const palette = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#17becf", "#d62728"];
  return palette[cluster % palette.length];
}

export default function GraphView({ nodes, edges, onSelectNode }: Props) {
  if (!nodes.length) {
    return (
      <div className="graph-empty">
        <p className="muted">No graph data yet. Run research to generate a knowledge graph.</p>
      </div>
    );
  }

  const flowNodes = nodes.map((n, i) => ({
    id: n.id,
    data: { label: n.label, summary: `${n.year ?? "n/a"} | score ${n.score.toFixed(2)}` },
    position: { x: (i % 8) * 220, y: Math.floor(i / 8) * 120 },
    style: {
      border: `2px solid ${colorForCluster(n.cluster)}`,
      borderRadius: 12,
      padding: 8,
      width: 200,
      fontSize: 12,
      background: "#ffffff",
    },
    title: `${n.label} — ${n.year ?? "n/a"}`,
  }));
  const flowEdges = edges.map((e, i) => ({
    id: `e-${i}-${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    animated: e.edge_type === "similarity",
  }));

  return (
    <div className="graph-wrap">
      <div className="graph-header">
        <h4>Knowledge Graph</h4>
        <p className="muted">Nodes are clustered by semantic similarity.</p>
      </div>
      <ReactFlow nodes={flowNodes} edges={flowEdges} fitView onNodeClick={(_, node) => onSelectNode?.(node.id)}>
        <Background gap={18} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
