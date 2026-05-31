"""
src/tests/test_citation_pipeline.py

Tests:
- citation evaluator
- citation grounding
- unsupported claim detection
- citation imputation
- response formatting
"""

from pprint import pprint

from src.evaluation.citation_evaluator import (
    evaluate_citations
)

from src.response_formatter import (
    format_response
)

# ─────────────────────────────────────────────────────
# MOCK RETRIEVED CHUNKS
# ─────────────────────────────────────────────────────

retrieved_chunks = [

    {
        "citation_id": "SOURCE_1",

        "source_file":
            "zr_04_permitted_obstructions_rear_yard.md",

        "subsection_title":
            "## Section 23-341: Permitted "
            "Obstructions in Required Rear "
            "Yards or Rear Yard Equivalents",

        "section_id": "23-341",

        "text":
            """
Air conditioning units,
mechanical equipment serving
the principal building,
and emergency generators
are NOT listed as permitted
obstructions in rear yards
under this Section.
"""
    },

    {
        "citation_id": "SOURCE_2",

        "source_file":
            "zr_08_permitted_obstructions_all_yards.md",

        "subsection_title":
            "## Section 23-311: Permitted "
            "Obstructions in All Yards, "
            "Courts and Open Areas",

        "section_id": "23-311",

        "text":
            """
Heating, ventilation and
air conditioning equipment
may extend not more than
2 feet into a rear yard.
"""
    }
]

# ─────────────────────────────────────────────────────
# TEST CASES
# ─────────────────────────────────────────────────────

TEST_CASES = [

    # -------------------------------------------------
    # GOOD CITED ANSWER
    # -------------------------------------------------

    {
        "name": "Properly grounded answer",

        "answer":
            """
HVAC equipment may extend
up to 2 feet into a rear yard
under certain conditions.

[SOURCE_2]
"""
    },

    # -------------------------------------------------
    # UNSUPPORTED CLAIM
    # -------------------------------------------------

    {
        "name": "Unsupported legal reasoning",

        "answer":
            """
HVAC equipment is automatically
allowed through a variance process.

[SOURCE_1]
"""
    },

    # -------------------------------------------------
    # INVALID CITATION
    # -------------------------------------------------

    {
        "name": "Invalid citation reference",

        "answer":
            """
Rear yard encroachments
are permitted.

[SOURCE_99]
"""
    },

    # -------------------------------------------------
    # ABSTENTION
    # -------------------------------------------------

    {
        "name": "Safe abstention",

        "answer":
            """
Insufficient information
to determine whether
the site qualifies for
special landmark transfer rights.
"""
    }
]

# ─────────────────────────────────────────────────────
# RUN TESTS
# ─────────────────────────────────────────────────────

for idx, test in enumerate(

    TEST_CASES,

    start=1
):

    print("\n" + "=" * 100)

    print(f"TEST {idx}")

    print("=" * 100)

    print("\nNAME:\n")

    print(test["name"])

    print("\nRAW ANSWER:\n")

    print(test["answer"])

    # -------------------------------------------------
    # EVALUATION
    # -------------------------------------------------

    evaluation = evaluate_citations(

        answer=test["answer"],

        retrieved_chunks=retrieved_chunks
    )

    print("\nEVALUATION:\n")

    pprint(evaluation)

    # -------------------------------------------------
    # FORMATTING
    # -------------------------------------------------

    formatted = format_response(

        answer=test["answer"],

        retrieved_chunks=retrieved_chunks,

        warnings=[]
    )

    print("\nFORMATTED RESPONSE:\n")

    print(formatted)

    print("\n")
