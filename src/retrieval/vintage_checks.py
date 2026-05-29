import json
import re
from pathlib import Path


CROSS_REF_PATH = (
    Path("chroma_db")
    / "cross_ref_map.json"
)


SECTION_PATTERN = r"Section\s+(\d{2}-\d{2,3})"


def load_cross_ref_map() -> dict:

    with open(
        CROSS_REF_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    


def detect_missing_cross_refs(
    retrieved_chunks: list
) -> list:

    cross_ref_map = load_cross_ref_map()

    missing_sections = set(
        cross_ref_map.get(
            "referenced_but_missing",
            []
        )
    )

    warnings = []

    for chunk in retrieved_chunks:

        text = chunk["text"]

        matches = re.findall(
            SECTION_PATTERN,
            text
        )

        for match in matches:

            if match in missing_sections:

                warning = (
                    f"Referenced section "
                    f"{match} is NOT present "
                    f"in corpus."
                )

                warnings.append(warning)

    return list(set(warnings))

def detect_superseded_content(
    retrieved_chunks: list
) -> list:

    warnings = []

    for chunk in retrieved_chunks:

        text = chunk["text"].lower()

        if "superseded" in text:

            warnings.append(
                "Retrieved content may be "
                "historical or superseded."
            )

        if "historical reference" in text:

            warnings.append(
                "Retrieved content contains "
                "historical reference material."
            )

        if "does not reflect amendments" in text:

            warnings.append(
                "Retrieved content may not "
                "reflect latest amendments."
            )

    return list(set(warnings))

def generate_vintage_warnings(
    retrieved_chunks: list
) -> list:

    warnings = []

    warnings.extend(
        detect_missing_cross_refs(
            retrieved_chunks
        )
    )

    warnings.extend(
        detect_superseded_content(
            retrieved_chunks
        )
    )

    return list(set(warnings))


# test 
from src.retrieval.retriever import (
    retrieve_chunks
)


if __name__ == "__main__":

    chunks = retrieve_chunks(

        question=(
            "What are rear yard "
            "requirements in R6 districts?"
        ),

        top_k=5,

        threshold=0.55
    )

    warnings = generate_vintage_warnings(
        chunks
    )

    print("\n=== WARNINGS ===\n")

    if not warnings:

        print("No warnings detected.")

    else:

        for warning in warnings:

            print(f"- {warning}")