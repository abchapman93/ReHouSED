from medspacy.target_matcher import TargetRule

rules = [
    TargetRule("apartment", "RESIDENCE",
               pattern=[
                   {"IS_TITLE": True, "OP": "+"},
                   {"LOWER": {"REGEX": "apartment"}}
               ]
               ),

    TargetRule("<RESIDES>", "RESIDES",
               pattern=[
                   {"LEMMA": {"IN": ["reside", "stay", "live", "sleep"]}},
                   {"LOWER": {"IN": ["in", "at"]}, "OP": "?"}
               ]),
    TargetRule("move in", "RESIDES", pattern=[{"LEMMA": "move"}, {"LOWER": "in"}]),
    TargetRule("current living situation:", "RESIDES"),

    TargetRule("veteran", "PATIENT",
               pattern=[
                   {"LOWER": {"REGEX": "^vet(eran)?"}},
                   {"LOWER": "'s", "OP": "?"}
               ]),
    TargetRule("patient", "PATIENT",
               pattern=[
                   {"LOWER": {"IN": ["patient", "pt", "pt."]}},
                   {"LOWER": "'s", "OP": "?"}
               ]),
    TargetRule("patient", "PATIENT",
               pattern=[
                   {"LOWER": {"IN": [
                       # "his", "her",
                                     "my", "me"]}}
               ]),

    TargetRule("<DET> job", "EMPLOYMENT",
               pattern=[
                   {"POS": "DET"},
                   {"LOWER": "job"},
               ],
               ),
    TargetRule("...Homeless", "HOMELESSNESS",
               pattern=[
                   {"LOWER": {"REGEX": "homeless"}}
               ]),

]