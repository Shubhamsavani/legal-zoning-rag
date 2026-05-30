
import json
import re

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.query import run_query_pipeline

from src.llm.ollama_client import (
    generate_response
)

console = Console()


# =================================================
# TEST CASES
# =================================================

TEST_CASES = [

    {
        "id": 1,

        "question":
            "Does this site have an E designation and what does that mean?",

        "bbl":
            "4049630075",

        "expected_sections": [

            "zr_09"
        ]
    },

    {
        "id": 2,

        "question":
            "What is the maximum floor area ratio for this site?",

        "bbl":
            "1016800019",

        "expected_sections": [

            "zr_"
        ]
    },

    {
        "id": 3,

        "question":
            "Is a rear yard required for this lot, and if so how deep?",

        "bbl":
            "2037690057",

        "expected_sections": [

            "zr_03"
        ]
    },

    {
        "id": 4,

        "question":
            "What is the population density of the surrounding census tract?",

        "bbl":
            "3049930009",

        "output_data": [

            "36800"
        ]
    },

    {
        "id": 5,

        "question":
            "Can I place an air conditioning unit in the rear yard?",

        "bbl":
            "5004980028",

        "expected_sections": [

            "zr_04"
        ]
    },

    {
        "id": 6,

        "question":
            "What was the maximum FAR for this zoning district in 2015?",

        "bbl":
            "1016800019",

        "output_expectation": [

            "historical_abstention"
        ]
    },

    {
        "id": 7,

        "question":
            "What are the specific bulk regulations for the Special Flushing Waterfront District?",

        "bbl":
            "4049630075",

        "output_expectation": [

            "fw_missing"
        ]
    },

    {
        "id": 8,

        "question":
            "What zoning rules apply when a section references another section not covered here?",

        "bbl":
            "3049930009",

        "expected_sections": [

            "zr_01"
        ]
    }
]


# =================================================
# EXPECTATION PROMPTS
# =================================================

EXPECTATION_PROMPTS = {

    "historical_abstention": """

The answer should clearly state that
historical zoning or FAR data is not
available in the corpus.

PASS if:
- answer abstains correctly
- answer avoids hallucinating historical FAR
- answer explicitly mentions corpus limitation

FAIL if:
- answer invents historical FAR values
- answer pretends historical data exists
""",

    "fw_missing": """

The answer should clearly state that
the corpus does not contain the
specific Special Flushing Waterfront
District bulk regulations.

PASS if:
- answer explicitly mentions corpus gap
- answer avoids inventing FW rules

FAIL if:
- answer hallucinates FW regulations
- answer pretends corpus contains them
"""
}


# =================================================
# RETRIEVAL EVALUATION
# =================================================

def evaluate_retrieval(

    expected_sections,

    retrieved_chunks
):

    retrieved_sources = [

        chunk.get("source_file", "")

        for chunk in retrieved_chunks
    ]

    matched = []

    missing = []

    for expected in expected_sections:

        found = False

        for source in retrieved_sources:

            if expected.lower() in source.lower():

                found = True

                matched.append(expected)

                break

        if not found:

            missing.append(expected)

    retrieval_pass = (
        len(missing) == 0
    )

    return {

        "pass":
            retrieval_pass,

        "matched":
            matched,

        "missing":
            missing,

        "retrieved_sources":
            retrieved_sources
    }


# =================================================
# OUTPUT DATA EVALUATION
# =================================================

def evaluate_output_data(

    expected_data,

    answer
):

    answer_lower = answer.lower()

    matched = []

    missing = []

    for item in expected_data:

        if item.lower() in answer_lower:

            matched.append(item)

        else:

            missing.append(item)

    passed = (
        len(missing) == 0
    )

    return {

        "pass":
            passed,

        "matched":
            matched,

        "missing":
            missing
    }


# =================================================
# LLM EXPECTATION JUDGE
# =================================================

def run_expectation_judge(

    expectation_key,

    question,

    answer
):

    try:

        expectation_prompt = (
            EXPECTATION_PROMPTS[
                expectation_key
            ]
        )

        prompt = f"""
You are evaluating a legal RAG answer.

QUESTION:
{question}

ANSWER:
{answer}

EXPECTATION:
{expectation_prompt}

Return ONLY valid JSON.

{{
  "pass": true,
  "reason": ""
}}
"""

        raw_response = generate_response(

            prompt=prompt,

            temperature=0.0,

            max_tokens=300
        )

        console.print(
            "\n[bold magenta]RAW JUDGE OUTPUT[/bold magenta]"
        )

        console.print(raw_response)

        cleaned = raw_response.strip()

        cleaned = cleaned.replace(
            "```json",
            ""
        )

        cleaned = cleaned.replace(
            "```",
            ""
        )

        match = re.search(

            r"\{.*\}",

            cleaned,

            re.DOTALL
        )

        if not match:

            return {

                "judge_failed": True,

                "pass": False,

                "reason":
                    "No JSON found."
            }

        json_text = match.group(0)

        parsed = json.loads(
            json_text
        )

        return {

            "judge_failed": False,

            "pass":
                parsed["pass"],

            "reason":
                parsed["reason"]
        }

    except Exception as e:

        return {

            "judge_failed": True,

            "pass": False,

            "reason": str(e)
        }


# =================================================
# MAIN
# =================================================

def main():

    summary_table = Table(
        title="INTELLI-SITE EVALUATION"
    )

    summary_table.add_column("Case")

    summary_table.add_column("Retrieval")

    summary_table.add_column("Output Data")

    summary_table.add_column("Expectation")

    summary_table.add_column("Final")

    for case in TEST_CASES:

        console.rule(
            f"CASE {case['id']}"
        )

        result = run_query_pipeline(

            bbl=case["bbl"],

            question=case["question"],

            save_logs=False,

            verbose=False
        )

        answer = result["response"]

        retrieved_chunks = result[
            "retrieved_chunks"
        ]

        console.print(
            "\n[bold cyan]QUESTION[/bold cyan]"
        )

        console.print(
            case["question"]
        )

        # =====================================
        # RETRIEVAL EVAL
        # =====================================

        retrieval_result = None

        if "expected_sections" in case:

            retrieval_result = evaluate_retrieval(

                case["expected_sections"],

                retrieved_chunks
            )

            console.print(
                "\n[bold yellow]EXPECTED SECTIONS[/bold yellow]"
            )

            for sec in case[
                "expected_sections"
            ]:

                console.print(f"- {sec}")

            console.print(
                "\n[bold yellow]RETRIEVED SOURCES[/bold yellow]"
            )

            for src in retrieval_result[
                "retrieved_sources"
            ]:

                console.print(f"- {src}")

            console.print(
                f"\n[bold green]RETRIEVAL PASS:[/bold green] "
                f"{retrieval_result['pass']}"
            )

            if retrieval_result["missing"]:

                console.print(
                    f"[bold red]MISSING:[/bold red] "
                    f"{retrieval_result['missing']}"
                )

        # =====================================
        # ANSWER
        # =====================================

        console.print(

            Panel(

                answer,

                title="ANSWER"
            )
        )

        # =====================================
        # OUTPUT DATA EVAL
        # =====================================

        output_data_result = None

        if "output_data" in case:

            output_data_result = evaluate_output_data(

                case["output_data"],

                answer
            )

            console.print(
                "\n[bold yellow]OUTPUT DATA CHECK[/bold yellow]"
            )

            console.print(
                f"PASS: {output_data_result['pass']}"
            )

            if output_data_result["missing"]:

                console.print(
                    f"Missing: "
                    f"{output_data_result['missing']}"
                )

        # =====================================
        # OUTPUT EXPECTATION JUDGE
        # =====================================

        expectation_result = None

        if "output_expectation" in case:

            expectation_key = case[
                "output_expectation"
            ][0]

            expectation_result = (
                run_expectation_judge(

                    expectation_key,

                    case["question"],

                    answer
                )
            )

            console.print(
                "\n[bold magenta]EXPECTATION JUDGE[/bold magenta]"
            )

            console.print(
                f"PASS: "
                f"{expectation_result['pass']}"
            )

            console.print(
                f"REASON: "
                f"{expectation_result['reason']}"
            )

        # =====================================
        # FINAL RESULT
        # =====================================

        final_pass = True

        if retrieval_result:

            final_pass = (
                final_pass
                and retrieval_result["pass"]
            )

        if output_data_result:

            final_pass = (
                final_pass
                and output_data_result["pass"]
            )

        if expectation_result:

            final_pass = (
                final_pass
                and expectation_result["pass"]
            )

        console.print(
            f"\n[bold cyan]FINAL RESULT:[/bold cyan] "
            f"{final_pass}"
        )

        summary_table.add_row(

            str(case["id"]),

            str(
                retrieval_result["pass"]
                if retrieval_result
                else "-"
            ),

            str(
                output_data_result["pass"]
                if output_data_result
                else "-"
            ),

            str(
                expectation_result["pass"]
                if expectation_result
                else "-"
            ),

            str(final_pass)
        )

    console.print("\n")

    console.print(summary_table)


if __name__ == "__main__":

    main()
