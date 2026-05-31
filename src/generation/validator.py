"""
src/generation/validator.py

Basic response validation layer
for Intelli-Site.
"""

import re

# ─────────────────────────────────────────────────────
# CHECK CITATIONS
# ─────────────────────────────────────────────────────

def contains_citations(
    answer: str
):

    matches = re.findall(

        r'\[SOURCE_\d+\]',

        answer
    )

    return len(matches) > 0

# ─────────────────────────────────────────────────────
# CHECK ABSTENTION
# ─────────────────────────────────────────────────────

def is_abstaining(
    answer: str
):

    patterns = [

        "insufficient information",

        "cannot determine",

        "not enough information",

        "does not contain enough",

        "unable to determine"
    ]

    lower = answer.lower()

    for p in patterns:

        if p in lower:
            return True

    return False

# ─────────────────────────────────────────────────────
# MAIN VALIDATOR
# ─────────────────────────────────────────────────────

def validate_answer(
    answer: str
):

    validation = {

        "has_citations": contains_citations(
            answer
        ),

        "is_abstaining": is_abstaining(
            answer
        ),

        "answer_length": len(answer)
    }

    return validation
