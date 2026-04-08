from app.podcast_agent.services.llm_service import call_llm


def review_script(script: str, context: str) -> str:
    """
    Improve script WITHOUT breaking format.
    """

    prompt = f"""
You are a strict podcast editor.

IMPORTANT RULES:
- DO NOT change "Host A" or "Host B"
- DO NOT change format
- ONLY improve clarity and wording
- DO NOT rewrite completely
- DO NOT summarize
- Keep same structure

Fix:
- clarity
- grammar
- repetition

SCRIPT:
{script}

CONTEXT:
{context}
"""

    return call_llm(prompt, model="mistral")