from medspacy.ner import TargetRule
from .. import callbacks

risk_of_homelessness_rules = [
# Risk of homelessness
    TargetRule("z59.8", "RISK_OF_HOMELESSNESS", attributes={"is_historical": True}),
    TargetRule("Other problems related to housing and economic circumstances", "RISK_OF_HOMELESSNESS"), # Z59.8
    TargetRule("evicted", "RISK_OF_HOMELESSNESS",
             pattern=[{"LOWER": "evicted"}]),
    TargetRule("evicted", "RISK_OF_HOMELESSNESS",
             pattern=[{"LOWER": "evicted"}, {"LOWER": "from"},
                      {"LOWER": {"IN": ["his", "her", "their"]}, "OP": "?"},
                      {"LOWER": {"IN": ["house", "apartment", "condo", "room"]}}]
             ),
    TargetRule("risk of homelessness", "RISK_OF_HOMELESSNESS"),
    # Will be removed if not modified by "needs"
    TargetRule("need rental assistance", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LEMMA": {"IN": ["need", "require", "request"]}},
                   {"LOWER": {"IN": ["rental", "housing"]}},
                   {"LOWER": {"IN": ["help", "assistance"]}}
               ]
               ),
    TargetRule("in need of rental assistance", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "in"},
                   {"LOWER": "need"},
                   {"LOWER": "of"},
                   {"LOWER": {"IN": ["rental", "housing"]}},
                   {"LOWER": {"IN": ["help", "assistance"]}}
               ]
               ),

    TargetRule("housing difficulties", "RISK_OF_HOMELESSNESS",
               pattern=[{"LOWER": "housing"}, {"LEMMA": "difficulty"}]),
    TargetRule("housing/X difficulties", "RISK_OF_HOMELESSNESS",
               pattern=[{"LOWER": "housing"}, {"TEXT": "/"},
                        {},
                        {"LEMMA": "difficulty"}]),
    TargetRule("eviction notice", "RISK_OF_HOMELESSNESS"),
    # TargetRule("Unstable", "RISK_OF_HOMELESSNESS",
    #            pattern=[
    #                {"LOWER": "unstable",
    #                 "_": {"section_title": "housing_status"},
    #                 }
    #            ]),
    TargetRule("Unstably housed", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"REGEX": "unstabl"}},
                   {"LOWER": {"REGEX": "hous(ed|ing)"}},
               ]),
    TargetRule("at risk of losing housing", "RISK_OF_HOMELESSNESS"),
    TargetRule("unable to pay bills", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "unable"},
                   {"LOWER": "to"},
                   {"LOWER": "pay"},
                   {"OP": "?"},
                   {"LOWER": {"IN": ["bills", "rent"]}},
               ]),
    TargetRule("stopped paying rent", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"REGEX": "^stop"}},
                   {"LOWER": "paying"},
                   {"OP": "?"},
                   {"LOWER": "rent"}
               ]),
    TargetRule("owe $<NUM>", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LEMMA": "owe"},
                   {"LOWER": "$"},
                   {"LIKE_NUM": True}
               ]),
    TargetRule("lack of stable housing", "RISK_OF_HOMELESSNESS"),
    TargetRule("Unspecified Housing or Economic Problem (Z59.9)", "RISK_OF_HOMELESSNESS"),
    TargetRule("Problem related to housing and economic circumstances, unspecified", "RISK_OF_HOMELESSNESS"),
    TargetRule("Economic Problem", "RISK_OF_HOMELESSNESS",
               pattern=[{"LOWER": "economic"}, {"LOWER": {"REGEX": "^problem"}}]),
    TargetRule("housing needs", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "housing"},
                   {"LEMMA": "need"},
               ]),
    # TargetRule("housing issues", "RISK_OF_HOMELESSNESS"),
    TargetRule("housing and X needs", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "housing"},
                   {"LOWER": "and"},
                   {"OP": "?"},
                   {"LEMMA": "need", "POS": "NOUN"},
               ]),
    TargetRule("concerns about housing", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"REGEX": "concerns?"}},
                   {"LOWER": "about"},
                   {"OP": "?"},
                   {"LOWER": "housing"},
               ]),

    # The following should possibly be "EVIDENCE_OF_HOMELESSNESS"
    TargetRule("v60.9", "RISK_OF_HOMELESSNESS"), # ICD-9
    TargetRule("Unspecified housing or economic circumstance", "RISK_OF_HOMELESSNESS"),

    TargetRule("veteran's housing needs", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"IN": ["veteran", "patient"]}},
                   {"LOWER": "'s"},
                   {"LOWER": "housing"},
                   {"LOWER": "needs"},
               ]),
    TargetRule("<PRON> housing needs", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"POS": "PRON"},
                   {"LOWER": "housing"},
                   {"LOWER": "needs"},
               ]),
    TargetRule("homeless referral", "RISK_OF_HOMELESSNESS"),
    TargetRule("re-house", "RISK_OF_HOMELESSNESS"),

    TargetRule("housing problems", "RISK_OF_HOMELESSNESS",
               # attributes={"is_hypothetical": True}
               ),
    TargetRule("housing problems: <ICD-10>", "RISK_OF_HOMELESSNESS",
               attributes={"is_historical": True},
               pattern=r"housing (problems|issues):?[\s]+\(?[a-z][\d]{2}\.[\d]+"),
    TargetRule("difficulty locating housing", "RISK_OF_HOMELESSNESS"),


]