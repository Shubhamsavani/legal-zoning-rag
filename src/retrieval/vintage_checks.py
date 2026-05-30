from datetime import datetime


# =====================================================
# STALE THRESHOLD
# =====================================================

STALE_YEARS_THRESHOLD = 10


# =====================================================
# PARSE AMENDMENT DATE
# =====================================================

def parse_amendment_date(

    amendment_str: str
):

    try:

        return datetime.strptime(
            amendment_str,
            "%m/%d/%Y"
        )

    except Exception:

        return None


# =====================================================
# DETECT HISTORICAL CHUNKS
# =====================================================

def detect_historical_chunks(

    retrieved_chunks: list
):

    warnings = []

    historical_chunks = []

    for chunk in retrieved_chunks:

        if (
            chunk.get(
                "is_historical"
            )
            ==
            "true"
        ):

            historical_chunks.append(

                chunk.get(
                    "section_id",
                    "UNKNOWN"
                )
            )

    if historical_chunks:

        warnings.append(

            "Retrieved context includes "

            "historical or superseded "

            "provisions: "

            +

            ", ".join(
                historical_chunks
            )
        )

    return warnings


# =====================================================
# DETECT STALE AMENDMENTS
# =====================================================

def detect_stale_amendments(

    retrieved_chunks: list
):

    warnings = []

    current_year = datetime.now().year

    stale_sections = []

    for chunk in retrieved_chunks:

        amendment_date = parse_amendment_date(

            chunk.get(
                "last_amended",
                ""
            )
        )

        if not amendment_date:
            continue

        amendment_year = amendment_date.year

        age = (
            current_year
            -
            amendment_year
        )

        if age >= STALE_YEARS_THRESHOLD:

            stale_sections.append(

                f"{chunk.get('section_id')} "
                f"({amendment_year})"
            )

    if stale_sections:

        warnings.append(

            "Some retrieved provisions "

            "may be outdated or older "

            "than expected: "

            +

            ", ".join(
                stale_sections
            )
        )

    return warnings


# =====================================================
# DETECT MIXED AMENDMENT ERAS
# =====================================================

def detect_mixed_amendment_eras(

    retrieved_chunks: list
):

    warnings = []

    amendment_years = []

    for chunk in retrieved_chunks:

        amendment_date = parse_amendment_date(

            chunk.get(
                "last_amended",
                ""
            )
        )

        if amendment_date:

            amendment_years.append(
                amendment_date.year
            )

    if len(amendment_years) < 2:
        return warnings

    oldest = min(amendment_years)

    newest = max(amendment_years)

    year_gap = newest - oldest

    # =============================================
    # LARGE TEMPORAL GAP
    # =============================================

    if year_gap >= 10:

        warnings.append(

            "Retrieved context spans "

            "multiple amendment eras "

            f"({oldest}–{newest}). "

            "Some provisions may reflect "

            "different zoning frameworks."
        )

    return warnings


# =====================================================
# DETECT DISTRICT SCOPE VARIATION
# =====================================================

def detect_district_scope_variation(

    retrieved_chunks: list
):

    warnings = []

    scopes = set()

    for chunk in retrieved_chunks:

        scope = chunk.get(
            "district_scope"
        )

        if scope:

            scopes.add(scope)

    if len(scopes) > 1:

        warnings.append(

            "Retrieved provisions apply "

            "to different zoning district "

            "scopes. Applicability may vary "
            
            "depending on district type."
        )

    return warnings


# =====================================================
# MAIN WARNING PIPELINE
# =====================================================

def generate_vintage_warnings(

    retrieved_chunks: list
):

    warnings = []

    # =============================================
    # HISTORICAL / SUPERSEDED
    # =============================================

    warnings.extend(

        detect_historical_chunks(
            retrieved_chunks
        )
    )

    # =============================================
    # STALE AMENDMENTS
    # =============================================

    warnings.extend(

        detect_stale_amendments(
            retrieved_chunks
        )
    )

    # =============================================
    # MIXED AMENDMENT ERAS
    # =============================================

    warnings.extend(

        detect_mixed_amendment_eras(
            retrieved_chunks
        )
    )

    # =============================================
    # DISTRICT SCOPE VARIATION
    # =============================================

    warnings.extend(

        detect_district_scope_variation(
            retrieved_chunks
        )
    )

    return warnings


# =====================================================
# TEST BLOCK
# =====================================================

if __name__ == "__main__":

    fake_chunks = [

        {

            "section_id":
            "23-22",

            "last_amended":
            "05/12/2008",

            "is_historical":
            "true",

            "district_scope":
            "R6 through R12"
        },

        {

            "section_id":
            "23-342",

            "last_amended":
            "05/12/2021",

            "is_historical":
            "false",

            "district_scope":
            "R1 through R10"
        }
    ]

    warnings = generate_vintage_warnings(
        fake_chunks
    )

    print("\n=== WARNINGS ===\n")

    for warning in warnings:

        print(f"- {warning}")