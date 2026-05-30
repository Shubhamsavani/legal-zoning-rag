import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.query import run_query_pipeline


# =====================================================
# TEST CASES
# =====================================================

TEST_CASES = [

    {
        "case_id": 1,
        "bbl": "4049630075",
        "question": (
            "Does this site have an "
            "E designation and what "
            "does that mean?"
        ),
        "expect_citation": [
            "site_records",
            "zr_09"
        ],
        "expect_abstain": False,
        "expect_vintage_flag": True,
        "label": "E designation — hybrid"
    },

    {
        "case_id": 2,
        "bbl": "1016800019",
        "question": (
            "What is the maximum "
            "floor area ratio for "
            "this site?"
        ),
        "expect_citation": [
            "zr_"
        ],
        "expect_abstain": False,
        "expect_vintage_flag": False,
        "label": "FAR — prose retrieval"
    },

    {
        "case_id": 3,
        "bbl": "2037690057",
        "question": (
            "Is a rear yard required "
            "for this lot, and if so "
            "how deep?"
        ),
        "expect_citation": [
            "zr_"
        ],
        "expect_abstain": False,
        "expect_vintage_flag": False,
        "label": "Rear yard — prose retrieval"
    },

    {
        "case_id": 4,
        "bbl": "3049930009",
        "question": (
            "What is the population "
            "density of the surrounding "
            "census tract?"
        ),
        "expect_citation": [
            "site_records"
        ],
        "expect_abstain": False,
        "expect_vintage_flag": True,
        "label": "Demographics — structured"
    },

    {
        "case_id": 5,
        "bbl": "5004980028",
        "question": (
            "Can I place an air "
            "conditioning unit in "
            "the rear yard?"
        ),
        "expect_citation": [
            "zr_"
        ],
        "expect_abstain": False,
        "expect_vintage_flag": False,
        "label": "Permitted obstruction — prose"
    },

    {
        "case_id": 6,
        "bbl": "1016800019",
        "question": (
            "What was the maximum FAR "
            "for this zoning district "
            "in 2015?"
        ),
        "expect_citation": [],
        "expect_abstain": True,
        "expect_vintage_flag": True,
        "label": "Historical FAR — abstention required"
    },

    {
        "case_id": 7,
        "bbl": "4049630075",
        "question": (
            "What are the specific bulk "
            "regulations for the Special "
            "Flushing Waterfront District?"
        ),
        "expect_citation": [],
        "expect_abstain": True,
        "expect_vintage_flag": False,
        "label": "Cross-ref gap — abstention required"
    },

    {
        "case_id": 8,
        "bbl": "3049930009",
        "question": (
            "What zoning rules apply "
            "when a section references "
            "another section not covered "
            "here?"
        ),
        "expect_citation": [
            "zr_01"
        ],
        "expect_abstain": False,
        "expect_vintage_flag": False,
        "label": "Cross-reference handling — prose"
    }
]


# =====================================================
# HELPERS
# =====================================================

def check_citation_ok(
    expected_citations,
    answer,
    retrieved_sources
):

    if not expected_citations:
        return True

    combined_text = (
        answer.lower()
        + " "
        + " ".join(retrieved_sources).lower()
    )

    for expected in expected_citations:

        if expected.lower() in combined_text:
            return True

    return False


def check_abstain_ok(
    expect_abstain,
    answer
):

    answer_lower = answer.lower()

    abstain_phrases = [

        "corpus does not contain",

        "corpus does not support",

        "cannot be determined",

        "insufficient information",

        "not enough information"
    ]

    found_abstain = any(
        phrase in answer_lower
        for phrase in abstain_phrases
    )

    if expect_abstain:
        return found_abstain

    return not found_abstain


def check_vintage_ok(
    expect_vintage_flag,
    answer
):

    if not expect_vintage_flag:
        return True

    answer_lower = answer.lower()

    vintage_keywords = [

        "2018",

        "historical",

        "superseded",

        "acs 2022",

        "vintage",

        "not exhaustive",

        "verify current status"
    ]

    return any(
        keyword in answer_lower
        for keyword in vintage_keywords
    )


def calculate_score(
    citation_ok,
    abstain_ok,
    vintage_ok
):

    checks = [
        citation_ok,
        abstain_ok,
        vintage_ok
    ]

    failed = sum(
        not c for c in checks
    )

    if failed == 0:
        return "PASS"

    if failed == 1:
        return "PARTIAL"

    return "FAIL"


# =====================================================
# MAIN EVALUATION
# =====================================================

def run_evaluation():

    console = Console()

    results = []

    summary = {
        "pass": 0,
        "partial": 0,
        "fail": 0
    }

    table = Table(
        title="INTELLI-SITE EVALUATION"
    )

    table.add_column("#")
    table.add_column("Label")
    table.add_column("Route")
    table.add_column("Abstained")
    table.add_column("Citation OK")
    table.add_column("Vintage OK")
    table.add_column("Score")

    for case in TEST_CASES:

        print(
            f"\nRunning Case "
            f"{case['case_id']}..."
        )

        pipeline_result = run_query_pipeline(

            bbl=case["bbl"],

            question=case["question"],

            save_logs=False
        )

        answer = pipeline_result[
            "response"
        ]

        route = pipeline_result[
            "route"
        ]

        retrieved_chunks = pipeline_result[
            "retrieved_chunks"
        ]

        retrieved_sources = list(set([

            chunk["source_file"]

            for chunk in retrieved_chunks
        ]))

        abstained = any(

            phrase in answer.lower()

            for phrase in [

                "corpus does not contain",

                "corpus does not support",

                "cannot be determined",

                "insufficient information",

                "not enough information"
            ]
        )

        citation_ok = check_citation_ok(

            case["expect_citation"],

            answer,

            retrieved_sources
        )

        abstain_ok = check_abstain_ok(

            case["expect_abstain"],

            answer
        )

        vintage_ok = check_vintage_ok(

            case["expect_vintage_flag"],

            answer
        )

        score = calculate_score(

            citation_ok,

            abstain_ok,

            vintage_ok
        )

        if score == "PASS":
            summary["pass"] += 1

        elif score == "PARTIAL":
            summary["partial"] += 1

        else:
            summary["fail"] += 1

        result = {

            "case_id":
            case["case_id"],

            "label":
            case["label"],

            "bbl":
            case["bbl"],

            "question":
            case["question"],

            "route":
            route,

            "answer_preview":
            answer[:200],

            "retrieved_sources":
            retrieved_sources,

            "abstained":
            abstained,

            "citation_ok":
            citation_ok,

            "abstain_ok":
            abstain_ok,

            "vintage_ok":
            vintage_ok,

            "score":
            score
        }

        results.append(result)

        table.add_row(

            str(case["case_id"]),

            case["label"],

            route,

            str(abstained),

            str(citation_ok),

            str(vintage_ok),

            score
        )

    # =================================================
    # WRITE JSON
    # =================================================

    logs_dir = Path("logs")

    logs_dir.mkdir(
        exist_ok=True
    )

    output = {

        "run_timestamp":
        datetime.now().isoformat(),

        "cases":
        results,

        "summary":
        summary
    }

    output_path = (
        logs_dir
        / "eval_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            output,

            f,

            indent=2
        )

    # =================================================
    # PRINT SUMMARY
    # =================================================

    console.print(table)

    console.print(
        f"\nPASS: "
        f"{summary['pass']}/8"
    )

    console.print(
        f"PARTIAL: "
        f"{summary['partial']}/8"
    )

    console.print(
        f"FAIL: "
        f"{summary['fail']}/8"
    )

    console.print(
        f"\nSaved results to: "
        f"{output_path}"
    )


# =====================================================
# ENTRYPOINT
# =====================================================

if __name__ == "__main__":

    run_evaluation()