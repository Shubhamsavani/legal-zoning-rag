from pprint import pprint

from src.evaluation.temporal_layer import (
    evaluate_temporal_risk
)

retrieved_chunks = [

    {
        "citation_id": "SOURCE_1",

        "section_id": "23-341",

        "last_amended": "11/10/2022"
    },

    {
        "citation_id": "SOURCE_2",

        "section_id": "12-01",

        "last_amended": "2/2/2011"
    }
]

# -----------------------------------------------------
# TEST ANSWER
# -----------------------------------------------------

answer = """
Rear yard obstructions are governed
by [SOURCE_1] and [SOURCE_2].
"""

warnings = evaluate_temporal_risk(

    answer=answer,

    retrieved_chunks=retrieved_chunks,

    query_year=2015
)

print("\nTEMPORAL WARNINGS:\n")

pprint(warnings)