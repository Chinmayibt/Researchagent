from app.podcast_agent.services.llm_service import call_llm


def generate_script(context: str, plan: str) -> str:
    prompt = f"""You are generating a HIGH-QUALITY 2-person podcast conversation.

STRICT RULES (MUST FOLLOW):
- ONLY output dialogue
- ONLY 2 speakers: Alex and Sam
- Each line MUST start with either:
  Alex:
  Sam:

- DO NOT repeat any previous sentence
- DO NOT include names inside sentences (only at start)
- DO NOT write "Alex: Sam:" or "Sam: Alex:"
- DO NOT include titles, narration, or explanations
- DO NOT copy the same line again

CONVERSATION RULES:
- Alex asks questions (curious, short)
- Sam explains (clear, informative)
- Alternate strictly: Alex → Sam → Alex → Sam
- Each line max 2 sentences

START EXACTLY LIKE THIS:
Alex: Welcome to the podcast! What are we discussing today?

QUALITY:
- Make it natural and engaging
- Explain concepts simply
- Avoid listing paper details like authors or references
- Focus on understanding, not citation dumping

CONTENT TO COVER:
{context}

PLAN:
{plan}

OUTPUT ONLY DIALOGUE.
"""

    return call_llm(prompt, model="llama3")