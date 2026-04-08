from typing import List, Dict, Optional
from app.services.llm_service import call_llm
import json
import re


# =========================================================
# 📄 PAPER NORMALIZER
# Accepts either:
#   - a dict with keys: title, abstract, concepts  (pre-parsed)
#   - a file path string ending in .pdf             (raw PDF)
# =========================================================
def normalize_paper_input(paper) -> Dict:
    """
    Convert any paper input format into {"title": ..., "content": ...}.
    """
    # Already a parsed dict from paper_service
    if isinstance(paper, dict):
        title = paper.get("title", "Unknown Paper")
        abstract = paper.get("abstract") or paper.get("absttract", "")   # typo-tolerant
        concepts = paper.get("concepts", [])

        content_parts = []
        if abstract:
            content_parts.append(f"Abstract:\n{abstract}")
        if concepts:
            content_parts.append("Key Concepts:\n" + "\n".join(f"- {c}" for c in concepts))

        return {"title": title, "content": "\n\n".join(content_parts)}

    # Raw PDF file path string
    if isinstance(paper, str) and paper.endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(paper) as pdf:
                pages = [p.extract_text() for p in pdf.pages[:8] if p.extract_text()]
                full_text = "\n\n".join(pages)[:6000]
            title = _extract_title(full_text) or paper.split("/")[-1].replace(".pdf", "")
            return {"title": title, "content": full_text}
        except ImportError:
            raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF '{paper}': {e}")

    raise ValueError(f"Unsupported paper format: {type(paper)} — {str(paper)[:80]}")


# =========================================================
# 🧠 MAIN FUNCTION
# =========================================================
def generate_roadmap(
    topic: str,
    paper_paths: List,        # list of dicts (pre-parsed) OR pdf path strings
    user_level: str = "beginner"
) -> Dict:
    """
    Main roadmap generation pipeline.
    paper_paths accepts:
      - List of dicts: {"title": ..., "abstract": ..., "concepts": [...]}
      - List of PDF file path strings
      - Mixed
    """
    print("📄 Extracting paper content...")
    papers_content: List[Dict] = []

    for paper in paper_paths:
        try:
            normalized = normalize_paper_input(paper)
            papers_content.append(normalized)
            print(f"  ✅ Loaded: {normalized['title']}")
        except Exception as e:
            print(f"  ⚠️ Skipped: {e}")

    if not papers_content:
        return {"error": "No paper content could be extracted."}

    print("🚀 Generating roadmap...")
    prompt = build_prompt(topic, papers_content, user_level)
    raw_output = call_llm(prompt)
    parsed = safe_parse_json(raw_output)

    if not parsed:
        return {"error": "LLM returned invalid JSON. Raw output: " + raw_output[:300]}

    roadmap = normalize_roadmap(parsed.get("roadmap", []))

    # --- Validations ---
    if not validate_structure(roadmap):
        return {"error": "Invalid roadmap structure from LLM."}

    if not validate_no_repetition(roadmap):
        return {"error": "Repetition detected in roadmap steps."}

    grounded, bad_steps = validate_grounded_to_papers(roadmap, papers_content)
    if not grounded:
        print(f"⚠️ Hallucinated concepts detected in steps: {bad_steps}. Retrying...")

        strict_prompt = build_prompt(topic, papers_content, user_level, strict=True)
        raw_output = call_llm(strict_prompt)
        parsed = safe_parse_json(raw_output)

        if not parsed:
            return {"error": "Retry also returned invalid JSON."}

        roadmap = normalize_roadmap(parsed.get("roadmap", []))

        grounded, bad_steps = validate_grounded_to_papers(roadmap, papers_content)
        if not grounded:
            return {"error": f"Hallucinated steps remain after retry: {bad_steps}"}

    critic_result = critic(roadmap)

    return {
        "roadmap": roadmap,
        "critic": critic_result
    }


# =========================================================
# 🧾 PROMPT BUILDER  (strict, grounded, few-shot)
# =========================================================
def build_prompt(
    topic: str,
    papers_content: List[Dict],
    user_level: str,
    strict: bool = False
) -> str:
    # Build grounded paper blocks — actual content goes in
    paper_blocks = ""
    for i, p in enumerate(papers_content, 1):
        paper_blocks += f"""
---
PAPER {i}: {p['title']}
CONTENT EXCERPT:
{p['content'][:3000]}
---
"""

    strict_addon = """
⚠️ STRICT CORRECTION MODE:
A previous attempt introduced hallucinated topics not found in the papers above.
You MUST only use concepts explicitly mentioned in the CONTENT EXCERPTs above.
If a concept does not appear in those excerpts, DO NOT include it.
""" if strict else ""

    return f"""You are an expert research paper tutor. Your ONLY job is to read the paper excerpts below and generate a LEARNING ROADMAP based solely on the concepts, methods, and topics found IN THOSE PAPERS.

{strict_addon}

═══════════════════════════════════════════
ABSOLUTE RULES — VIOLATING ANY = INVALID OUTPUT
═══════════════════════════════════════════
1. Every step MUST reference a concept explicitly found in the paper excerpts below.
2. DO NOT invent topics. DO NOT add generic CS/ML prerequisites unless they appear in the papers.
3. DO NOT include: "string operations", "regex", "HTML", "CSS", "JavaScript basics", "file I/O" or any unrelated programming topic.
4. Each `concept_from_paper` field MUST quote or paraphrase a phrase from the paper text.
5. Steps must build logically: foundational concepts → methods → advanced applications.
6. No duplicate concepts across steps.
7. Between 4 and 12 steps total.

═══════════════════════════════════════════
TOPIC: {topic}
USER LEVEL: {user_level}
═══════════════════════════════════════════

{paper_blocks}

═══════════════════════════════════════════
FEW-SHOT EXAMPLE (for format only — do NOT copy content)
═══════════════════════════════════════════
If papers were about "Transformer models for protein folding", a valid roadmap step would be:
{{
  "step": 1,
  "paper_title": "Attention Is All You Need",
  "concept_from_paper": "self-attention mechanism over input sequences",
  "reason": "The paper's core contribution is the self-attention layer — understanding it is the prerequisite for all downstream model components.",
  "what_you_learn": "How queries, keys, and values compute attention weights; why this replaces recurrence."
}}

An INVALID step would be:
{{
  "step": 2,
  "paper_title": "...",
  "concept_from_paper": "string tokenization with regex split",   ← FORBIDDEN
  "reason": "...",
  "what_you_learn": "..."
}}

═══════════════════════════════════════════
OUTPUT — return ONLY this JSON, no markdown, no explanation:
═══════════════════════════════════════════
{{
  "roadmap": [
    {{
      "step": 1,
      "paper_title": "exact paper title from above",
      "concept_from_paper": "direct phrase or term from that paper's excerpt",
      "reason": "why this concept must be learned first / at this stage",
      "what_you_learn": "concrete skills or knowledge gained from studying this concept"
    }}
  ]
}}
"""


# =========================================================
# 🏷️ TITLE EXTRACTOR  (simple heuristic from PDF text)
# =========================================================
def _extract_title(text: str) -> Optional[str]:
    """Grab the first non-empty line that looks like a title (< 120 chars)."""
    for line in text.splitlines():
        line = line.strip()
        if 10 < len(line) < 120 and not line.startswith("Abstract"):
            return line
    return None


# =========================================================
# 🧩 SAFE JSON PARSER
# =========================================================
def safe_parse_json(text: str) -> Dict:
    # Strip markdown fences
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*", "", text)

    # Normalize smart quotes
    text = (text
            .replace("\u2018", "'").replace("\u2019", "'")
            .replace("\u201c", '"').replace("\u201d", '"'))

    # Direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass

    # Extract first {...} block
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    print("❌ JSON parsing failed. Raw snippet:\n", text[:400])
    return {}


# =========================================================
# 🧹 NORMALIZATION
# =========================================================
def normalize_roadmap(roadmap: List[Dict]) -> List[Dict]:
    cleaned = []
    for i, step in enumerate(roadmap):
        cleaned.append({
            "step": step.get("step", i + 1),
            "paper_title": step.get("paper_title", "Unknown"),
            "concept_from_paper": step.get("concept_from_paper", ""),
            "reason": step.get("reason", ""),
            "what_you_learn": step.get("what_you_learn", "")
        })
    return cleaned


# =========================================================
# ✅ STRUCTURE VALIDATION
# =========================================================
def validate_structure(roadmap: List[Dict]) -> bool:
    required = {"step", "paper_title", "concept_from_paper", "reason", "what_you_learn"}
    for step in roadmap:
        if not isinstance(step, dict):
            return False
        if not required.issubset(step.keys()):
            print("❌ Missing keys in step:", step.get("step"), set(step.keys()))
            return False
    return True


# =========================================================
# 🔁 NO REPETITION VALIDATION
# =========================================================
def validate_no_repetition(roadmap: List[Dict]) -> bool:
    seen = set()
    for s in roadmap:
        key = s.get("concept_from_paper", "").lower().strip()
        if key and key in seen:
            print("❌ Repeated concept:", key)
            return False
        seen.add(key)
    return True


# =========================================================
# 🎯 GROUNDING VALIDATION  (replaces weak keyword ban)
# =========================================================
HALLUCINATION_PATTERNS = [
    r"\bregex\b", r"\bstring split\b", r"\bhtml\b", r"\bcss\b",
    r"\bjavascript basics\b", r"\bfile i/?o\b", r"\bsocket\b",
    r"\boperating system\b", r"\bcompiler\b", r"\blinked list\b",
    r"\bsorting algorithm\b",
]

def validate_grounded_to_papers(
    roadmap: List[Dict],
    papers_content: List[Dict]
) -> tuple[bool, List[int]]:
    """
    Two checks:
    1. No hallucination patterns.
    2. concept_from_paper must have at least 2 words matching any paper's text.
    """
    all_paper_text = " ".join(p["content"].lower() for p in papers_content)
    bad_steps = []

    for step in roadmap:
        combined = (
            step.get("concept_from_paper", "") + " " +
            step.get("reason", "") + " " +
            step.get("what_you_learn", "")
        ).lower()

        # Check hallucination patterns
        for pattern in HALLUCINATION_PATTERNS:
            if re.search(pattern, combined):
                print(f"❌ Hallucination pattern '{pattern}' in step {step['step']}")
                bad_steps.append(step["step"])
                break

        # Check concept is grounded: at least 3 content words from concept appear in paper
        concept_words = [
            w for w in step.get("concept_from_paper", "").lower().split()
            if len(w) > 3  # skip stopwords
        ]
        matches = sum(1 for w in concept_words if w in all_paper_text)
        if concept_words and matches < max(1, len(concept_words) // 3):
            print(f"⚠️ Step {step['step']} concept not grounded: '{step.get('concept_from_paper')}'")
            bad_steps.append(step["step"])

    bad_steps = list(set(bad_steps))
    return (len(bad_steps) == 0), bad_steps
# =========================================================
# 🔂 DEDUPLICATION
# =========================================================
def deduplicate_by_concept_name(roadmap: List[Dict]) -> List[Dict]:
    seen = set()
    deduped = []
    for step in roadmap:
        base = step.get("concept_from_paper", "").split("—")[0].strip().lower()
        if base and base not in seen:
            seen.add(base)
            deduped.append(step)
    # Re-number steps sequentially
    for i, s in enumerate(deduped, 1):
        s["step"] = i
    return deduped

# =========================================================
# 🧠 CRITIC AGENT
# =========================================================
def critic(roadmap: List[Dict]) -> str:
    if len(roadmap) < 3:
        return "INVALID: Too short (< 3 steps)"
    if len(roadmap) > 15:
        return "INVALID: Too long (> 15 steps)"

    for i in range(1, len(roadmap)):
        if roadmap[i]["step"] <= roadmap[i - 1]["step"]:
            return "INVALID: Steps not ordered sequentially"

    for step in roadmap:
        if not step["reason"] or not step["what_you_learn"] or not step["concept_from_paper"]:
            return f"INVALID: Missing content in step {step['step']}"

    return "VALID"


# =========================================================
# 🧪 DEBUG RUN
# =========================================================
if __name__ == "__main__":
    # Pass actual PDF paths here
    result = generate_roadmap(
        topic="Machine Learning in Healthcare",
        paper_paths=[
            "papers/ivf_ann_ga.pdf",
            "papers/transformer_clinical_nlp.pdf"
        ],
        user_level="beginner"
    )

    print("\n✅ FINAL OUTPUT:\n", json.dumps(result, indent=2))