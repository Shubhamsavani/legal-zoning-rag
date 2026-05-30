import re


def replace_citation_placeholders(

    response: str,

    retrieved_chunks: list
) -> str:

    # =====================================
    # Build citation lookup table
    # =====================================

    citation_lookup = {}

    for chunk in retrieved_chunks:

        citation_id = chunk.get(
            "citation_id"
        )

        source_file = chunk.get(
            "source_file",
            "unknown"
        )

        section_title = chunk.get(
            "section_title",
            "unknown"
        )

        start_line = chunk.get(
            "start_line",
            "?"
        )

        end_line = chunk.get(
            "end_line",
            "?"
        )

        formatted_citation = (

            f"[{section_title} | "
            f"{source_file} | "
            f"lines {start_line}-{end_line}]"
        )

        citation_lookup[
            citation_id
        ] = formatted_citation

    # =====================================
    # Replace placeholders
    # =====================================

    def replace_match(match):

        citation_id = match.group(1)

        return citation_lookup.get(

            citation_id,

            f"[UNKNOWN_CITATION:{citation_id}]"
        )

    processed_response = re.sub(

        r"\[(SOURCE_\d+)\]",

        replace_match,

        response
    )

    return processed_response


# =====================================
# TEST BLOCK
# =====================================

if __name__ == "__main__":

    fake_response = (

        "Rear yard depth is 30 feet "
        "[SOURCE_1]."
    )

    retrieved_chunks = [

        {

            "citation_id":
            "SOURCE_1",

            "source_file":
            "zr_03_rear_yard_requirements.md",

            "section_title":
            "Section 23-34",

            "start_line":
            2,

            "end_line":
            23
        }
    ]

    processed = replace_citation_placeholders(

        response=fake_response,

        retrieved_chunks=retrieved_chunks
    )

    print(processed)