from pprint import pprint

from src.structured.retrieval import (
    get_complete_site_profile,
    summarize_site_profile
)

BBL = "4049630075"

profile = get_complete_site_profile(
    BBL
)

summary = summarize_site_profile(
    profile
)

print("\nFULL PROFILE\n")

pprint(profile)

print("\nSUMMARY\n")

pprint(summary)
