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
        "Do not infer that a regulation "
        "is permitted, prohibited, or "
        "inapplicable unless the retrieved "
        "text explicitly supports that conclusion."
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
        f"\n{site_context}"
    )

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
    # RETRIEVED LEGAL TEXT
    # =================================================

    prompt_parts.append(
        "\n=== RETRIEVED ZONING TEXT ==="
    )

    for idx, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        similarity = chunk.get(
            "similarity",
            0
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

        text = chunk.get(
            "text",
            ""
        )

        prompt_parts.append(
            f"\n--- CHUNK {idx} ---"
        )

        prompt_parts.append(
            f"Similarity: {similarity}"
        )

        prompt_parts.append(
            f"Source File: {source_file}"
        )

        prompt_parts.append(
            f"Section: {section_title}"
        )

        prompt_parts.append(
            f"Last Amended: {last_amended}"
        )

        prompt_parts.append("\nTEXT:\n")

        prompt_parts.append(text)

    # =================================================
    # USER QUESTION
    # =================================================

    prompt_parts.append(
        "\n=== USER QUESTION ==="
    )

    prompt_parts.append(question)

    # =================================================
    # FINAL INSTRUCTIONS
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

    return "\n".join(prompt_parts)

# test
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

# # test
# if __name__ == "__main__":

#     question = (
#         "What are the rear yard "
#         "requirements for this site?"
#     )

#     route = route_question(question)

#     site = lookup_site(
#         "4049630075"
#     )

#     site_context = format_site_context(
#         site
#     )

#     chunks = retrieve_chunks(
#         question=question,
#         top_k=5,
#         threshold=0.55
#     )

#     warnings = generate_vintage_warnings(
#         chunks
#     )

#     prompt = build_prompt(
#         question=question,
#         route=route,
#         site_context=site_context,
#         retrieved_chunks=chunks,
#         warnings=warnings
#     )

#     print(prompt[:6000])