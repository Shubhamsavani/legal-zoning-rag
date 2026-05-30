def route_question(
    question: str,
    site: dict = None
) -> str:

    """
    Routing has been removed.

    System now always uses:
    - structured site lookup
    - vector zoning retrieval

    This function is kept only for
    backwards compatibility.
    """

    return "hybrid"

