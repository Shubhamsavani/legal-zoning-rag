import json
from pathlib import Path
from datetime import datetime


LOG_DIR = Path("logs")


LOG_DIR.mkdir(
    exist_ok=True
)


def write_log(
    bbl: str,
    question: str,
    retrieved_chunks: list,
    warnings: list,
    response: str
) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{timestamp}_{bbl}.json"
    )

    log_path = LOG_DIR / filename

    log_data = {

        "timestamp": timestamp,

        "bbl": bbl,

        "question": question,

        "warnings": warnings,

        "retrieved_chunks": retrieved_chunks,

        "response": response
    }

    with open(
        log_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            log_data,
            f,
            indent=2,
            ensure_ascii=False
        )

    return str(log_path)

# # test
# if __name__ == "__main__":

#     path = write_log(

#         bbl="4049630075",

#         question="What are rear yard requirements?",

#         retrieved_chunks=[

#             {
#                 "section_title":
#                 "Section 23-34"
#             }
#         ],

#         warnings=[

#             "Section 23-711 missing"
#         ],

#         response="Rear yard depth is 30 feet."
#     )

#     print("\nLog written to:\n")

#     print(path)