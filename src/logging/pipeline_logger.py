"""
src/logging/pipeline_logger.py

Central logging utility for Intelli-Site.
"""

import json
import time

from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────
# LOG DIRECTORY
# ─────────────────────────────────────────────────────

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(
    exist_ok=True
)

LOG_FILE = (
    LOG_DIR / "pipeline_logs.jsonl"
)

# ─────────────────────────────────────────────────────
# MAIN LOGGER
# ─────────────────────────────────────────────────────

def log_pipeline_run(

    question: str,

    bbl: str,

    route_result: dict,

    retrieved_chunks: list,

    warnings: list,

    temporal_warning: str,

    validation: dict,

    final_answer: str,

    runtime_seconds: float
):

    log = {

        # -------------------------------------------------
        # TIMESTAMP
        # -------------------------------------------------

        "timestamp": datetime.utcnow().isoformat(),

        # -------------------------------------------------
        # QUERY
        # -------------------------------------------------

        "question": question,

        "bbl": bbl,

        # -------------------------------------------------
        # ROUTING
        # -------------------------------------------------

        "route": route_result.get(
            "route"
        ),

        "route_confidence": route_result.get(
            "confidence"
        ),

        "query_year": route_result.get(
            "query_year"
        ),

        # -------------------------------------------------
        # RETRIEVAL
        # -------------------------------------------------

        "retrieved_chunk_count": len(
            retrieved_chunks
        ),

        "retrieved_sections": [

            {

                "citation_id": c.get(
                    "citation_id"
                ),

                "section_id": c.get(
                    "section_id"
                ),

                "subsection_title": c.get(
                    "subsection_title"
                ),

                "source_file": c.get(
                    "source_file"
                ),

                "retrieval_method": c.get(
                    "retrieval_method"
                )

            }

            for c in retrieved_chunks
        ],

        # -------------------------------------------------
        # WARNINGS
        # -------------------------------------------------

        "warnings": warnings,

        "temporal_warning": temporal_warning,

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        "validation": validation,

        # -------------------------------------------------
        # ANSWER
        # -------------------------------------------------

        "final_answer": final_answer,

        # -------------------------------------------------
        # PERFORMANCE
        # -------------------------------------------------

        "runtime_seconds": round(
            runtime_seconds,
            3
        )
    }

    with open(

        LOG_FILE,

        "a",

        encoding="utf-8"

    ) as f:

        f.write(
            json.dumps(
                log,
                ensure_ascii=False
            )
            + "\n"
        )

    print(
        f"\n[INFO] Pipeline log written to:\n"
        f"{LOG_FILE}"
    )
