def format_site_context(site: dict) -> str:

    lines = []

    lines.append("=== SITE RECORD ===")

    # ---------------------------------
    # Friendly field labels
    # ---------------------------------
    field_mapping = {

        "bbl": "BBL",

        "address": "Address",

        "borough": "Borough",

        "zoning_district": "Zoning District",

        "special_district": "Special District",

        "flood_zone_source": "Flood Zone",

        "lot_area_sqft": "Lot Area",

        "lot_width_ft": "Lot Width",

        "lot_depth_ft": "Lot Depth",

        "building_area_sqft": "Building Area",

        "year_built": "Year Built",

        "building_class": "Building Class",

        "num_stories": "Number of Stories",

        "e_designation": "(E) Designation",

        "census_tract": "Census Tract",

        "pop_density_per_sqmi": "Population Density",

        "median_hh_income_usd": "Median Household Income",

        "income_vintage": "Income Data Vintage",

        "pct_below_poverty": "Percent Below Poverty",

        "pct_renter_occupied": "Percent Renter Occupied",

        "builtfar": "Built FAR",

        "residfar": "Residential FAR Limit",

        "commfar": "Commercial FAR Limit",

        "facilfar": "Facility FAR Limit",

        "numfloors": "PLUTO Number of Floors",

        "bldgarea": "PLUTO Building Area",

        "landuse": "Land Use",

        "notes": "Notes"
    }

    # ---------------------------------
    # Format all non-null fields
    # ---------------------------------
    for field, label in field_mapping.items():

        value = site.get(field)

        if value is None:
            continue

        value = str(value).strip()

        if value == "":
            continue

        # Special formatting
        if field == "e_designation":

            if value.upper() == "Y":

                designation_type = site.get(
                    "e_designation_type",
                    ""
                )

                value = (
                    f"YES — {designation_type}"
                )

            else:
                value = "NO"

        elif field == "lot_area_sqft":

            value = f"{value} sqft"

        elif field == "building_area_sqft":

            value = f"{value} sqft"

        elif field == "median_hh_income_usd":

            value = f"${value}"

        elif field == "pop_density_per_sqmi":

            value = f"{value}/sqmi"

        elif field == "pct_below_poverty":

            value = f"{value}%"

        elif field == "pct_renter_occupied":

            value = f"{value}%"

        lines.append(f"{label}: {value}")

    # ---------------------------------
    # E-designation warning
    # ---------------------------------
    if site.get("e_designation", "").upper() == "Y":

        lines.append("")

        lines.append(
            "⚠ NOTE: (E) designation data "
            "in prose corpus is from Feb 2018 "
            "and is not exhaustive."
        )

        lines.append(
            "Site record confirms active "
            "(E) designation."
        )

        lines.append(
            "Verify current status with "
            "NYC OER."
        )

    return "\n".join(lines)

# testing 

# from src.site.lookup import lookup_site


# if __name__ == "__main__":

#     site = lookup_site(
#         "4049630075"
#     )

#     context = format_site_context(site)

#     print(context)