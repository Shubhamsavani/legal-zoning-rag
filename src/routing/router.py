import requests


# =====================================================
# OLLAMA CONFIG
# =====================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "llama3"


# =====================================================
# ROUTER PROMPT
# =====================================================

ROUTER_SYSTEM_PROMPT = """

You are a query routing classifier for a legal zoning assistant.

Your task is to classify the user question into EXACTLY ONE category:

structured
prose
hybrid


# CATEGORY DEFINITIONS

structured:
- property records
- flood zones
- ownership
- census data
- environmental designation records
- building metadata
- parcel information
- structured databases
- tabular lookups

Examples:
- Who owns this property?
- What year was this building built?
- Does this lot have an E-designation?


prose:
- zoning regulations
- zoning resolution interpretation
- FAR analysis
- setback rules
- yard requirements
- permitted uses
- legal reasoning over zoning text

Examples:
- What FAR is allowed in R7A?
- What are rear yard requirements?
- Are accessory structures allowed?


hybrid:
- requires BOTH structured data and zoning text interpretation

Examples:
- Does this property have an E-designation and what does it mean?
- What zoning restrictions apply to this parcel?
- What flood zone restrictions affect this property?


# IMPORTANT RULES

Return ONLY ONE WORD:

structured
prose
hybrid

Do not explain.
Do not add punctuation.
Do not output anything else.
"""


# =====================================================
# LLM ROUTER
# =====================================================

def route_question(
    question: str
) -> str:

    prompt = f"""

{ROUTER_SYSTEM_PROMPT}

User Question:
{question}

Classification:
"""

    payload = {

        "model": MODEL_NAME,

        "prompt": prompt,

        "stream": False,

        "options": {

            "temperature": 0,

            "top_p": 0.1,

            "num_predict": 5
        }
    }

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        generated_text = data.get(
            "response",
            ""
        )

        route = (
            generated_text
            .strip()
            .lower()
        )

        # =============================================
        # VALIDATION
        # =============================================

        valid_routes = {

            "structured",
            "prose",
            "hybrid"
        }

        if route not in valid_routes:

            return "hybrid"

        return route

    # =================================================
    # ERROR HANDLING
    # =================================================

    except requests.exceptions.Timeout:

        print(
            "[Router Error] Ollama timeout"
        )

        return "hybrid"

    except requests.exceptions.ConnectionError:

        print(
            "[Router Error] Could not connect to Ollama"
        )

        return "hybrid"

    except requests.exceptions.HTTPError as e:

        print(
            f"[Router Error] HTTP error: {e}"
        )

        return "hybrid"

    except Exception as e:

        print(
            f"[Router Error] Unexpected error: {e}"
        )

        return "hybrid"


# =====================================================
# TEST BLOCK
# =====================================================

if __name__ == "__main__":

    questions = [

        "Does this site have an E designation?",

        "What FAR is allowed in this district?",

        "What is the flood zone and setback requirement?",

        "Who owns this property?",

        "Are mechanical units allowed in rear yards?",

        "What zoning regulations apply to this lot?"
    ]

    for q in questions:

        result = route_question(q)

        print(f"\nQuestion: {q}")

        print(f"Route: {result}")
