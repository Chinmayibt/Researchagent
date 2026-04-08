import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def call_llm(prompt: str, model: str = "mistral") -> str:
    """
    Call local Ollama LLM with proper error handling.
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            raise ValueError("Invalid response from LLM")

        output = data["response"].strip()

        if not output:
            raise ValueError("Empty response from LLM")

        return output

    except Exception as e:
        print("\n❌ LLM ERROR:", str(e))
        return "Error: LLM failed"