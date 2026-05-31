from pprint import pprint

from src.routing.router import (
    route_query
)

TEST_QUERIES = [

    # ---------------------------------------------
    # STRUCTURED
    # ---------------------------------------------

    "What is the zoning district for BBL 4049630075?",

    "What flood zone is this property in?",

    "What is the lot area of this site?",

    # ---------------------------------------------
    # LEGAL RAG
    # ---------------------------------------------

    "Can HVAC equipment project into a rear yard?",

    "What setback regulations apply in R7A?",

    "Does this site require environmental remediation?",

    # ---------------------------------------------
    # REJECT
    # ---------------------------------------------

    "Who won the FIFA world cup?",

    "Write me a Python sorting algorithm",

    "What is the capital of France?"
]

for q in TEST_QUERIES:

    print("\n" + "=" * 80)

    print("QUERY:\n")

    print(q)

    result = route_query(q)

    print("\nROUTER RESULT:\n")

    pprint(result)
