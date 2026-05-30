from pathlib import Path


CORPUS_DIR = Path(
    "corpus/zoning"
)


def load_source_file(
    source_file: str
):

    file_path = (
        CORPUS_DIR
        / source_file
    )

    if not file_path.exists():

        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        lines = f.readlines()

    return lines


def build_highlighted_markdown(

    lines,

    start_line,

    end_line
):

    rendered = []

    for idx, line in enumerate(
        lines,
        start=1
    ):

        clean_line = line.rstrip()

        # ================================
        # Highlight cited lines
        # ================================

        if start_line <= idx <= end_line:

            rendered.append(

                f"> 🔵 "
                f"`{idx:03}` "
                f"{clean_line}"
            )

        else:

            rendered.append(
                f"`{idx:03}` {clean_line}"
            )

    return "\n".join(rendered)
