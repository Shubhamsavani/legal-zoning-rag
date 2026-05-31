"""
src/response_formatter.py

Formats final Intelli-Site responses.

Responsibilities:
- Replace SOURCE citations
- Build citation appendix
- Render warnings
"""

import re


# ─────────────────────────────────────────────────────
# BUILD CITATION MAP
# ─────────────────────────────────────────────────────

def build_citation_map(
    retrieved_chunks: list
):

    citation_map = {}

    for chunk in retrieved_chunks:

        citation_id = chunk.get(
            "citation_id"
        )

        title = chunk.get(
            "subsection_title",
            ""
        )

        source_file = chunk.get(
            "source_file",
            ""
        )

        line_range = (

            f"{chunk.get('start_line')}"

            f"-"

            f"{chunk.get('end_line')}"
        )

        citation_map[citation_id] = {

            "title": title,

            "source_file": source_file,

            "line_range": line_range
        }

    return citation_map


# ─────────────────────────────────────────────────────
# REPLACE INLINE CITATIONS
# ─────────────────────────────────────────────────────

def replace_inline_citations(

    answer: str,

    citation_map: dict
):

    formatted = answer

    for cid, meta in citation_map.items():

        replacement = (

            f"[{meta['title']}]"
        )

        formatted = formatted.replace(

            f"[{cid}]",

            replacement
        )

    # ---------------------------------------------
    # CLEAN DUPLICATE CITATION LABELS
    # ---------------------------------------------

    formatted = re.sub(

        r"\[Citation:\s*(.*?)\]",

        r"\1",

        formatted
    )

    return formatted


# ─────────────────────────────────────────────────────
# FORMAT RESPONSE
# ─────────────────────────────────────────────────────

def format_response(

    answer: str,

    retrieved_chunks: list,

    warnings: list
):

    citation_map = build_citation_map(
        retrieved_chunks
    )

    answer = replace_inline_citations(

        answer=answer,

        citation_map=citation_map
    )

    lines = []

    # -------------------------------------------------
    # ANSWER
    # -------------------------------------------------

    lines.append("=" * 80)

    lines.append("FINAL ANSWER")

    lines.append("=" * 80)

    lines.append("")

    lines.append(answer)

    lines.append("")

    # -------------------------------------------------
    # WARNINGS
    # -------------------------------------------------

    if warnings:

        lines.append("=" * 80)

        lines.append("WARNINGS")

        lines.append("=" * 80)

        lines.append("")

        for w in warnings:

            lines.append(f"- {w}")

        lines.append("")

    # -------------------------------------------------
    # SOURCES
    # -------------------------------------------------

    if retrieved_chunks:

        lines.append("=" * 80)

        lines.append("CITATIONS USED")

        lines.append("=" * 80)

        lines.append("")

        seen = set()

        for chunk in retrieved_chunks:

            citation_id = chunk.get(
                "citation_id"
            )

            if citation_id in seen:
                continue

            seen.add(citation_id)

            lines.append(

                f"[{citation_id}] "

                f"{chunk['subsection_title']}"
            )

            lines.append(

                f"  Source: "
                f"{chunk['source_file']}"
            )

            lines.append(

                f"  Lines: "
                f"{chunk['start_line']}"
                f"-"
                f"{chunk['end_line']}"
            )

            lines.append("")

    return "\n".join(lines)