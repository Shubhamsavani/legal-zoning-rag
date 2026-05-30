EVAL_CASES = [

    # =================================================
    # FAR LOOKUP
    # =================================================

    {

        "id":
        "eval_001",

        "category":
        "floor_area_ratio",

        "bbl":
        "1016800019",

        "question":
        "What is the maximum floor area ratio for this site?",

        "expected_sections":
        [
            "23-151"
        ],

        "expected_behaviors":
        [
            "cite_retrieved_sections",
            "mention_far"
        ],

        "must_abstain":
        False,

        "must_warn_vintage":
        False,

        "must_follow_dependencies":
        False
    },

    # =================================================
    # REAR YARD REQUIREMENTS
    # =================================================

    {

        "id":
        "eval_002",

        "category":
        "rear_yard",

        "bbl":
        "1016800019",

        "question":
        "Is a rear yard required and how deep must it be?",

        "expected_sections":
        [
            "23-342"
        ],

        "expected_behaviors":
        [
            "mention_rear_yard_depth",
            "cite_retrieved_sections"
        ],

        "must_abstain":
        False,

        "must_warn_vintage":
        False,

        "must_follow_dependencies":
        False
    },

    # =================================================
    # CROSS REFERENCE TEST
    # =================================================

    {

        "id":
        "eval_003",

        "category":
        "cross_reference",

        "bbl":
        "1016800019",

        "question":
        "Can I place an air conditioning unit in the rear yard?",

        "expected_sections":
        [
            "23-341",
            "23-342"
        ],

        "expected_behaviors":
        [
            "follow_cross_reference",
            "cite_dependency_sections"
        ],

        "must_abstain":
        False,

        "must_warn_vintage":
        False,

        "must_follow_dependencies":
        True
    },

    # =================================================
    # ENVIRONMENTAL FLAG
    # =================================================

    {

        "id":
        "eval_004",

        "category":
        "environmental",

        "bbl":
        "1016800019",

        "question":
        "Does this site have any environmental designations?",

        "expected_sections":
        [
            "APPENDIX_CEQR"
        ],

        "expected_behaviors":
        [
            "use_structured_data",
            "mention_environmental_flags"
        ],

        "must_abstain":
        False,

        "must_warn_vintage":
        False,

        "must_follow_dependencies":
        False
    },

    # =================================================
    # DEMOGRAPHIC LOOKUP
    # =================================================

    {

        "id":
        "eval_005",

        "category":
        "demographics",

        "bbl":
        "1016800019",

        "question":
        "What is the population density near this site?",

        "expected_sections":
        [],

        "expected_behaviors":
        [
            "use_structured_data",
            "mention_population_density"
        ],

        "must_abstain":
        False,

        "must_warn_vintage":
        False,

        "must_follow_dependencies":
        False
    },

    # =================================================
    # VINTAGE TEST
    # =================================================

    {

        "id":
        "eval_006",

        "category":
        "historical_far",

        "bbl":
        "1016800019",

        "question":
        "What was the maximum floor area ratio for this zoning district five years ago?",

        "expected_sections":
        [
            "23-151"
        ],

        "expected_behaviors":
        [
            "mention_historical_context",
            "warn_about_vintage"
        ],

        "must_abstain":
        False,

        "must_warn_vintage":
        True,

        "must_follow_dependencies":
        False
    },

    # =================================================
    # ABSTENTION TEST
    # =================================================

    {

        "id":
        "eval_007",

        "category":
        "unsupported_question",

        "bbl":
        "1016800019",

        "question":
        "What is the structural steel load capacity for this building?",

        "expected_sections":
        [],

        "expected_behaviors":
        [
            "abstain_cleanly"
        ],

        "must_abstain":
        True,

        "must_warn_vintage":
        False,

        "must_follow_dependencies":
        False
    },

    # =================================================
    # ANOTHER ABSTENTION
    # =================================================

    {

        "id":
        "eval_008",

        "category":
        "unsupported_question",

        "bbl":
        "1016800019",

        "question":
        "Does this site qualify for LEED platinum certification?",

        "expected_sections":
        [],

        "expected_behaviors":
        [
            "abstain_cleanly"
        ],

        "must_abstain":
        True,

        "must_warn_vintage":
        False,

        "must_follow_dependencies":
        False
    }
]
