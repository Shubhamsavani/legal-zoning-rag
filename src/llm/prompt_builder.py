from datetime import datetime

from typing import Optional


# =====================================================
# FORMAT RETRIEVED CHUNKS
# =====================================================

def format_retrieved_chunks(

    retrieved_chunks: list
):

    semantic_chunks = []

    dependency_chunks = []

    # =================================================
    # SPLIT BY RETRIEVAL TYPE
    # =================================================

    for chunk in retrieved_chunks:

        retrieval_type = chunk.get(
            "retrieval_type",
            "semantic"
        )

        formatted_chunk = (

            f"{chunk['citation_id']}\n"

            f"Retrieval Type: "
            f"{retrieval_type}\n"

            f"Section ID: "
            f"{chunk['section_id']}\n"

            f"Section Title: "
            f"{chunk['section_title']}\n"

            f"Source File: "
            f"{chunk['source_file']}\n"

            f"Last Amended: "
            f"{chunk['last_amended']}\n"

            f"District Scope: "
            f"{chunk['district_scope']}\n"
            +
            (
                f"Cross References: "
                f"{chunk['cross_refs']}\n"

                if chunk["cross_refs"] != "NONE"

                else ""
            )
            + "\n"
            +
            (
                "WARNING: HISTORICAL / "
                "SUPERSEDED PROVISION\n\n"

                if chunk.get(
                    "is_historical"
                ) == "true"

                else ""
            )
            +
            f"{chunk['text']}"
        )

        if retrieval_type == "dependency":

            dependency_chunks.append(
                formatted_chunk
            )

        else:

            semantic_chunks.append(
                formatted_chunk
            )

    # =================================================
    # BUILD FINAL CONTEXT
    # =================================================

    context_sections = []

    # -------------------------------------------------
    # PRIMARY MATCHES
    # -------------------------------------------------

    if semantic_chunks:

        semantic_block = (

            "=== PRIMARY LEGAL MATCHES ===\n\n"

            +

            "\n\n".join(semantic_chunks)
        )

        context_sections.append(
            semantic_block
        )

    # -------------------------------------------------
    # DEPENDENCY REFERENCES
    # -------------------------------------------------

    if dependency_chunks:

        dependency_block = (

            "=== DEPENDENCY REFERENCES ===\n\n"

            "The following sections were "

            "referenced by the primary "

            "legal matches and may provide "

            "supporting legal context.\n\n"

            +

            "\n\n".join(dependency_chunks)
        )

        context_sections.append(
            dependency_block
        )

    return "\n\n".join(
        context_sections
    )


# =====================================================
# BUILD SYSTEM PROMPT
# =====================================================

def build_system_prompt():

    current_date = datetime.now().strftime(
        "%B %d, %Y"
    )

    return f"""
You are a legal zoning research assistant.

Today's date is {current_date}.

Your job is to answer questions using:
1. Structured site/property data
2. Retrieved zoning resolution context

Grounding Rules:

- Structured site data is the authoritative source for factual property information such as:
  - zoning district
  - FAR
  - flood zone
  - lot area
  - demographics
  - building characteristics
  - year built
  - population density

- Use zoning markdown retrieval ONLY when legal interpretation, zoning rules, restrictions, permitted uses, setbacks, yard regulations, overlays, or regulatory reasoning are required.

- Base your reasoning strictly on the retrieved legal text when legal retrieval is provided.

- Never reference legal section numbers, article names, zoning provisions, or building code provisions unless they explicitly appear in the retrieved context.

- Do not use external legal knowledge or pretrained zoning knowledge beyond the retrieved context.

- If no retrieved legal sections are available, answer ONLY from structured site data and do not invent zoning rules.

- If the retrieved context is insufficient, explicitly state that the corpus does not contain enough information instead of inventing legal provisions.

- Prefer concise, structured, professional explanations over conversational language.
"""


# =====================================================
# BUILD USER PROMPT
# =====================================================

def build_user_prompt(

    user_question: str,

    retrieved_chunks: list,

    vintage_warnings: Optional[list] = None,

    has_retrieval_context: bool = True,

    query_type: str = "LEGAL"
):

    # =================================================
    # FORMAT CONTEXT
    # =================================================

    formatted_context = (
        format_retrieved_chunks(
            retrieved_chunks
        )
    )

    # =================================================
    # WARNINGS
    # =================================================

    warning_block = ""

    if vintage_warnings:

        warning_block = (

            "=== LEGAL / TEMPORAL WARNINGS ===\n\n"

            +

            "\n".join(
                f"- {warning}"
                for warning in vintage_warnings
            )

            +

            "\n\n"
        )

    # =================================================
    # QUERY-TYPE INSTRUCTIONS
    # =================================================

    if query_type == "FACTUAL":

        query_instruction = (

            "This is a FACTUAL query.\n\n"

            "Use ONLY structured site/property "
            "data unless legal retrieval is "
            "explicitly necessary.\n\n"

            "Do not invent zoning regulations "
            "or legal provisions."
        )

    elif query_type == "HYBRID":

        query_instruction = (

            "This is a HYBRID query.\n\n"

            "Use structured site/property "
            "data for factual attributes and "
            "retrieved zoning context for "
            "legal interpretation."
        )

    else:

        query_instruction = (

            "This is a LEGAL query.\n\n"

            "Prioritize retrieved zoning "
            "context and legal applicability."
        )

    # =================================================
    # CITATION POLICY
    # =================================================

    if has_retrieval_context:

        citation_instruction = (

            "Use citation IDs like "
            "[SOURCE_1] when citing "
            "retrieved zoning provisions."
        )

    else:

        citation_instruction = (

            "Do not generate legal citations "
            "if no retrieved zoning sections "
            "are provided."
        )

    # =================================================
    # RESPONSE RULES
    # =================================================

    response_rules = """

1. Explain directly applicable zoning rules first.
2. Use dependency references only if relevant.
3. Mention important district limitations or exceptions.
4. Mention if any referenced provision appears historical or superseded.
5. If the context is incomplete, say what additional information may be needed.
6. If a retrieved provision applies to a broader district range (for example "R1 through R10"), you may infer that explicitly included districts within that range are covered unless the retrieved text states otherwise.
7. Do not reject applicability merely because the queried district is not separately named if it is clearly included within a retrieved district range.
8. Prefer reasonable interpretation of explicitly retrieved zoning ranges over overly cautious refusal to answer.
9. Never invent legal citations or section numbers.
10. Never introduce external zoning provisions or building code references.
"""

    # =================================================
    # FINAL USER PROMPT
    # =================================================

    return f"""
{warning_block}

=== QUERY TYPE ===

{query_type}


=== QUERY STRATEGY ===

{query_instruction}


=== USER QUESTION ===

{user_question}


=== RETRIEVED LEGAL CONTEXT ===

{formatted_context}


=== RESPONSE INSTRUCTIONS ===

Provide a grounded answer using the available evidence.

Citation Policy:
- {citation_instruction}

Requirements:

{response_rules}

Now provide the final answer.
"""


# =====================================================
# BUILD FULL PROMPT PAYLOAD
# =====================================================

def build_prompt_payload(

    user_question: str,

    retrieved_chunks: list,

    vintage_warnings: Optional[list] = None,

    has_retrieval_context: bool = True,

    query_type: str = "LEGAL"
):

    system_prompt = build_system_prompt()

    user_prompt = build_user_prompt(

        user_question=
        user_question,

        retrieved_chunks=
        retrieved_chunks,

        vintage_warnings=
        vintage_warnings,

        has_retrieval_context=
        has_retrieval_context,

        query_type=
        query_type
    )

    return {

        "system_prompt":
        system_prompt,

        "user_prompt":
        user_prompt
    }


# =====================================================
# TEST BLOCK
# =====================================================

if __name__ == "__main__":

    fake_chunks = [

        {

            "citation_id":
            "SOURCE_1",

            "retrieval_type":
            "semantic",

            "section_id":
            "23-342",

            "section_title":
            "Rear Yard Requirements",

            "source_file":
            "zr_03_rear_yard_requirements.md",

            "last_amended":
            "5/12/2021",

            "district_scope":
            "R1 through R10",

            "cross_refs":
            "23-341|23-344",

            "text":
            "Rear yard regulations ..."
        }
    ]

    payload = build_prompt_payload(

        user_question=
        "What are rear yard requirements?",

        retrieved_chunks=
        fake_chunks,

        query_type=
        "LEGAL",

        has_retrieval_context=
        True
    )

    print("\n=== SYSTEM PROMPT ===\n")

    print(payload["system_prompt"])

    print("\n=== USER PROMPT ===\n")

    print(payload["user_prompt"])