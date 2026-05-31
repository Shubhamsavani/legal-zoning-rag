"""
src/generation/llm.py

LLM generation layer for Intelli-Site.

Responsibilities:
- Ollama interaction
- prompt submission
- response extraction
- safe generation config
"""

import requests

# ─────────────────────────────────────────────────────
# OLLAMA CONFIG
# ─────────────────────────────────────────────────────

OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)

MODEL_NAME = "llama3"

# ─────────────────────────────────────────────────────
# GENERATION
# ─────────────────────────────────────────────────────

def generate_answer(

    prompt: str,

    model: str = MODEL_NAME,

    temperature: float = 0.1,

    top_p: float = 0.9,

    timeout: int = 300
):

    payload = {

        "model": model,

        "prompt": prompt,

        "stream": False,

        "options": {

            "temperature": temperature,

            "top_p": top_p
        }
    }

    response = requests.post(

        OLLAMA_URL,

        json=payload,

        timeout=timeout
    )

    response.raise_for_status()

    data = response.json()

    answer = data.get(
        "response",
        ""
    ).strip()

    return answer
