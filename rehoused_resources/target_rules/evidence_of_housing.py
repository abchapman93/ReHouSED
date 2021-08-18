from medspacy.ner import TargetRule
from .. import callbacks


housing_rules = [
TargetRule("apartment", "EVIDENCE_OF_HOUSING"),
TargetRule("apartment complex", "EVIDENCE_OF_HOUSING"),
    TargetRule("house", "EVIDENCE_OF_HOUSING",
               ),
    TargetRule("to house", "IGNORE", pattern=[
        {"LOWER": "to"},
        {"LOWER": "house", "POS": "VERB"}
    ]),
    TargetRule("veteran's <RESIDENCE>", "EVIDENCE_OF_HOUSING",
             pattern=[
                      {"_": {"concept_tag": "PATIENT"}, "OP": "+", "IS_TITLE": False},
                      {"_": {"concept_tag": "RESIDENCE"}, "OP": "+", "LOWER": {"NOT_IN": ["housing"]}},
                        {"POS": "NOUN", "OP": "!"},
                      ]
               ),
    TargetRule("<HIS/HER> residence", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"POS": "ADJ", "OP": "*", "LOWER": {"NOT_IN": ["temporary"]}},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+", "LOWER": {"NOT_IN": ["housing", "home"]}},
                   {"POS": "NOUN", "OP": "!"}
                   # {"LOWER": {"IN": ["medication"]}}
               ],
               ),
    TargetRule("<HIS/HER> lease", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"LOWER": "lease"},
               ],
               ),
    TargetRule("home", "EVIDENCE_OF_HOUSING",
               pattern=[{"LOWER": "home"}],
               attributes={"is_ignored": True},
               ),
    TargetRule("Veteran's home", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["veteran", "vets", "patient", "pt"]}},
                   {"LOWER": "'s", "OP": "?"},
                   {"OP": "?", "IS_TITLE": False},
                   {"LOWER": "home"},
               ]),
    TargetRule("<his/her> home", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"LOWER": "home"},
               ],
               on_match=callbacks.his_her_home
               ),
    TargetRule("<HE/SHE> has an apartment", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["he", "she"]}},
                   {"LOWER": "has"},
                   {"LOWER": {"IN": ["a", "an"]}, "OP": "?"},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
               ]),
    TargetRule("<HIS/HER> housing application", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"_": {"concept_tag": "PATIENT"}, "OP": "+", "IS_TITLE": False},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
                   {"LOWER": "application"}
                ],
               attributes={"is_hypothetical": True}),
    TargetRule("<HIS/HER> housing status", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"_": {"concept_tag": "PATIENT"}, "OP": "+", "IS_TITLE": False},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
                   {"LOWER": "status"}
               ],
               attributes={"is_ignored": True}),
    TargetRule("<HIS/HER> housing needs", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"LOWER": "housing"},
                   {"LOWER": "needs"}
               ],
               ),

    TargetRule("move into their apartment", "EVIDENCE_OF_HOUSING",
               pattern=[{"LEMMA": "move"}, {"LOWER": {"IN": ["in", "into"]}},
                        {"_": {"concept_tag": "PATIENT"}, "OP": "+"},
                        {"LOWER": "own", "OP": "?"},
                        {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
                        ],

               ),

    TargetRule("move into <DET> <RESIDENCE>", "EVIDENCE_OF_HOUSING",
               pattern=[{"LEMMA": "move"},
                        {"LOWER": {"IN": ["in", "into"]}},
                        {"POS": "DET"},
                        {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
                        ],
               ),
    TargetRule("signed a lease", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LEMMA": "sign"},
                   {"POS": "DET"},
                   {"LOWER": "lease"},
               ]
               ),
    TargetRule("received the keys", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LEMMA": {"IN": ["receive", "give", "get"]}},
                   {"POS": "DET", "OP": "?"},
                   {"LOWER": "keys"},
               ]
               ),
    TargetRule("pass inspection", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LEMMA": "pass"},
                   {"POS": "DET", "OP": "?"},
                   {"POS": "ADJ", "OP": "*"},
                   {"LOWER": "inspection"},
               ]
               ),
    TargetRule("not pass inspection", "RISK_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "not"},
                   {"LEMMA": "pass"},
                   {"POS": "DET", "OP": "?"},
                   {"POS": "ADJ", "OP": "*"},
                   {"LOWER": "inspection"},
               ]
               ),

    TargetRule("Housing rented by Veteran, no ongoing housing subsidy", "EVIDENCE_OF_HOUSING"),

    TargetRule("housing", "EVIDENCE_OF_HOUSING", attributes={"is_ignored": True}, # Ignore this word by default but flag it for later consideration
               ),
    TargetRule("successfully housed", "EVIDENCE_OF_HOUSING"),
    TargetRule("maintain housing", "EVIDENCE_OF_HOUSING", pattern=[
        {"LOWER": {"REGEX": "maintain"}},
        {"LOWER": "housing"}
    ]),
    TargetRule("stable housing", "EVIDENCE_OF_HOUSING", on_match=callbacks.disambiguate_housing
               ),
    TargetRule("permanent housing", "EVIDENCE_OF_HOUSING", on_match=callbacks.permanent_housing_program),
    TargetRule("housing search", "EVIDENCE_OF_HOUSING", attributes={"is_hypothetical": True},
               pattern=[
                   {"POS": {"IN": ["DET", "ADJ"]}, "OP": "?"},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
                   {"LOWER": {"REGEX": "^search"}},
               ]),
    TargetRule("housing search", "EVIDENCE_OF_HOUSING", attributes={"is_hypothetical": True},
               ),
    TargetRule("housing options", "EVIDENCE_OF_HOUSING",
             pattern=[{"LOWER": "housing"}, {"LEMMA": "option"}],
             attributes={"is_hypothetical": True}),
    TargetRule("option of housing", "EVIDENCE_OF_HOUSING",
             attributes={"is_hypothetical": True}),
    TargetRule("housing leads", "EVIDENCE_OF_HOUSING",
             pattern=[{"LOWER": "housing"}, {"LOWER": "lead"}],
             attributes={"is_hypothetical": True}),

    # TargetRule("place to live", "EVIDENCE_OF_HOUSING"),
    TargetRule("home visit", "EVIDENCE_OF_HOUSING"),

    TargetRule("apartment search", "EVIDENCE_OF_HOUSING", attributes={"is_hypothetical": True}),
    TargetRule("housing application", "EVIDENCE_OF_HOUSING", attributes={"is_hypothetical": True}),
    TargetRule("housing appointment", "EVIDENCE_OF_HOUSING", attributes={"is_hypothetical": True},
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"LOWER": "housing"},
                   {"LOWER": {"IN": ["appointment", "appt"]}}
               ]
               ),
    TargetRule("<THEIR> housing appointment", "EVIDENCE_OF_HOUSING", attributes={"is_hypothetical": True},
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"LOWER": "housing"},
                   {"LOWER": {"IN": ["appointment", "appt"]}}
               ]),
    TargetRule("apartment viewing", "EVIDENCE_OF_HOUSING",
             pattern=[{"LOWER": {"IN": ["housing", "apartment"]}}, {"LEMMA": "viewing"}],
             attributes={"is_hypothetical": True}),
    TargetRule("house hunting", "EVIDENCE_OF_HOUSING",
               pattern=[{"LOWER": {"IN": ["house", "home"]}}, {"LOWER": {"REGEX": r"^hunt"}}],
               attributes={"is_hypothetical": True}
               ),



    # Extract and highlight these, but let's not include them in the document classification logic yet
    TargetRule("landlord", "EVIDENCE_OF_HOUSING", attributes={"is_ignored": True}),
    TargetRule("<THEIR> landlord", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"LOWER": "current", "OP": "?"},
                   {"LOWER": "landlord"}
               ]
               ),
    TargetRule("Veteran's landlord", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"_": {"concept_tag": "PATIENT"}, "OP": "+"},
                   {"LOWER": "current", "OP": "?"},
                   {"LOWER": "landlord"}
               ]
               ),
    TargetRule("voucher", "EVIDENCE_OF_HOUSING", attributes={"is_ignored": True}),

    TargetRule("will be living at", "EVIDENCE_OF_HOUSING", attributes={"is_hypothetical": True}),
    TargetRule("plans to live", "EVIDENCE_OF_HOUSING",
             pattern=[{"LOWER": {"REGEX": "plan"}}, {"LOWER": "to"}, {"LOWER": {"IN": ["live", "reside"]}}],
             attributes={"is_hypothetical": True}),
    TargetRule("discharged to stable housing", "EVIDENCE_OF_HOUSING",
               pattern=r"(d/c|d/c'd|discharged?) to stable housing"
               ),
    TargetRule("Stably housed", "EVIDENCE_OF_HOUSING"),
    TargetRule("stable housing", "EVIDENCE_OF_HOUSING", on_match=callbacks.disambiguate_housing),
    TargetRule("lives independently", "EVIDENCE_OF_HOUSING",
               pattern=[{"LOWER": {"REGEX": "liv(es|ing)"}}, {"LOWER": {"REGEX": "^independent"}}]),
    TargetRule("independent housing", "EVIDENCE_OF_HOUSING",),
    TargetRule("lives at <RESIDENCE>", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LEMMA": {"IN": ["live", "reside"]}},
                   {"LOWER": {"IN": ["at", "in"]}},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+", "IS_TITLE": False}
               ]),
    TargetRule("lives with <FAMILY>", "EVIDENCE_OF_HOUSING",
               pattern=[
                 {"LOWER": {"IN": ["live", "lives", "living",
                                   "reside", "resides", "residing",
                                   "domicile", "domiciles", "domiciling", "domiciled"]}},
                   {"LOWER": {"IN": ["with", "w", "w/"]}},
                   {"LOWER": "/", "OP": "?"},
                   {"LOWER": {"IN": ["his", "her", "their"]}, "OP": "?"},
                   {"_": {"concept_tag": "FAMILY"}, "OP": "+"}
               ]),
    TargetRule("living facility", "EVIDENCE_OF_HOUSING"),
    TargetRule("sold his house", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LEMMA": "sell"},
                   {"POS": "DET"},
                   {"_": {"concept_tag": "RESIDENCE"}}
               ],
               attributes={"is_ignored": True}),

    TargetRule("not worried about housing", "EVIDENCE_OF_HOUSING"),
    TargetRule("approved for a unit", "EVIDENCE_OF_HOUSING"),
    TargetRule("housing subsidy", "EVIDENCE_OF_HOUSING"),
    TargetRule("rental assistance", "EVIDENCE_OF_HOUSING", pattern=[{"LOWER": {"IN": ["rental", "housing"]}}, {"LOWER": "assistance"}]),
    TargetRule("rent", "EVIDENCE_OF_HOUSING"),
    TargetRule("their rent is $\d", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["his", "her"]}},
                   {"LOWER": "rent"},
                   {"LOWER": "is"},
                   {"LOWER": "$", "OP": "?"},
                   {"LIKE_NUM": True}
               ]),
    TargetRule("re-housed", "EVIDENCE_OF_HOUSING"),
    TargetRule("recently housed", "EVIDENCE_OF_HOUSING"),
    TargetRule("remains housed", "EVIDENCE_OF_HOUSING"),
    TargetRule("current/behind on rent", "EVIDENCE_OF_HOUSING",
               pattern=[{"LOWER": {"IN": ["current", "behind"]}},
                        {"LOWER": {"IN": ["in", "on", "with"]}},
                        {"LOWER": "rent"}
                        ]),
    TargetRule("currently housed", "EVIDENCE_OF_HOUSING"),
    TargetRule("paid security deposit", "EVIDENCE_OF_HOUSING"),
    TargetRule("security deposit paid", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": "security"},
                   {"LOWER": "deposit"},
                   {"LEMMA": "be", "OP": "?"},
                   {"LOWER": "paid"}
               ]),
    TargetRule("security deposit", "EVIDENCE_OF_HOUSING"),
    TargetRule("secured housing", "EVIDENCE_OF_HOUSING"),
    TargetRule("resides alone", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["resides", "lives"]}},
                   {"LOWER": "alone"}
               ]),

    TargetRule("<RESIDENCE> rented by <PATIENT>", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
                   {"LOWER": {"IN": ["owned", "rented", "leased"]}},
                   {"LOWER": "by"},
                   {"_": {"concept_tag": "PATIENT"}, "OP": "+"},
               ]),

    TargetRule("not at risk of <homelessness>", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": "not"},
                   {"LOWER": "at"},
                   {"OP": "?"},
                   {"LOWER": "risk"},
                   {"LOWER": {"IN": ["of", "for"]}},
                   {"OP": "?"},
                   {"LOWER": {"IN": [
                       "homelessness",
                       "eviction",
                       "homeless"
                   ]}},
               ]),

    TargetRule("found a new apartment", "EVIDENCE_OF_HOUSING",
               pattern=[
                   {"LOWER": "found"},
                   {"LOWER": "a"},
                   {"LOWER": "new"},
                   {"LOWER": {"IN": ["apartment", 'apt']}},
               ]),

]