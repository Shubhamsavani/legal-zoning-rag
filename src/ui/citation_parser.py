import re


def extract_citations(response: str):

    pattern = r"\[(.*?)\]"

    matches = re.findall(
        pattern,
        response
    )

    return matches


def split_response_and_citations(
    response: str
):

    pattern = r"(\[.*?\])"

    parts = re.split(
        pattern,
        response
    )

    return parts