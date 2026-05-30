import argparse


from src.site.lookup import (
    lookup_site
)

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

from src.llm.prompt_builder import (
    build_prompt
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


# =====================================================
# CORE PIPELINE FUNCTION
# =====================================================

def run_query_pipeline(

    bbl: str,

    question: str,

    top_k: int = 5,

    threshold: float = 0.55,

    save_logs: bool = True,

    verbose: bool = False
):

    # =====================================
    # SITE LOOKUP
    # =====================================

    if verbose:
        print("1. Looking up site data...")

    site = lookup_site(bbl)

    if verbose:
        print("✓ Site lookup complete")

    # =====================================
    # ROUTE QUESTION
    # =====================================

    if verbose:
        print("\n2. Routing question...")

    route = route_question(
        question
    )

    if verbose:
        print(f"✓ Route: {route}")

    # =====================================
    # FORMAT SITE CONTEXT
    # =====================================

    if verbose:
        print("\n3. Formatting site context...")

    site_context = format_site_context(
        site
    )

    if verbose:
        print("✓ Site context ready")

    # =====================================
    # RETRIEVE CHUNKS
    # =====================================

    if verbose:
        print("\n4. Retrieving zoning text...")

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

    # =====================================
    # VINTAGE WARNINGS
    # =====================================

    if verbose:
        print("\n5. Running vintage checks...")

    warnings = generate_vintage_warnings(
        retrieved_chunks
    )

    if verbose:

        print(
            f"✓ Generated "
            f"{len(warnings)} warnings"
        )

    # =====================================
    # BUILD PROMPT
    # =====================================

    if verbose:
        print("\n6. Building prompt...")

    prompt = build_prompt(

        question=question,

        route=route,

        site_context=site_context,

        retrieved_chunks=retrieved_chunks,

        warnings=warnings
    )

    if verbose:
        print("✓ Prompt assembled")

    # =====================================
    # GENERATE RESPONSE
    # =====================================

    if verbose:
        print("\n7. Querying Ollama...")

    response = generate_response(
        prompt=prompt
    )

    if verbose:
        print("✓ Response generated")

    # =====================================
    # DETERMINISTIC CITATIONS
    # =====================================

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
            print("\n8. Writing log file...")

        log_path = write_log(

            bbl=bbl,

            question=question,

            route=route,

            retrieved_chunks=retrieved_chunks,

            warnings=warnings,

            response=response
        )

        if verbose:
            print(f"✓ Log saved: {log_path}")

    # =====================================
    # RETURN STRUCTURED RESULT
    # =====================================

    return {

        "bbl":
        bbl,

        "question":
        question,

        "route":
        route,

        "site":
        site,

        "site_context":
        site_context,

        "retrieved_chunks":
        retrieved_chunks,

        "warnings":
        warnings,

        "prompt":
        prompt,

        "response":
        response,

        "log_path":
        log_path
    }


# =====================================================
# CLI ENTRYPOINT
# =====================================================

def main():

    # =====================================
    # CLI ARGUMENTS
    # =====================================

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

        default=0.55,

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