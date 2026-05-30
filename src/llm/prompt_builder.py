def build_prompt(
    question: str,
    route: str,
    site_context: str,
    retrieved_chunks: list,
    warnings: list
) -> str:

    prompt_parts = []

    # =================================================
    # SYSTEM INSTRUCTIONS
    # =================================================

    prompt_parts.append(
        "You are an NYC zoning and land-use "
        "analysis assistant."
    )

    prompt_parts.append(
        "Answer ONLY using the provided "
        "site data and retrieved zoning text."
    )

    prompt_parts.append(
        "Do NOT invent regulations, "
        "definitions, zoning permissions, "
        "or legal conclusions."
    )

    prompt_parts.append(
        "Do NOT assume regulations do not "
        "exist merely because relevant "
        "sections were not retrieved."
    )

    prompt_parts.append(
        "Absence of retrieved evidence "
        "is NOT evidence that no regulation "
        "exists."
    )

    prompt_parts.append(
        "If information is missing, "
        "say explicitly that the corpus "
        "does not contain enough information."
    )

    prompt_parts.append(
        "If retrieved sections only discuss "
        "certain zoning districts, do not "
        "generalize those rules to other "
        "district types unless explicitly "
        "stated in the retrieved text."
    )

    prompt_parts.append(
        "If a section explicitly states "
        "applicable zoning districts, "
        "do not apply those regulations "
        "to other district types unless "
        "the retrieved text explicitly "
        "authorizes that extension."
    )

    prompt_parts.append(
        "Do not infer that a regulation "
        "is permitted, prohibited, or "
        "inapplicable unless the retrieved "
        "text explicitly supports that conclusion."
    )
    
    prompt_parts.append(
        "When district applicability is "
        "unclear, state that applicability "
        "cannot be determined from the "
        "retrieved corpus."
    )

    prompt_parts.append(
        "Distinguish clearly between "
        "what the retrieved text states "
        "and what the corpus may simply "
        "not contain."
    )

    prompt_parts.append(
        "Always mention uncertainty when "
        "retrieved documents are historical, "
        "superseded, incomplete, or when "
        "important referenced sections "
        "are missing from the corpus."
    )

    prompt_parts.append(
        "Mention referenced-but-missing "
        "sections when they materially "
        "affect the answer."
    )

    prompt_parts.append(
        "Cite relevant section titles "
        "and section numbers whenever possible."
    )

    prompt_parts.append(
        "When using retrieved evidence "
        "in your answer, cite the "
        "corresponding Citation ID "
        "in square brackets like "
        "[SOURCE_1]."
    )

    prompt_parts.append(
        "Do NOT invent citations, "
        "line numbers, filenames, "
        "or section references."
    )

    prompt_parts.append(
        "Only use Citation IDs that were "
        "explicitly provided in the "
        "retrieved zoning text."
    )

    # =================================================
    # ROUTING MODE
    # =================================================

    prompt_parts.append(
        f"\n=== QUERY TYPE ===\n{route.upper()}"
    )

    # =================================================
    # SITE CONTEXT
    # =================================================

    prompt_parts.append(
        f"\n=== SITE CONTEXT ===\n"
    )

    prompt_parts.append(site_context)

    # =================================================
    # VINTAGE WARNINGS
    # =================================================

    if warnings:

        prompt_parts.append(
            "\n=== IMPORTANT WARNINGS ==="
        )

        for warning in warnings:

            prompt_parts.append(
                f"- {warning}"
            )

    # =================================================
    # RETRIEVED ZONING TEXT
    # =================================================

    prompt_parts.append(
        "\n=== RETRIEVED ZONING TEXT ==="
    )

    for chunk in retrieved_chunks:

        citation_id = chunk.get(
            "citation_id",
            "UNKNOWN_SOURCE"
        )

        source_file = chunk.get(
            "source_file",
            "unknown"
        )

        section_title = chunk.get(
            "section_title",
            "unknown"
        )

        last_amended = chunk.get(
            "last_amended",
            "unknown"
        )

        start_line = chunk.get(
            "start_line",
            "unknown"
        )

        end_line = chunk.get(
            "end_line",
            "unknown"
        )

        distance = chunk.get(
            "distance",
            "unknown"
        )

        text = chunk.get(
            "text",
            ""
        )

        prompt_parts.append(
            f"""
--------------------------------------------------
Citation ID:
{citation_id}

Source File:
{source_file}

Section:
{section_title}

Last Amended:
{last_amended}

Lines:
{start_line}-{end_line}

Similarity Distance:
{distance}

Retrieved Text:
{text}
--------------------------------------------------
"""
        )

    # =================================================
    # USER QUESTION
    # =================================================

    prompt_parts.append(
        "\n=== USER QUESTION ==="
    )

    prompt_parts.append(question)

    # =================================================
    # RESPONSE INSTRUCTIONS
    # =================================================

    prompt_parts.append(
        "\n=== RESPONSE INSTRUCTIONS ==="
    )

    prompt_parts.append(
        "Provide a concise but legally "
        "careful answer."
    )

    prompt_parts.append(
        "Separate factual site data from "
        "zoning interpretation."
    )

    prompt_parts.append(
        "Do not claim certainty where "
        "the corpus is incomplete."
    )

    prompt_parts.append(
        "Mention referenced-but-missing "
        "sections if they materially affect "
        "the answer."
    )

    prompt_parts.append(
        "When making a factual or legal "
        "statement derived from retrieved "
        "text, include the corresponding "
        "Citation ID like [SOURCE_1]."
    )

    prompt_parts.append(
        "Do not use Citation IDs unless "
        "the answer actually relied on "
        "that retrieved text."
    )

    return "\n".join(prompt_parts)


# =================================================
# TEST BLOCK
# =================================================

from src.site.lookup import lookup_site

from src.site.formatter import (
    format_site_context
)

from src.routing.router import (
    route_question
)

from src.retrieval.retriever import (
    retrieve_chunks
)

from src.retrieval.vintage_checks import (
    generate_vintage_warnings
)


if __name__ == "__main__":

    question = (
        "What are the rear yard "
        "requirements for this site?"
    )

    route = route_question(question)

    site = lookup_site(
        "4049630075"
    )

    site_context = format_site_context(
        site
    )

    chunks = retrieve_chunks(
        question=question,
        top_k=5,
        threshold=0.55
    )

    warnings = generate_vintage_warnings(
        chunks
    )

    prompt = build_prompt(
        question=question,
        route=route,
        site_context=site_context,
        retrieved_chunks=chunks,
        warnings=warnings
    )

    print(prompt[:8000])