import argparse


from src.site.lookup import (
    lookup_site
)

from src.site.formatter import (
    format_site_context
)

from src.retrieval.retriever import (
    retrieve_chunks
)

from src.retrieval.vintage_checks import (
    generate_vintage_warnings
)

from src.llm.prompt_builder import (
    build_prompt_payload
)

from src.llm.ollama_client import (
    generate_response
)

from src.logging_utils.logger import (
    write_log
)

from src.retrieval.citation_postprocessor import (
    replace_citation_placeholders
)

from src.routing.query_classifier import (
    classify_query
)


# =====================================================
# BUILD FINAL MODEL PROMPT
# =====================================================

def assemble_full_prompt(

    system_prompt: str,

    user_prompt: str,

    site_context: str
):

    return f"""
{system_prompt}

=== SITE CONTEXT ===

{site_context}


{user_prompt}
"""


# =====================================================
# CORE PIPELINE FUNCTION
# =====================================================

def run_query_pipeline(

    bbl: str,

    question: str,

    top_k: int = 5,

    threshold: float = 0.80,

    save_logs: bool = True,

    verbose: bool = False
):

    # =====================================
    # QUERY CLASSIFICATION
    # =====================================

    query_type = classify_query(
        question
    )

    if verbose:

        print(
            f"\nQUERY TYPE: "
            f"{query_type}"
        )

    # =====================================
    # SITE LOOKUP
    # =====================================

    if verbose:
        print("\n1. Looking up site data...")

    site = lookup_site(bbl)

    if verbose:
        print("✓ Site lookup complete")

    # =====================================
    # FORMAT SITE CONTEXT
    # =====================================

    if verbose:
        print("\n2. Formatting site context...")

    site_context = format_site_context(
        site
    )

    if verbose:
        print("✓ Site context ready")

    # =====================================
    # CONDITIONAL LEGAL RETRIEVAL
    # =====================================

    retrieved_chunks = []

    if query_type in [

        "LEGAL",

        "HYBRID"
    ]:

        if verbose:
            print("\n3. Retrieving zoning text...")

        retrieved_chunks = retrieve_chunks(

            question=question,

            top_k=top_k,

            threshold=threshold
        )

        if verbose:

            print(
                f"✓ Retrieved "
                f"{len(retrieved_chunks)} chunks"
            )

            print(
                "\nDEBUG RETRIEVED CHUNKS:\n"
            )

            for chunk in retrieved_chunks:

                print(

                    f"- "
                    f"{chunk.get('section_id')} "
                    f"({chunk.get('retrieval_type')})"
                )

    else:

        if verbose:

            print(
                "\n3. Skipping zoning retrieval "
                "(FACTUAL query)"
            )

    # =====================================
    # CHECK RETRIEVAL CONTEXT
    # =====================================

    has_retrieval_context = (
        len(retrieved_chunks) > 0
    )

    # =====================================
    # VINTAGE WARNINGS
    # =====================================

    if verbose:
        print("\n4. Running legal checks...")

    warnings = generate_vintage_warnings(
        retrieved_chunks=retrieved_chunks
    )

    if verbose:

        print(
            f"✓ Generated "
            f"{len(warnings)} warnings"
        )

    # =====================================
    # BUILD PROMPT PAYLOAD
    # =====================================

    if verbose:
        print("\n5. Building prompts...")

    prompt_payload = build_prompt_payload(

        user_question=
        question,

        retrieved_chunks=
        retrieved_chunks,

        vintage_warnings=
        warnings,

        has_retrieval_context=
        has_retrieval_context,

        query_type=
        query_type
    )

    system_prompt = prompt_payload[
        "system_prompt"
    ]

    user_prompt = prompt_payload[
        "user_prompt"
    ]

    full_prompt = assemble_full_prompt(

        system_prompt=
        system_prompt,

        user_prompt=
        user_prompt,

        site_context=
        site_context
    )

    if verbose:
        print("✓ Prompt assembly complete")

    # =====================================
    # GENERATE RESPONSE
    # =====================================

    if verbose:
        print("\n6. Querying Ollama...")

    response = generate_response(
        prompt=full_prompt
    )

    if verbose:
        print("✓ Response generated")

    # =====================================
    # DETERMINISTIC CITATIONS
    # =====================================

    if has_retrieval_context:

        response = replace_citation_placeholders(

            response=response,

            retrieved_chunks=retrieved_chunks
        )

    # =====================================
    # WRITE LOG
    # =====================================

    log_path = None

    if save_logs:

        if verbose:
            print("\n7. Writing log file...")

        log_path = write_log(

            bbl=bbl,

            question=question,

            retrieved_chunks=retrieved_chunks,

            warnings=warnings,

            response=response
        )

        if verbose:
            print(
                f"✓ Log saved: "
                f"{log_path}"
            )

    # =====================================
    # RETURN RESULT
    # =====================================

    return {

        "bbl":
        bbl,

        "question":
        question,

        "query_type":
        query_type,

        "site":
        site,

        "site_context":
        site_context,

        "retrieved_chunks":
        retrieved_chunks,

        "warnings":
        warnings,

        "system_prompt":
        system_prompt,

        "user_prompt":
        user_prompt,

        "full_prompt":
        full_prompt,

        "response":
        response,

        "log_path":
        log_path
    }


# =====================================================
# CLI ENTRYPOINT
# =====================================================

def main():

    parser = argparse.ArgumentParser(

        description=(

            "Intelli-Site "
            "Legal Zoning RAG"
        )
    )

    parser.add_argument(

        "--bbl",

        required=True,

        help="NYC BBL identifier"
    )

    parser.add_argument(

        "--question",

        required=True,

        help="User zoning question"
    )

    parser.add_argument(

        "--top-k",

        type=int,

        default=5,

        help="Number of chunks to retrieve"
    )

    parser.add_argument(

        "--threshold",

        type=float,

        default=0.80,

        help="Similarity threshold"
    )

    parser.add_argument(

        "--no-log",

        action="store_true",

        help="Disable logging"
    )

    args = parser.parse_args()

    # =====================================
    # START PIPELINE
    # =====================================

    print("\n=================================")
    print("INTELLI-SITE QUERY PIPELINE")
    print("=================================\n")

    result = run_query_pipeline(

        bbl=args.bbl,

        question=args.question,

        top_k=args.top_k,

        threshold=args.threshold,

        save_logs=not args.no_log,

        verbose=True
    )

    # =====================================
    # FINAL OUTPUT
    # =====================================

    print("\n=================================")
    print("FINAL RESPONSE")
    print("=================================\n")

    print(result["response"])

    print("\n=================================\n")


# =====================================================
# ENTRYPOINT
# =====================================================

if __name__ == "__main__":

    main()