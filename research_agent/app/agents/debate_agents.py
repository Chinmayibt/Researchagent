from app.services.llm_service import call_llm


def agent_A(paper_text):
    prompt = f"""
    You are Researcher A.

    Based on the following FULL research paper:
    {paper_text}

    Extract:
    - Main claim
    - Methodology
    - Strengths

    Then strongly defend this paper.
    """
    return call_llm(prompt)


def agent_B(paper_text):
    prompt = f"""
    You are Researcher B.

    Based on the following FULL research paper:
    {paper_text}

    Extract:
    - Main claim
    - Methodology
    - Strengths

    Then strongly defend this paper.
    """
    return call_llm(prompt)


def judge_agent(arg_A, arg_B):
    prompt = f"""
    You are a neutral research evaluator.

    Argument A:
    {arg_A}

    Argument B:
    {arg_B}

    Compare based on:
    - Dataset realism
    - Method validity
    - Practical applicability

    Give:
    - Winner
    - Reason
    - Confidence (low/medium/high)
    """
    return call_llm(prompt)


def critic_agent(verdict):
    prompt = f"""
    You are a strict critic.

    Evaluate this verdict:
    {verdict}

    Is the reasoning strong and justified?

    Answer:
    - VALID
    - WEAK (with reason)
    """
    return call_llm(prompt)


def run_debate(text_A, text_B):
    # Round 1
    arg_A = agent_A(text_A)
    arg_B = agent_B(text_B)

    # Round 2
    rebuttal_A = call_llm(f"""
    You are Agent A.

    Your argument:
    {arg_A}

    Opponent:
    {arg_B}

    Strengthen and counter.
    """)

    rebuttal_B = call_llm(f"""
    You are Agent B.

    Your argument:
    {arg_B}

    Opponent:
    {arg_A}

    Strengthen and counter.
    """)

    # Judge
    verdict = judge_agent(
        arg_A + "\n" + rebuttal_A,
        arg_B + "\n" + rebuttal_B
    )

    # Critic
    review = critic_agent(verdict)

    # 🔁 NEW: SELF-CORRECTION LOOP
    if "WEAK" in review.upper():
        verdict = call_llm(f"""
        Your previous verdict was weak.

        Improve it using:
        - clearer comparison
        - stronger justification
        - objective reasoning

        Previous verdict:
        {verdict}
        """)

        review = critic_agent(verdict)

    return {
        "round_1": {"A": arg_A, "B": arg_B},
        "round_2": {"A_rebuttal": rebuttal_A, "B_rebuttal": rebuttal_B},
        "final_verdict": verdict,
        "critic": review
    }