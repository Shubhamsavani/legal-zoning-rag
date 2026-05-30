import requests


OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)

MODEL_NAME = "llama3"


# =====================================================
# CLASSIFY QUERY TYPE
# =====================================================

def classify_query(
    question: str
):

    prompt = f"""
You are a query routing classifier for a legal zoning assistant.

Classify the user question into EXACTLY ONE of these categories:

1. FACTUAL
- The answer can be answered entirely from structured property/site data.
- Examples:
  - zoning district
  - FAR
  - lot area
  - flood zone
  - population density
  - building height
  - year built
  - demographics

2. LEGAL
- The answer requires zoning regulations, legal interpretation, restrictions, permitted uses, setbacks, yard rules, overlays, or cross-referenced zoning provisions.

3. HYBRID
- The answer requires BOTH:
  - structured site/property facts
  AND
  - zoning/legal interpretation.

Return ONLY ONE WORD:
FACTUAL
LEGAL
HYBRID

User Question:
{question}
"""

    payload = {

        "model": MODEL_NAME,

        "prompt": prompt,

        "stream": False,

        "options": {

            "temperature": 0.0,

            "num_predict": 10
        }
    }

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        text = result.get(
            "response",
            ""
        ).strip().upper()

        if "FACTUAL" in text:
            return "FACTUAL"

        if "HYBRID" in text:
            return "HYBRID"

        return "LEGAL"

    except Exception:

        # Safe fallback
        return "LEGAL"


# =====================================================
# TEST BLOCK
# =====================================================

if __name__ == "__main__":

    test_questions = [

        "What is the zoning district?",

        "What are the rear yard requirements?",

        "What rear yard rules apply to this R7A property?",

        "What is the population density?"
    ]

    for question in test_questions:

        result = classify_query(
            question
        )

        print("\nQUESTION:\n")

        print(question)

        print("\nCLASSIFICATION:\n")

        print(result)

        print("\n" + "="*50)
