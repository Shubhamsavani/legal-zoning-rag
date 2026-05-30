import json
import requests

from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.query import run_query_pipeline


# =====================================================
# OLLAMA CONFIG
# =====================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

OLLAMA_MODEL = "llama3"


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

        "evaluation_prompt": """
A strong answer should:

- Correctly identify whether the site has an E designation
- Explain what an E designation means
- Use grounded zoning/site information
- Avoid hallucinations
- Mention uncertainty if information is incomplete
- Reference retrieved zoning/site records naturally

A bad answer:
- Invents zoning rules
- Gives generic unsupported explanations
- Ignores retrieved context
""",

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

        "evaluation_prompt": """
A strong answer should:

- Correctly identify the FAR
- Use retrieved zoning information
- Clearly explain the regulation
- Avoid unsupported assumptions

A bad answer:
- Gives incorrect FAR values
- Hallucinates zoning regulations
- Provides vague generic explanations
""",

        "label": "FAR retrieval"
    },

    {
        "case_id": 3,

        "bbl": "2037690057",

        "question": (
            "Is a rear yard required "
            "for this lot, and if so "
            "how deep?"
        ),

        "evaluation_prompt": """
A strong answer should:

- Correctly determine whether a rear yard is required
- Mention required depth if available
- Stay grounded in zoning text
- Avoid fabricated dimensions

A bad answer:
- Invents requirements
- Gives unsupported dimensions
- Ignores missing information
""",

        "label": "Rear yard retrieval"
    },

    {
        "case_id": 4,

        "bbl": "3049930009",

        "question": (
            "What is the population "
            "density of the surrounding "
            "census tract?"
        ),

        "evaluation_prompt": """
A strong answer should:

- Correctly report demographic information
- Mention if data may be historical/vintage
- Avoid pretending precision if unavailable

A bad answer:
- Invents demographic data
- Ignores data uncertainty
""",

        "label": "Demographics"
    },

    {
        "case_id": 5,

        "bbl": "5004980028",

        "question": (
            "Can I place an air "
            "conditioning unit in "
            "the rear yard?"
        ),

        "evaluation_prompt": """
A strong answer should:

- Correctly identify whether AC units are permitted
- Ground answer in zoning regulations
- Mention conditions or restrictions if present

A bad answer:
- Makes unsupported legal claims
- Gives definitive permissions without evidence
""",

        "label": "Permitted obstruction"
    },

    {
        "case_id": 6,

        "bbl": "1016800019",

        "question": (
            "What was the maximum FAR "
            "for this zoning district "
            "in 2015?"
        ),

        "evaluation_prompt": """
A strong answer should:

- Recognize this is a historical query
- Abstain if historical information is unavailable
- Clearly explain missing corpus support

A bad answer:
- Hallucinates historical FAR values
- Pretends certainty
""",

        "label": "Historical FAR abstention"
    },
    {
        "case_id": 7,

        "bbl": "5004980028",

        "question": (
            "If HVAC equipment is generally "
            "allowed in yards, why might it "
            "still not be permitted in a "
            "required rear yard?"
        ),

        "evaluation_prompt": """
    A strong answer should:

    - Correctly identify that Section 23-311 allows HVAC equipment
    generally in yards

    - Correctly identify that Section 23-341 governs specifically
    permitted rear yard obstructions

    - Explain that HVAC/mechanical equipment is NOT listed as a
    permitted rear yard obstruction under Section 23-341

    - Correctly apply the legal interpretation rule that the
    particular controls the general

    - Mention cross-references between sections

    - Avoid making unsupported legal conclusions

    A bad answer:
    - Claims HVAC equipment is always allowed everywhere
    - Ignores the conflict between Sections 23-311 and 23-341
    - Fails to explain why the more specific rear yard rule controls
    - Hallucinates additional zoning exceptions
    """,

        "label": "Cross-reference conflict resolution"
    },


    {
        "case_id": 8,

        "bbl": "4049630075",

        "question": (
            "Do the rear yard requirements "
            "always apply in Special Purpose "
            "Districts?"
        ),

        "evaluation_prompt": """
    A strong answer should:

    - Correctly identify that Section 23-344 states Special Purpose
    District regulations may supersede standard rear yard rules

    - Explain that alternative requirements may control in Special
    Purpose Districts

    - Clearly state that the corpus does NOT include the actual
    Special Purpose District regulations themselves

    - Partially abstain where appropriate

    - Avoid pretending to know the exact Special District rules

    A bad answer:
    - Invents Special Purpose District regulations
    - Claims rear yard rules always apply universally
    - Fails to acknowledge missing corpus coverage
    - Gives unsupported definitive conclusions
    """,

        "label": "Special district partial abstention"
    }

]


# =====================================================
# SAFE CHUNK EXTRACTION
# =====================================================

def build_retrieved_context(

    retrieved_chunks
):

    retrieved_context_parts = []

    for chunk in retrieved_chunks:

        source = (

            chunk.get("source_file")

            or chunk.get("source")

            or "unknown_source"
        )

        content = (

            chunk.get("chunk_text")

            or chunk.get("text")

            or chunk.get("content")

            or chunk.get("document")

            or chunk.get("chunk")

            or str(chunk)
        )

        retrieved_context_parts.append(

            f"SOURCE: {source}\n"
            f"CONTENT:\n{content}"
        )

    return "\n\n".join(
        retrieved_context_parts
    )


# =====================================================
# OLLAMA CALL
# =====================================================

def call_ollama(

    prompt
):

    payload = {

        "model": OLLAMA_MODEL,

        "prompt": prompt,

        "stream": False,

        "format": "json"
    }

    response = requests.post(

        OLLAMA_URL,

        json=payload
    )

    response.raise_for_status()

    result = response.json()

    return result["response"]


# =====================================================
# LLM JUDGE
# =====================================================

def evaluate_with_llm(

    test_case,
    pipeline_result
):

    answer = pipeline_result["response"]

    route = pipeline_result["route"]

    retrieved_chunks = pipeline_result[
        "retrieved_chunks"
    ]

    warnings = pipeline_result.get(
        "warnings",
        []
    )

    retrieved_context = build_retrieved_context(
        retrieved_chunks
    )

    warnings_text = "\n".join(warnings)

    judge_prompt = f"""
You are an expert evaluator for a legal zoning RAG system.

Your task is to evaluate whether the generated answer is:

- correct
- grounded
- faithful to retrieved context
- non-hallucinatory
- appropriately abstaining when needed
- legally cautious
- complete and useful

==================================================
QUESTION
==================================================

{test_case['question']}

==================================================
EXPECTED BEHAVIOR
==================================================

{test_case['evaluation_prompt']}

==================================================
RETRIEVED CONTEXT
==================================================

{retrieved_context}

==================================================
WARNINGS
==================================================

{warnings_text}

==================================================
GENERATED ANSWER
==================================================

{answer}

==================================================
ROUTE
==================================================

{route}

==================================================
SCORING INSTRUCTIONS
==================================================

Evaluate the answer carefully.

Score from 0 to 10.

Evaluation criteria:

1. Correctness
2. Grounding in retrieved context
3. Hallucination avoidance
4. Completeness
5. Abstention quality
6. Legal caution
7. Clarity

Return ONLY valid JSON.

Format:

{{
    "score": 8,
    "reasoning": "...",
    "strengths": [
        "...",
        "..."
    ],
    "weaknesses": [
        "...",
        "..."
    ]
}}
"""

    try:

        content = call_ollama(
            judge_prompt
        )

        parsed = json.loads(content)

    except Exception as e:

        parsed = {

            "score": 0,

            "reasoning":
            f"Failed evaluation: {str(e)}",

            "strengths": [],

            "weaknesses": [
                "LLM judge failure"
            ]
        }

    return parsed


# =====================================================
# MAIN EVALUATION
# =====================================================

def run_evaluation():

    console = Console()

    table = Table(
        title="LEGAL RAG EVALUATION"
    )

    table.add_column("#")

    table.add_column("Label")

    table.add_column("Route")

    table.add_column("Score")

    table.add_column("Reasoning")

    results = []

    total_score = 0


    for case in TEST_CASES:

        print(
            f"\nRunning Case "
            f"{case['case_id']}..."
        )

        try:

            pipeline_result = run_query_pipeline(

                bbl=case["bbl"],

                question=case["question"],

                save_logs=False,

                verbose=False
            )

            llm_eval = evaluate_with_llm(

                case,
                pipeline_result
            )

            score = llm_eval.get(
                "score",
                0
            )

            total_score += score

            result = {

                "case_id":
                case["case_id"],

                "label":
                case["label"],

                "question":
                case["question"],

                "route":
                pipeline_result["route"],

                "response":
                pipeline_result["response"],

                "retrieved_chunks":
                pipeline_result[
                    "retrieved_chunks"
                ],

                "warnings":
                pipeline_result[
                    "warnings"
                ],

                "llm_evaluation":
                llm_eval
            }

            results.append(result)

            table.add_row(

                str(case["case_id"]),

                case["label"],

                pipeline_result["route"],

                f"{score}/10",

                llm_eval.get(
                    "reasoning",
                    ""
                )[:80]
            )

        except Exception as e:

            table.add_row(

                str(case["case_id"]),

                case["label"],

                "ERROR",

                "0/10",

                str(e)[:80]
            )

            results.append({

                "case_id":
                case["case_id"],

                "label":
                case["label"],

                "error":
                str(e)
            })


    average_score = round(

        total_score / len(TEST_CASES),

        2
    )


    # =================================================
    # SAVE RESULTS
    # =================================================

    logs_dir = Path("logs")

    logs_dir.mkdir(
        exist_ok=True
    )

    output = {

        "timestamp":
        datetime.now().isoformat(),

        "model":
        OLLAMA_MODEL,

        "average_score":
        average_score,

        "results":
        results
    }

    output_path = (

        logs_dir
        / "llm_eval_results.json"
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
    # DISPLAY SUMMARY
    # =================================================

    console.print(table)

    console.print(
        f"\nAverage Score: "
        f"{average_score}/10"
    )

    console.print(
        f"\nSaved results to:"
    )

    console.print(
        str(output_path)
    )


# =====================================================
# ENTRYPOINT
# =====================================================

if __name__ == "__main__":

    run_evaluation()