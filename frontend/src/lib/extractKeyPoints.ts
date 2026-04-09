/** Pull 3–5 readable sentences from an abstract for source cards. */
export function extractKeyPoints(abstract: string): string[] {
  const raw = (abstract || "").replace(/\s+/g, " ").trim();
  if (!raw) return ["No abstract available for this paper."];

  const sentences = raw
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length >= 28 && s.length < 500);

  const seen = new Set<string>();
  const out: string[] = [];
  for (const s of sentences) {
    const key = s.slice(0, 48).toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(/[.!?]$/.test(s) ? s : `${s}.`);
    if (out.length >= 5) break;
  }

  if (out.length === 0) {
    return [raw.length > 240 ? `${raw.slice(0, 237)}…` : raw];
  }
  return out.slice(0, 5);
}
