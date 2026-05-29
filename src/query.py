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

    print("1. Looking up site data...")

    site = lookup_site(args.bbl)

    print("✓ Site lookup complete")

    # =====================================
    # ROUTE QUESTION
    # =====================================

    print("\n2. Routing question...")

    route = route_question(
        args.question
    )

    print(f"✓ Route: {route}")

    # =====================================
    # FORMAT SITE CONTEXT
    # =====================================

    print("\n3. Formatting site context...")

    site_context = format_site_context(
        site
    )

    print("✓ Site context ready")

    # =====================================
    # RETRIEVE CHUNKS
    # =====================================

    print("\n4. Retrieving zoning text...")

    retrieved_chunks = retrieve_chunks(

        question=args.question,

        top_k=args.top_k,

        threshold=args.threshold
    )

    print(
        f"✓ Retrieved "
        f"{len(retrieved_chunks)} chunks"
    )

    # =====================================
    # VINTAGE WARNINGS
    # =====================================

    print("\n5. Running vintage checks...")

    warnings = generate_vintage_warnings(
        retrieved_chunks
    )

    print(
        f"✓ Generated "
        f"{len(warnings)} warnings"
    )

    # =====================================
    # BUILD PROMPT
    # =====================================

    print("\n6. Building prompt...")

    prompt = build_prompt(

        question=args.question,

        route=route,

        site_context=site_context,

        retrieved_chunks=retrieved_chunks,

        warnings=warnings
    )

    print("✓ Prompt assembled")

    # =====================================
    # GENERATE RESPONSE
    # =====================================

    print("\n7. Querying Ollama...")

    response = generate_response(
        prompt=prompt
    )

    print("✓ Response generated")

    # =====================================
    # WRITE LOG
    # =====================================

    if not args.no_log:

        print("\n8. Writing log file...")

        log_path = write_log(

            bbl=args.bbl,

            question=args.question,

            route=route,

            retrieved_chunks=retrieved_chunks,

            warnings=warnings,

            response=response
        )

        print(f"✓ Log saved: {log_path}")

    # =====================================
    # FINAL OUTPUT
    # =====================================

    print("\n=================================")
    print("FINAL RESPONSE")
    print("=================================\n")

    print(response)

    print("\n=================================\n")


if __name__ == "__main__":

    main()