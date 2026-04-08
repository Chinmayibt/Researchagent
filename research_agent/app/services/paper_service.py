from app.services.llm_service import call_llm
from app.agents.roadmap_agent import safe_parse_json as extract_json


def extract_paper(text: str) -> dict:
    prompt = f"""
You are a research paper analyst. Extract structured, deeply specific information from the paper below.

Paper content:
{text[:4000]}

Extract the following fields:

1. title — exact paper title
2. abstract — 3-4 lines summarizing the problem, method, and result
3. methodology — 2-3 sentences describing HOW the method works (specific steps, architecture, pipeline)
4. key_findings — 2-3 concrete results or conclusions from the paper (with numbers/metrics if present)
5. concepts — list of technical concepts WITH their role in the paper

RULES for concepts:
- Each concept must follow this format: "ConceptName — what it does in THIS paper"
- Must be domain-specific (e.g., ANN, NLP, Transformers, GA, BERT, NER)
- Must NOT be generic words like "data", "text", "model", "results"
- Minimum 5 concepts, maximum 12
- Include metrics/evaluation methods used (e.g., F1-score, Precision, Recall)

EXAMPLES of good concepts:
  "Artificial Neural Network (ANN) — predicts IVF live birth probability from patient parameters"
  "Genetic Algorithm (GA) — searches optimal ANN hyperparameters (layers, neurons, learning rate)"
  "F1-score — evaluates prediction balance between precision and recall on IVF dataset"

EXAMPLES of bad concepts (NEVER do this):
  "Machine Learning"        ← too generic, no role stated
  "Data preprocessing"      ← not domain-specific
  "text"                    ← forbidden

OUTPUT — valid JSON only, no markdown, no explanation:
{{
  "title": "...",
  "abstract": "...",
  "methodology": "...",
  "key_findings": "...",
  "concepts": [
    "ConceptName — role in this paper",
    "..."
  ]
}}
"""

    response = call_llm(prompt)
    return extract_json(response)