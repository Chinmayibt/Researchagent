from app.podcast_agent.services.llm_service import call_llm


def generate_plan(context: str) -> str:
    """
    Generate structured podcast plan using Mistral.
    """

    prompt = f"""
You are an expert podcast planner.

Convert the given research content into a clear podcast outline.

STRICT RULES:
- Max 120 words
- No fluff
- Focus on core ideas only
- Output must be structured

FORMAT:
1. Topic Introduction
2. Core Concept 1
3. Core Concept 2
4. Key Mechanism
5. Importance
6. Closing Insight

CONTENT:
{context}
"""

    return call_llm(prompt, model="mistral")