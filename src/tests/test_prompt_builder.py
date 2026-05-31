from pprint import pprint

from src.retrieval.retriever import (
    retrieve_chunks
)

from src.structured.retrieval import (
    get_complete_site_profile,
    summarize_site_profile
)

from src.prompt_builder import (
    build_prompt
)

# ─────────────────────────────────────────────────────
# TEST INPUT
# ─────────────────────────────────────────────────────

QUESTION = (
    "Does this property have "
    "hazardous material restrictions?"
)

BBL = "4049630075"

# ─────────────────────────────────────────────────────
# STRUCTURED RETRIEVAL
# ─────────────────────────────────────────────────────

profile = get_complete_site_profile(
    BBL
)

summary = summarize_site_profile(
    profile
)

# ─────────────────────────────────────────────────────
# LEGAL RETRIEVAL
# ─────────────────────────────────────────────────────

chunks, warnings = retrieve_chunks(

    question=QUESTION,

    top_k=5,

    threshold=0.38
)

# ─────────────────────────────────────────────────────
# BUILD PROMPT
# ─────────────────────────────────────────────────────

prompt = build_prompt(

    question=QUESTION,

    site_summary=summary,

    retrieved_chunks=chunks,

    warnings=warnings
)

# ─────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────

print("\n" + "=" * 100)

print("PROMPT PREVIEW")

print("=" * 100)

print(prompt[:5000])

print("\n")

print("=" * 100)

print("PROMPT LENGTH")

print("=" * 100)

print(len(prompt))
