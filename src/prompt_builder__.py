"""
src/prompt_builder.py

Route-aware grounded prompt builder
for Intelli-Site.

Supports:
- structured_only
- legal_rag
"""

from typing import List, Dict

# ─────────────────────────────────────────────────────
# SITE CONTEXT
# ─────────────────────────────────────────────────────

def format_site_context(
    site_summary: Dict
) -> str:

    if not site_summary:

        return (
            "No structured site data available."
        )

    lines = []

    fields = [

        ("BBL", "bbl"),

        ("Address", "address"),

        ("Borough", "borough"),

        ("Zoning District", "zoning_district"),

        ("Special District", "special_district"),

        ("Overlay", "overlay"),

        ("Flood Zone", "flood_zone"),

        ("E Designation", "e_designation"),

        ("E Designation Type", "e_designation_type"),

        ("Lot Area (sqft)", "lot_area_sqft"),

        ("Building Area (sqft)", "building_area_sqft"),

        ("Year Built", "year_built"),
    ]

    for label, key in fields:

        value = site_summary.get(key)

        if value:

            lines.append(
                f"- {label}: {value}"
            )

    notes = site_summary.get("notes")

    if notes:

        lines.append(
            f"- Notes: {notes}"
        )

    return "\n".join(lines)

# ─────────────────────────────────────────────────────
# LEGAL CONTEXT
# ─────────────────────────────────────────────────────

def format_legal_context(
    retrieved_chunks: List[Dict]
) -> str:

    if not retrieved_chunks:

        return (
            "No legal sections retrieved."
        )

    blocks = []

    for chunk in retrieved_chunks:

        citation = chunk.get(
            "citation_id",
            "UNKNOWN"
        )

        section = chunk.get(
            "section_id",
            ""
        )

        subsection = chunk.get(
            "subsection_title",
            ""
        )

        source = chunk.get(
            "source_file",
            ""
        )

        # text = chunk.get(
        #     "text",
        #     ""
        # )

        # to avoid duplication of text - temporary fix - Later fixneeded in chunking and retreival strategy
        text = chunk.get("text", "")

        # -------------------------------------------------
        # LIGHT CLEANING
        # -------------------------------------------------

        lines = []

        seen = set()

        for line in text.splitlines():

            clean = line.strip()

            if not clean:
                continue

            # remove exact duplicates
            if clean in seen:
                continue

            seen.add(clean)

            # remove internal node ids
            if clean.endswith("_body"):
                continue

            lines.append(clean)

        text = "\n".join(lines)


        retrieval_method = chunk.get(
            "retrieval_method",
            ""
        )

        block = f"""
        [{citation}]

        SECTION: {section}

        TITLE:
        {subsection}

        SOURCE FILE:
        {source}

        RETRIEVAL METHOD:
        {retrieval_method}

        LEGAL TEXT:
        {text}
        """

        blocks.append(
            block.strip()
        )

    return "\n\n".join(blocks)

# ─────────────────────────────────────────────────────
# WARNINGS
# ─────────────────────────────────────────────────────

def format_warnings(
    warnings: List[str]
) -> str:

    if not warnings:

        return (
            "No retrieval warnings."
        )

    return "\n".join([
        f"- {w}"
        for w in warnings
    ])

# ─────────────────────────────────────────────────────
# STRUCTURED-ONLY PROMPT
# ─────────────────────────────────────────────────────

def build_structured_prompt(

    question: str,

    site_context: str

):

    return f"""
You are Intelli-Site,
a factual NYC property intelligence assistant.

You MUST follow these rules:

1. Answer ONLY using the provided site data.
2. Do NOT invent missing facts.
3. If information is unavailable,
   explicitly say so.
4. Be concise and factual.
5. Do NOT perform legal interpretation.
6. Do NOT speculate.

==================================================
USER QUESTION
==================================================

{question}

==================================================
STRUCTURED SITE DATA
==================================================

{site_context}

==================================================
TASK
==================================================

Answer the user's question
using ONLY the structured site data.
""".strip()

# ─────────────────────────────────────────────────────
# LEGAL RAG PROMPT
# ─────────────────────────────────────────────────────

def build_legal_prompt(

    question: str,

    site_context: str,

    legal_context: str,

    warning_context: str

):

    return f"""
You are Intelli-Site,
a provenance-aware legal zoning assistant
for NYC zoning analysis.

You MUST follow these rules:

1. Answer ONLY using provided context.
2. Never invent zoning rules.
3. Never fabricate legal conclusions.
4. Cite supporting sections using
   citation IDs like [SOURCE_1].
5. If context is insufficient,
   explicitly abstain.
6. If warnings indicate missing sections,
   acknowledge uncertainty.
7. Distinguish between:
   - site facts
   - zoning regulations
   - assumptions
8. Prefer precise legal language.

==================================================
USER QUESTION
==================================================

{question}

==================================================
STRUCTURED SITE DATA
==================================================

{site_context}

==================================================
RETRIEVED LEGAL CONTEXT
==================================================

{legal_context}

==================================================
RETRIEVAL WARNINGS
==================================================

{warning_context}

==================================================
TASK
==================================================

Provide a grounded zoning/legal analysis.

Use citations wherever possible.

If the corpus does not contain enough
information to answer confidently,
state that explicitly.
""".strip()

# ─────────────────────────────────────────────────────
# MAIN ENTRYPOINT
# ─────────────────────────────────────────────────────

def build_prompt(

    question: str,

    route: str,

    site_summary: Dict,

    retrieved_chunks: List[Dict],

    warnings: List[str]

):

    site_context = format_site_context(
        site_summary
    )

    # -------------------------------------------------
    # STRUCTURED ONLY
    # -------------------------------------------------

    if route == "structured_only":

        return build_structured_prompt(

            question=question,

            site_context=site_context
        )

    # -------------------------------------------------
    # LEGAL RAG
    # -------------------------------------------------

    legal_context = format_legal_context(
        retrieved_chunks
    )

    warning_context = format_warnings(
        warnings
    )

    return build_legal_prompt(

        question=question,

        site_context=site_context,

        legal_context=legal_context,

        warning_context=warning_context
    )
