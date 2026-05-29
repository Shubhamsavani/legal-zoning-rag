import sys
import pandas as pd


SITE_RECORDS_PATH = "corpus/structured/site_records.csv"

PLUTO_PATH = "corpus/structured/pluto_25v4.csv"


PLUTO_COLUMNS = [
    "builtfar",
    "residfar",
    "commfar",
    "facilfar",
    "numfloors",
    "bldgarea",
    "landuse"
]


def lookup_site(bbl: str) -> dict:

    # -----------------------------
    # Load CSV files
    # -----------------------------
    site_df = pd.read_csv(
        SITE_RECORDS_PATH,
        dtype=str
    )

    pluto_df = pd.read_csv(
        PLUTO_PATH,
        dtype=str
    )

    # -----------------------------
    # Normalize BBL columns
    # -----------------------------
    site_df["bbl"] = (
        site_df["bbl"]
        .astype(str)
        .str.strip()
    )

    pluto_df["BBL"] = (
        pluto_df["BBL"]
        .astype(str)
        .str.strip()
    )

    bbl = str(bbl).strip()

    # -----------------------------
    # Lookup in site_records
    # -----------------------------
    site_match = site_df[
        site_df["bbl"] == bbl
    ]

    if site_match.empty:

        print(
            f"\nERROR: BBL {bbl} "
            f"not found in site_records.csv"
        )

        sys.exit(1)

    # Convert first row to dict
    site_record = (
        site_match.iloc[0]
        .dropna()
        .to_dict()
    )

    # -----------------------------
    # Lookup in PLUTO
    # -----------------------------
    pluto_match = pluto_df[
        pluto_df["BBL"] == bbl
    ]

    if not pluto_match.empty:

        pluto_record = (
            pluto_match.iloc[0]
            .dropna()
            .to_dict()
        )

        for column in PLUTO_COLUMNS:

            if column in pluto_record:

                site_record[column] = (
                    pluto_record[column]
                )

    return site_record

# test code
# if __name__ == "__main__":

#     result = lookup_site(
#         "4049630075"
#     )

#     print(result)