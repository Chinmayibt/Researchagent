export type ReportSections = {
  abstract: string;
  findings: string;
  methods: string;
};

const ABSTRACT_ALIASES = [
  /^\s*#\s*Abstract\b/im,
  /^\s*##\s*Abstract\b/im,
  /^\s*##\s*Summary\b/im,
  /^\s*##\s*Executive summary\b/im,
];
const FINDINGS_ALIASES = [
  /^\s*##\s*Key findings\b/im,
  /^\s*##\s*Key finding\b/im,
  /^\s*##\s*Main findings\b/im,
  /^\s*##\s*Trends\b/im,
  /^\s*##\s*Findings\b/im,
];
const METHODS_ALIASES = [
  /^\s*##\s*Methodology\b/im,
  /^\s*##\s*Methods\b/im,
  /^\s*##\s*Method\b/im,
  /^\s*##\s*Methods overview\b/im,
];

function sliceAfterHeading(markdown: string, patterns: RegExp[]): string {
  for (const re of patterns) {
    const m = markdown.match(re);
    if (m?.index != null) {
      const start = m.index + m[0].length;
      const tail = markdown.slice(start);
      const next = tail.search(/^\s*##\s+/m);
      const body = next === -1 ? tail : tail.slice(0, next);
      return body.trim();
    }
  }
  return "";
}

/** Extract common sections from review markdown; falls back to first headings or intro snippet. */
export function extractReportSections(markdown: string): ReportSections {
  if (!markdown.trim()) {
    return { abstract: "", findings: "", methods: "" };
  }

  let abstract = "";
  for (const re of ABSTRACT_ALIASES) {
    const m = markdown.match(re);
    if (m?.index != null) {
      const start = m.index + m[0].length;
      const tail = markdown.slice(start);
      const next = tail.search(/^\s*##\s+/m);
      abstract = (next === -1 ? tail : tail.slice(0, next)).trim();
      break;
    }
  }

  let findings = sliceAfterHeading(markdown, FINDINGS_ALIASES);
  let methods = sliceAfterHeading(markdown, METHODS_ALIASES);

  if (!abstract) {
    const h2 = markdown.match(/^##\s+(.+)$/m);
    if (h2) {
      const idx = markdown.indexOf(h2[0]);
      const after = markdown.slice(idx + h2[0].length);
      const next = after.search(/^\s*##\s+/m);
      abstract = (next === -1 ? after : after.slice(0, next)).trim().slice(0, 2000);
    } else {
      abstract = markdown.replace(/^#\s+.+\n+/m, "").trim().slice(0, 500);
    }
  }

  if (!findings || !methods) {
    const blocks: string[] = [];
    const re = /^##\s+(.+)$/gm;
    let m: RegExpExecArray | null;
    const headings: { title: string; start: number; contentStart: number }[] = [];
    while ((m = re.exec(markdown)) !== null) {
      headings.push({ title: m[1].trim(), start: m.index, contentStart: m.index + m[0].length });
    }
    for (let i = 0; i < headings.length; i++) {
      const h = headings[i];
      const end = i + 1 < headings.length ? headings[i + 1].start : markdown.length;
      const body = markdown.slice(h.contentStart, end).trim();
      blocks.push(body);
    }
    if (!findings && blocks[0]) findings = blocks[0];
    if (!methods && blocks[1]) methods = blocks[1];
    if (!findings && blocks.length) findings = blocks.join("\n\n").slice(0, 1500);
  }

  return {
    abstract: abstract.trim(),
    findings: findings.trim(),
    methods: methods.trim(),
  };
}
