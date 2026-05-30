from datetime import datetime


from src.eval.eval_cases import (
    EVAL_CASES
)

from src.query import (
    run_query_pipeline
)


# =====================================================
# CHECK RETRIEVED SECTIONS
# =====================================================

def evaluate_retrieval(

    expected_sections: list,

    retrieved_chunks: list
):

    retrieved_section_ids = [

        chunk.get("section_id")

        for chunk in retrieved_chunks
    ]

    matched = []

    missing = []

    for section_id in expected_sections:

        if section_id in retrieved_section_ids:

            matched.append(
                section_id
            )

        else:

            missing.append(
                section_id
            )

    # =============================================
    # CONDITIONAL PASS
    # =============================================

    if len(expected_sections) == 0:

        passed = True

    else:

        passed = (
            len(missing) == 0
        )

    return {

        "passed":
        passed,

        "matched":
        matched,

        "missing":
        missing,

        "retrieved":
        retrieved_section_ids
    }


# =====================================================
# CHECK CITATIONS
# =====================================================

def evaluate_citations(
    response: str
):

    # =============================================
    # BAD CITATIONS
    # =============================================

    if "UNKNOWN_CITATION" in response:

        return {

            "passed":
            False,

            "detected":
            False
        }

    # =============================================
    # DETECT CITATIONS
    # =============================================

    has_citations = (

        "[SOURCE_"

        in response
    )

    return {

        "passed":
        has_citations,

        "detected":
        has_citations
    }


# =====================================================
# CHECK ABSTENTION
# =====================================================

def evaluate_abstention(

    response: str,

    must_abstain: bool
):

    abstention_phrases = [

        "insufficient",

        "not provided",

        "cannot determine",

        "does not support",

        "not enough information",

        "corpus does not",

        "not available",

        "not contained",

        "cannot be determined"
    ]

    response_lower = response.lower()

    detected = any(

        phrase in response_lower

        for phrase in abstention_phrases
    )

    if must_abstain:

        passed = detected

    else:

        passed = True

    return {

        "passed":
        passed,

        "detected":
        detected
    }


# =====================================================
# CHECK VINTAGE WARNINGS
# =====================================================

def evaluate_vintage(

    warnings: list,

    must_warn_vintage: bool
):

    detected = len(warnings) > 0

    if must_warn_vintage:

        passed = detected

    else:

        passed = True

    return {

        "passed":
        passed,

        "detected":
        detected
    }


# =====================================================
# CHECK DEPENDENCY EXPANSION
# =====================================================

def evaluate_dependencies(

    retrieved_chunks: list,

    must_follow_dependencies: bool
):

    dependency_chunks = [

        chunk

        for chunk in retrieved_chunks

        if chunk.get(
            "retrieval_type"
        )
        ==
        "dependency"
    ]

    detected = (
        len(dependency_chunks)
        > 0
    )

    if must_follow_dependencies:

        passed = detected

    else:

        passed = True

    return {

        "passed":
        passed,

        "detected":
        detected
    }


# =====================================================
# RUN SINGLE EVAL CASE
# =====================================================

def run_single_eval(

    eval_case: dict
):

    print("\n====================================")
    print(f"RUNNING {eval_case['id']}")
    print("====================================\n")

    # =============================================
    # RUN PIPELINE
    # =============================================

    result = run_query_pipeline(

        bbl=
        eval_case["bbl"],

        question=
        eval_case["question"],

        verbose=False,

        save_logs=False
    )

    # =============================================
    # DISPLAY INFO
    # =============================================

    print(
        f"Category: "
        f"{eval_case['category']}"
    )

    print(
        f"\nQuery Type:\n"
    )

    print(
        result["query_type"]
    )

    print(
        f"\nQuestion:\n"
    )

    print(
        eval_case["question"]
    )

    print(
        f"\nExpected Behaviors:\n"
    )

    for behavior in eval_case[
        "expected_behaviors"
    ]:

        print(
            f"- {behavior}"
        )

    print(
        f"\nExpected Sections:\n"
    )

    if eval_case["expected_sections"]:

        for section in eval_case[
            "expected_sections"
        ]:

            print(
                f"- {section}"
            )

    else:

        print("None")

    print(
        f"\nRetrieved Sections:\n"
    )

    if result["retrieved_chunks"]:

        for chunk in result[
            "retrieved_chunks"
        ]:

            print(

                f"- "
                f"{chunk.get('section_id')} "
                f"({chunk.get('retrieval_type')})"
            )

    else:

        print("None")

    print(
        f"\nWarnings:\n"
    )

    if result["warnings"]:

        for warning in result["warnings"]:

            print(
                f"- {warning}"
            )

    else:

        print("None")

    print(
        f"\nFinal Response:\n"
    )

    print(result["response"])

    print("\n")

    # =============================================
    # EVALUATIONS
    # =============================================

    retrieval_eval = evaluate_retrieval(

        expected_sections=
        eval_case[
            "expected_sections"
        ],

        retrieved_chunks=
        result[
            "retrieved_chunks"
        ]
    )

    citation_eval = evaluate_citations(

        response=
        result["response"]
    )

    abstention_eval = evaluate_abstention(

        response=
        result["response"],

        must_abstain=
        eval_case[
            "must_abstain"
        ]
    )

    vintage_eval = evaluate_vintage(

        warnings=
        result["warnings"],

        must_warn_vintage=
        eval_case[
            "must_warn_vintage"
        ]
    )

    dependency_eval = evaluate_dependencies(

        retrieved_chunks=
        result["retrieved_chunks"],

        must_follow_dependencies=
        eval_case[
            "must_follow_dependencies"
        ]
    )

    # =============================================
    # OVERALL PASS
    # =============================================

    passed = True

    # =============================================
    # RETRIEVAL
    # =============================================

    if not retrieval_eval["passed"]:

        passed = False

    # =============================================
    # CITATIONS
    # =============================================

    if result["retrieved_chunks"]:

        if not citation_eval["passed"]:

            passed = False

    # =============================================
    # ABSTENTION
    # =============================================

    if eval_case["must_abstain"]:

        if not abstention_eval["passed"]:

            passed = False

    # =============================================
    # VINTAGE
    # =============================================

    if eval_case["must_warn_vintage"]:

        if not vintage_eval["passed"]:

            passed = False

    # =============================================
    # DEPENDENCIES
    # =============================================

    if eval_case["must_follow_dependencies"]:

        if not dependency_eval["passed"]:

            passed = False

    # =============================================
    # DISPLAY BREAKDOWN
    # =============================================

    print("Evaluation Breakdown:\n")

    print(
        f"Retrieval: "
        f"{retrieval_eval['passed']}"
    )

    print(
        f"Citations: "
        f"{citation_eval['passed']}"
    )

    print(
        f"Abstention: "
        f"{abstention_eval['passed']}"
    )

    print(
        f"Vintage: "
        f"{vintage_eval['passed']}"
    )

    print(
        f"Dependencies: "
        f"{dependency_eval['passed']}"
    )

    print(
        f"\nOVERALL: "
        f"{passed}"
    )

    print("\n" + "="*60 + "\n")

    # =============================================
    # RESULT OBJECT
    # =============================================

    eval_result = {

        "eval_id":
        eval_case["id"],

        "question":
        eval_case["question"],

        "passed":
        passed,

        "retrieval":
        retrieval_eval,

        "citations":
        citation_eval,

        "abstention":
        abstention_eval,

        "vintage":
        vintage_eval,

        "dependencies":
        dependency_eval,

        "response":
        result["response"]
    }

    return eval_result


# =====================================================
# RUN ALL EVALS
# =====================================================

def run_all_evals():

    all_results = []

    total = len(EVAL_CASES)

    passed = 0

    # =============================================
    # RUN EACH CASE
    # =============================================

    for eval_case in EVAL_CASES:

        result = run_single_eval(
            eval_case
        )

        all_results.append(
            result
        )

        if result["passed"]:

            passed += 1

    # =============================================
    # SUMMARY
    # =============================================

    summary = {

        "timestamp":
        datetime.now().isoformat(),

        "total_cases":
        total,

        "passed_cases":
        passed,

        "failed_cases":
        total - passed,

        "pass_rate":
        round(
            passed / total,
            2
        ),

        "results":
        all_results
    }

    return summary


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("\n====================================")
    print("RUNNING EVAL SUITE")
    print("====================================\n")

    report = run_all_evals()

    print("\n====================================")
    print("EVAL SUMMARY")
    print("====================================\n")

    print(
        f"Total Cases: "
        f"{report['total_cases']}"
    )

    print(
        f"Passed: "
        f"{report['passed_cases']}"
    )

    print(
        f"Failed: "
        f"{report['failed_cases']}"
    )

    print(
        f"Pass Rate: "
        f"{report['pass_rate']}"
    )

    print("\n====================================\n")