"""
src/evaluation/temporal_layer.py

Temporal risk and amendment analysis layer
for Intelli-Site.
"""

from datetime import datetime
import re

CURRENT_YEAR = datetime.now().year

# ─────────────────────────────────────────────────────
# PARSE AMENDMENT YEAR
# ─────────────────────────────────────────────────────

def extract_amendment_year(
    last_amended: str
):

    if not last_amended:
        return None

    match = re.search(
        r'(\d{4})',
        str(last_amended)
    )

    if not match:
        return None

    return int(match.group(1))

# ─────────────────────────────────────────────────────
# EXTRACT USED CITATIONS
# ─────────────────────────────────────────────────────

def extract_used_citations(
    answer: str
):

    return set(

        re.findall(
            r'\[SOURCE_\d+\]',
            answer
        )
    )

# ─────────────────────────────────────────────────────
# MAIN TEMPORAL EVALUATOR
# ─────────────────────────────────────────────────────

def evaluate_temporal_risk(

    answer: str,

    retrieved_chunks: list,

    query_year: int = None
):

    warnings = []

    used = extract_used_citations(
        answer
    )

    used_chunks = []

    for chunk in retrieved_chunks:

        cid = f"[{chunk['citation_id']}]"

        if cid in used:

            used_chunks.append(chunk)

    # -------------------------------------------------
    # AGE CHECKS
    # -------------------------------------------------

    for chunk in used_chunks:

        amended = extract_amendment_year(

            chunk.get(
                "last_amended",
                ""
            )
        )

        if not amended:
            continue

        age = CURRENT_YEAR - amended

        # ---------------------------------------------
        # VERY OLD
        # ---------------------------------------------

        if age > 10:

            warnings.append(

                "[DANGER] "
                f"{chunk['section_id']} "
                f"was last amended in "
                f"{amended} "
                f"({age} years old). "
                "Current NYC zoning "
                "amendments may not "
                "be reflected."

            )

        # ---------------------------------------------
        # MODERATELY OLD
        # ---------------------------------------------

        elif age >= 5:

            warnings.append(

                "[WARNING] "
                f"{chunk['section_id']} "
                f"was last amended in "
                f"{amended}. "
                "Verify whether newer "
                "zoning amendments exist."

            )

        # ---------------------------------------------
        # QUERY YEAR MISMATCH
        # ---------------------------------------------

        if query_year:

            if amended > query_year:

                warnings.append(

                    "[WARNING] "
                    f"The retrieved citation "
                    f"({chunk['section_id']}) "
                    f"reflects amendments "
                    f"newer than the "
                    f"requested year "
                    f"({query_year}). "
                    "Historical provisions "
                    "for the requested period "
                    "may not exist in corpus."

                )

    return sorted(list(set(warnings)))