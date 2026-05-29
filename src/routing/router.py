STRUCTURED_KEYWORDS = [

    "flood",
    "fema",
    "e designation",
    "e-designation",
    "hazardous",
    "income",
    "poverty",
    "population",
    "density",
    "renter",
    "year built",
    "building class",
    "census",
    "owner",
    "owns",
    "property",
    "address",
    "borough"
]

PROSE_KEYWORDS = [

    "far",
    "floor area",
    "yard",
    "setback",
    "height",
    "bulk",
    "obstruction",
    "permitted",
    "use",
    "residential",
    "commercial",
    "zoning resolution",
    "section",
    "regulation",
    "allowed",
    "require",
    "must",
    "shall"
]


def route_question(question: str) -> str:

    question_lower = question.lower()

    structured_match = any(
        keyword in question_lower
        for keyword in STRUCTURED_KEYWORDS
    )

    prose_match = any(
        keyword in question_lower
        for keyword in PROSE_KEYWORDS
    )

    # ---------------------------------
    # Both matched
    # ---------------------------------
    if structured_match and prose_match:
        return "hybrid"

    # ---------------------------------
    # Only structured
    # ---------------------------------
    if structured_match:
        return "structured"

    # ---------------------------------
    # Only prose
    # ---------------------------------
    if prose_match:
        return "prose"

    # ---------------------------------
    # Neither matched
    # ---------------------------------
    return "hybrid"


# test this file 
if __name__ == "__main__":

    questions = [

        "Does this site have an E designation?",

        "What FAR is allowed in this district?",

        "What is the flood zone and setback requirement?",

        "Who owns this property?"
    ]

    for q in questions:

        result = route_question(q)

        print(f"\nQuestion: {q}")

        print(f"Route: {result}")