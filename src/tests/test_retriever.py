"""
test/test_retriever.py

Retriever evaluation harness for Intelli-Site.

Evaluates:
- retrieval quality
- dependency expansion
- precision / recall
- abstention retrieval behavior
- retrieval overlap quality
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.retrieval.retriever import retrieve_chunks


console = Console()

# =====================================================
# CONFIG
# =====================================================

TOP_K = 5

THRESHOLD = 0.38

OVERLAP_THRESHOLD = 0.30


# =====================================================
# TEST CASES
# =====================================================

TEST_CASES = [

    {
        "label": "Rear yard depth",
        "question": (
            "For this property, how deep "
            "does the required rear yard "
            "need to be?"
        ),

        "expected_files": [
            "zr_03_rear_yard_requirements.md"
        ]
    },

    {
        "label": "Fence in rear yard",

        "question": (
            "Can I build a fence in the "
            "required rear yard of this site?"
        ),

        "expected_files": [
            "zr_03_rear_yard_requirements.md"
        ]
    },

    {
        "label": "HVAC equipment",

        "question": (
            "Can HVAC equipment project "
            "into the rear yard?"
        ),

        "expected_files": [
            "zr_03_rear_yard_requirements.md"
        ]
    },

    {
        "label": "Residential FAR",

        "question": (
            "What is the maximum residential "
            "FAR allowed for this property?"
        ),

        "expected_files": [
            "zr_04_bulk_and_far.md"
        ]
    },

    {
        "label": "Community facility FAR",

        "question": (
            "If developed as a community "
            "facility, what FAR applies?"
        ),

        "expected_files": [
            "zr_04_bulk_and_far.md"
        ]
    },

    {
        "label": "Street wall requirement",

        "question": (
            "Does this property need "
            "a street wall near the street line?"
        ),

        "expected_files": [
            "zr_10_height_setback_R6_R12.md"
        ]
    },

    {
        "label": "Setback requirement",

        "question": (
            "Would this building require "
            "a setback above base height?"
        ),

        "expected_files": [
            "zr_10_height_setback_R6_R12.md"
        ]
    },

    {
        "label": "Environmental restrictions",

        "question": (
            "Does this site have any "
            "E-designation restrictions?"
        ),

        "expected_files": [
            "zr_09_ceqr_e_designations.md"
        ]
    },

    {
        "label": "Cross reference retrieval",

        "question": (
            "Are there other sections "
            "related to rear yard rules?"
        ),

        "expected_files": [

            "zr_03_rear_yard_requirements.md",

            "zr_01_rules_of_construction.md"
        ]
    },

    {
        "label": "Historical FAR",

        "question": (
            "What was the FAR for this "
            "site in 2015?"
        ),

        "expected_files": []
    },

    {
        "label": "Missing special district",

        "question": (
            "What rules apply if this "
            "property is inside the "
            "Special Hudson Yards District?"
        ),

        "expected_files": []
    },

    {
        "label": "GIS polygon geometry",

        "question": (
            "Can you provide GIS polygon "
            "coordinates for this site?"
        ),

        "expected_files": []
    },
]


# =====================================================
# GLOBAL METRICS
# =====================================================

total_cases = 0

true_positive = 0

false_positive = 0

false_negative = 0

dependency_hits = 0

summary_rows = []


# =====================================================
# OVERLAP FUNCTION
# =====================================================

def compute_overlap(

    expected,

    retrieved
):

    if not expected:

        return 0.0

    expected_set = set(expected)

    retrieved_set = set(retrieved)

    intersection = expected_set.intersection(
        retrieved_set
    )

    return (

        len(intersection)

        / len(expected_set)
    )


# =====================================================
# RUN TESTS
# =====================================================

for idx, case in enumerate(
    TEST_CASES,
    start=1
):

    label = case["label"]

    question = case["question"]

    expected_files = case[
        "expected_files"
    ]

    console.rule(
        f"[bold cyan]TEST {idx}: {label}"
    )

    console.print(

        Panel(

            question,

            title="QUESTION",

            border_style="blue"
        )
    )

    # =================================================
    # RETRIEVE
    # =================================================

    retrieved_chunks, warnings = retrieve_chunks(

        question=question,

        top_k=TOP_K,

        threshold=THRESHOLD
    )

    retrieved_files = list(set(

        chunk.get(
            "source_file",
            ""
        )

        for chunk in retrieved_chunks
    ))

    overlap = compute_overlap(

        expected_files,

        retrieved_files
    )

    # =================================================
    # METRICS
    # =================================================

    total_cases += 1

    dependency_found = False

    for chunk in retrieved_chunks:

        if (

            chunk.get(
                "retrieval_method"
            )

            == "dependency"
        ):

            dependency_hits += 1

            dependency_found = True

    # -------------------------------------------------
    # TRUE POSITIVE
    # -------------------------------------------------

    if overlap >= OVERLAP_THRESHOLD:

        true_positive += 1

        retrieval_status = "GOOD"

    else:

        retrieval_status = "WEAK"

    # -------------------------------------------------
    # FALSE POSITIVE
    # -------------------------------------------------

    extra_files = [

        f for f in retrieved_files

        if f not in expected_files
    ]

    false_positive += len(extra_files)

    # -------------------------------------------------
    # FALSE NEGATIVE
    # -------------------------------------------------

    missing_files = [

        f for f in expected_files

        if f not in retrieved_files
    ]

    false_negative += len(missing_files)

    # =================================================
    # SAVE SUMMARY ROW
    # =================================================

    summary_rows.append({

        "case": label,

        "expected": len(expected_files),

        "retrieved": len(retrieved_files),

        "overlap": overlap,

        "status": retrieval_status
    })

    # =================================================
    # RETRIEVED CHUNK TABLE
    # =================================================

    table = Table(

        title="Retrieved Files",

        box=box.ROUNDED
    )

    table.add_column(
        "File",
        style="cyan"
    )

    table.add_column(
        "Method",
        style="green"
    )

    table.add_column(
        "Section"
    )

    for chunk in retrieved_chunks:

        table.add_row(

            str(
                chunk.get(
                    "source_file",
                    "-"
                )
            ),

            str(
                chunk.get(
                    "retrieval_method",
                    "-"
                )
            ),

            str(
                chunk.get(
                    "section_id",
                    "-"
                )
            )
        )

    console.print(table)

    # =================================================
    # EXPECTED VS RETRIEVED
    # =================================================

    comparison = Table(

        title="Evaluation",

        box=box.MINIMAL_DOUBLE_HEAD
    )

    comparison.add_column(
        "Metric",
        style="yellow"
    )

    comparison.add_column(
        "Value",
        style="green"
    )

    comparison.add_row(
        "Expected Files",
        str(expected_files)
    )

    comparison.add_row(
        "Retrieved Files",
        str(retrieved_files)
    )

    comparison.add_row(
        "Overlap Score",
        f"{overlap:.2f}"
    )

    comparison.add_row(
        "Extra Files",
        str(extra_files)
    )

    comparison.add_row(
        "Missing Files",
        str(missing_files)
    )

    comparison.add_row(
        "Dependency Expansion",
        str(dependency_found)
    )

    comparison.add_row(
        "Warnings",
        str(len(warnings))
    )

    comparison.add_row(
        "Status",
        retrieval_status
    )

    console.print(comparison)

# =====================================================
# FINAL METRICS
# =====================================================

precision = 0

if (

    true_positive + false_positive

) > 0:

    precision = (

        true_positive

        / (

            true_positive
            + false_positive
        )

    ) * 100

recall = 0

if (

    true_positive + false_negative

) > 0:

    recall = (

        true_positive

        / (

            true_positive
            + false_negative
        )

    ) * 100

# =====================================================
# FINAL SUMMARY TABLE
# =====================================================

console.rule(
    "[bold magenta]FINAL RETRIEVAL METRICS"
)

metrics_table = Table(

    title="Retriever Evaluation Metrics",

    box=box.DOUBLE_EDGE
)

metrics_table.add_column(
    "Metric",
    style="cyan"
)

metrics_table.add_column(
    "Value",
    style="green"
)

metrics_table.add_row(
    "Total Test Cases",
    str(total_cases)
)

metrics_table.add_row(
    "True Positives",
    str(true_positive)
)

metrics_table.add_row(
    "False Positives",
    str(false_positive)
)

metrics_table.add_row(
    "False Negatives",
    str(false_negative)
)

metrics_table.add_row(
    "Precision",
    f"{precision:.2f}%"
)

metrics_table.add_row(
    "Recall",
    f"{recall:.2f}%"
)

metrics_table.add_row(
    "Dependency Expansions",
    str(dependency_hits)
)

console.print(metrics_table)

# =====================================================
# PER CASE SUMMARY
# =====================================================

summary_table = Table(

    title="Per Case Summary",

    box=box.ROUNDED
)

summary_table.add_column(
    "Case",
    style="cyan"
)

summary_table.add_column(
    "Expected"
)

summary_table.add_column(
    "Retrieved"
)

summary_table.add_column(
    "Overlap"
)

summary_table.add_column(
    "Status"
)

for row in summary_rows:

    summary_table.add_row(

        row["case"],

        str(row["expected"]),

        str(row["retrieved"]),

        f"{row['overlap']:.2f}",

        row["status"]
    )

console.print(summary_table)

console.rule(
    "[bold green]RETRIEVAL EVALUATION COMPLETE"
)