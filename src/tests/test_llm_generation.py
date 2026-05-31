"""
src/tests/test_llm_generation.py

Smoke test for Intelli-Site LLM generation layer.
"""

from pprint import pprint

from src.generation.llm import (
    generate_answer
)

from src.generation.validator import (
    validate_answer
)

# ─────────────────────────────────────────────────────
# TEST PROMPTS
# ─────────────────────────────────────────────────────

TEST_PROMPTS = [

    # -------------------------------------------------
    # FACTUAL
    # -------------------------------------------------

    {
        "name": "Structured factual query",

        "prompt": """
The property is located in zoning district R7A.

Question:
What is the zoning district?

Answer briefly.
"""
    },

    # -------------------------------------------------
    # LEGAL WITH CITATIONS
    # -------------------------------------------------

    {
        "name": "Legal zoning query",

        "prompt": """
You are a zoning assistant.

Question:
Can HVAC equipment project into a rear yard?

Legal Context:

[SOURCE_1]

Section 23-44 states that
certain permitted obstructions
may project into required yards,
including HVAC equipment
under specified conditions.

Instructions:
- Use citations
- Answer conservatively
"""
    },

    # -------------------------------------------------
    # INSUFFICIENT CONTEXT
    # -------------------------------------------------

    {
        "name": "Abstention behavior",

        "prompt": """
You are a legal zoning assistant.

Question:
Does this site qualify for landmark transfer rights?

Context:
No relevant landmark information provided.

Instructions:
If information is insufficient,
say so explicitly.
"""
    }
]

# ─────────────────────────────────────────────────────
# RUN TESTS
# ─────────────────────────────────────────────────────

for idx, test in enumerate(

    TEST_PROMPTS,

    start=1
):

    print("\n" + "=" * 100)

    print(f"TEST {idx}")

    print("=" * 100)

    print("\nNAME:\n")

    print(test["name"])

    print("\nPROMPT:\n")

    print(test["prompt"])

    # -------------------------------------------------
    # GENERATION
    # -------------------------------------------------

    answer = generate_answer(
        test["prompt"]
    )

    print("\nANSWER:\n")

    print(answer)

    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------

    validation = validate_answer(
        answer
    )

    print("\nVALIDATION:\n")

    pprint(validation)