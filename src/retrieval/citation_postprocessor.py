import re


# =====================================================
# FORMAT SINGLE CITATION
# =====================================================

def format_citation(

    chunk: dict
):

    section_id = chunk.get(
        "section_id",
        "UNKNOWN"
    )

    section_title = chunk.get(
        "section_title",
        "Unknown Section"
    )

    retrieval_type = chunk.get(
        "retrieval_type",
        "semantic"
    )

    # =================================================
    # SHORT RETRIEVAL LABEL
    # =================================================

    if retrieval_type == "dependency":

        retrieval_label = (
            "dependency"
        )

    else:

        retrieval_label = (
            "semantic"
        )

    # =================================================
    # HISTORICAL WARNING
    # =================================================

    historical_warning = ""

    if (
        chunk.get(
            "is_historical"
        )
        ==
        "true"
    ):

        historical_warning = (
            " | historical"
        )

    # =================================================
    # FINAL FORMAT
    # =================================================

    formatted = (

        f"[{section_id}"

        f" — "

        f"{section_title}"

        f" | "

        f"{retrieval_label}"

        f"{historical_warning}]"
    )

    return formatted


# =====================================================
# BUILD CITATION LOOKUP
# =====================================================

def build_citation_lookup(

    retrieved_chunks: list
):

    lookup = {}

    for chunk in retrieved_chunks:

        citation_id = chunk.get(
            "citation_id"
        )

        lookup[citation_id] = (
            format_citation(chunk)
        )

    return lookup


# =====================================================
# REPLACE PLACEHOLDERS
# =====================================================

def replace_citation_placeholders(

    response: str,

    retrieved_chunks: list
):

    citation_lookup = (

        build_citation_lookup(
            retrieved_chunks
        )
    )

    # =================================================
    # REPLACEMENT FUNCTION
    # =================================================

    def replace_match(match):

        citation_id = match.group(1)

        return citation_lookup.get(

            citation_id,

            f"[UNKNOWN_CITATION:{citation_id}]"
        )

    # =================================================
    # REPLACE ALL PLACEHOLDERS
    # =================================================

    processed_response = re.sub(

        r"\[(SOURCE_\d+)\]",

        replace_match,

        response
    )

    return processed_response


# =====================================================
# TEST BLOCK
# =====================================================

if __name__ == "__main__":

    fake_response = (

        "Rear yard depth requirements "

        "apply in R1 through R10 "

        "districts [SOURCE_1]. "

        "Permitted obstructions may "

        "also apply [SOURCE_2]."
    )

    retrieved_chunks = [

        {

            "citation_id":
            "SOURCE_1",

            "section_id":
            "23-342",

            "section_title":
            "Rear Yard Requirements",

            "retrieval_type":
            "semantic",

            "is_historical":
            "false"
        },

        {

            "citation_id":
            "SOURCE_2",

            "section_id":
            "23-341",

            "section_title":
            "Permitted Obstructions",

            "retrieval_type":
            "dependency",

            "is_historical":
            "false"
        }
    ]

    processed = (

        replace_citation_placeholders(

            response=
            fake_response,

            retrieved_chunks=
            retrieved_chunks
        )
    )

    print("\n=== PROCESSED RESPONSE ===\n")

    print(processed)
