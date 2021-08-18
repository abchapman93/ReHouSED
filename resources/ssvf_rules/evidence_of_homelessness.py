from medspacy.ner import TargetRule
from .. import callbacks

homeless_rules = [
    TargetRule("homeless", "EVIDENCE_OF_HOMELESSNESS", pattern=[{"LOWER": {"REGEX": "homeless"}}]),
    TargetRule("chronic homelessness", "EVIDENCE_OF_HOMELESSNESS",
             pattern=[{"LOWER": {"REGEX": "^chronic"}},
                 {"LOWER": {"REGEX": "^homeless"}}]),
    TargetRule("literally homeless", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("homeless veteran", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("sleep in <HOMELESS_LOCATION>", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   # {"LEMMA": "sleep"},
                   # {"LOWER": "in"},
                    {"_": {"concept_tag": "RESIDES"}, "OP": "+"},
                   {"OP": "?"},
                   {"_": {"concept_tag": "HOMELESS_LOCATION"}}
               ]),
    # TODO: The previous rule should make these redundant
    TargetRule("sleep in park", "EVIDENCE_OF_HOMELESSNESS", pattern=[{"LEMMA": "sleep"},
                                                                   {"LOWER": "in"},
                                                                   {"POS": "DET", "OP": "?"},
                                                                {"LOWER": "park"}]),
    TargetRule("live on streets", "EVIDENCE_OF_HOMELESSNESS", pattern=[{"LEMMA": "live"},
                                                                    {"LOWER": "on"},
                                                                    {"LOWER": "the", "OP": "?"},
                                                                    {"LEMMA": "street"}]),

    TargetRule("lose housing", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LEMMA": "lose"},
                    # {"POS": "DET"},
                    {},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
    ]),
    TargetRule("<RESIDES> in <PROPN> Park", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"_": {"concept_tag": "RESIDES"}, "OP": "+"},
                   {"LOWER": "the", "OP": "?"},
                   {"IS_TITLE": True, "OP": "+"},
                   {"LOWER": "park"}
               ]),
    TargetRule("At least 1 night", "EVIDENCE_OF_HOMELESSNESS"), # Answer to template "How long have you been homeless?"
    TargetRule("How long have you been homeless? ", "EVIDENCE_OF_HOMELESSNESS",
               pattern= [
                   {"LOWER": "how"},
                   {"LOWER": "long"},
                   {"LOWER": "have"},
                   {"LOWER": "you"},
                   {"LOWER": "been"},
                   {"LOWER": "homeless"},
                   {"LOWER": "?"},
                   {"IS_SPACE": True, "OP": "*"},
                   {"LIKE_NUM": True, "OP": "+"},
                   {"LOWER": {"REGEX": r"^(day|week|month|year)"}}
               ],
               # pattern=r"How long have you been homeless\?[\s]+[\d]"
               ),
    TargetRule("Is veteran currently homeless? No", "EVIDENCE_OF_HOMELESSNESS",
               attributes={"is_negated": True},
               pattern=[
                   {"LOWER": "is"},
                   {"LOWER": "the", "OP": "?"},
                   {"LOWER": {"IN": ["veteran", "vet", "patient", "pt"]}},
                   {"LOWER": "currently"},
                   {"LOWER": "homeless"},
                   {"LOWER": "?"},
                   {"IS_SPACE": True, "OP": "*"},
                   {"LOWER": {"IN": ["no", "n", "not"]}},
               ]
               ),
    TargetRule("Is veteran currently homeless? Yes", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "is"},
                   {"LOWER": "the", "OP": "?"},
                   {"LOWER": {"IN": ["veteran", "vet", "patient", "pt"]}},
                   {"LOWER": "currently"},
                   {"LOWER": "homeless"},
                   {"LOWER": "?"},
                   {"IS_SPACE": True, "OP": "*"},
                   {"LOWER": {"IN": ["Yes", "y"]}},
               ]
               ),
    TargetRule("lack of housing", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}),
    TargetRule("Housing lack", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}),
    TargetRule("homeless letter", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"REGEX": "homeless"}},
                   {"LOWER": "verification", "OP": "?"},
                   {"LOWER": "letter"},
               ]),
    TargetRule("in need of housing", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("needs housing", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[{"LEMMA": "need"}, {"LOWER": "housing"}]),
    TargetRule("Needs: Housing", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("needs stable housing", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[{"LEMMA": "need"}, {"LOWER": "stable"}, {"LOWER": "housing"}]),
    TargetRule("admitted from <HOMELESS_LOCATION>", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"REGEX": "^admit"}},
                   {"LOWER": "from"},
                   {"OP": "?"},
                    {"_": {"concept_tag": "HOMELESS_LOCATION"}, "OP": "+"},
               ]),
    TargetRule("unoccupied apartment", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("residing outside", "EVIDENCE_OF_HOMELESSNESS",
             pattern=[{"LEMMA": {"IN": ["reside", "sleep", "stay"]}},
                      {"LOWER": {"IN": ["outdoors", "outside"]}}]),
    TargetRule("v60.0", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}), # ICD-9
    TargetRule("Lack of Housing (ICD-9-CM V60.0)", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}),
    TargetRule("No - Not living in stable housing", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("Did the Veteran enter the HUD-VASH program?  Yes", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("Admitted to HUD-VASH", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "admitted"},
                   {"LOWER": {"IN": ["to", "into"]}},
                   {"OP": "?"},
                   {"_": {"concept_tag": "HUD-VASH"}, "OP":"+"},
               ]),

    TargetRule("Homeless single person (SCT 160700001)", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}),
    TargetRule("Homeless single person", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}),
    TargetRule("(SCT 266935003)", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}),
    TargetRule("z59.0", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}), # ICD-10
    TargetRule("Dx: Z59.0 (homelessness)", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}), # ICD-10
    TargetRule("Lack of Housing (Z59.0)", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}), # ICD-10
    TargetRule("Homeless (SNOMED CT 32911000) Z59.0", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}), # ICD-10
    TargetRule("Homelessness (ICD-10-CM Z59.0)", "EVIDENCE_OF_HOMELESSNESS", attributes={"is_historical": True}), # ICD-10

    TargetRule("place not meant for human habitation", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "place"},
                   {"LOWER": "not"},
                   {"LOWER": "meant"},
                   {"LOWER": "for"},
                   {"LOWER": "human"},
                   {"LOWER": {"REGEX": "^habitat"}},
               ]),
    TargetRule("Place not meant for habitation", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("homelessness issues", "EVIDENCE_OF_HOMELESSNESS",
             pattern=[{"LOWER": {"REGEX": "homeless"}}, {"LOWER": {"REGEX": "issue"}}],
             attributes={"is_hypothetical": True}),
    TargetRule("Is Veteran currently homeless? - No", "EVIDENCE_OF_HOMELESSNESS",
             attributes={"is_negated": True},
             pattern=[{"LOWER": "is"}, {"LOWER": "veteran"},
                      {"LOWER": "currently"}, {"LOWER": "homeless"},
                      {"LOWER": "?"}, {"LOWER": "-"},
                      {"IS_SPACE": True, "OP": "*"},
                      {"LOWER": "no"}]),
    TargetRule("Is Veteran currently homeless? - Yes", "EVIDENCE_OF_HOMELESSNESS",
             pattern=[{"LOWER": "is"}, {"LOWER": "veteran"},
                      {"LOWER": "currently"}, {"LOWER": "homeless"},
                      {"LOWER": "?"}, {"LOWER": "-"},
                      {"IS_SPACE": True, "OP": "*"},
                      {"LOWER": "yes"}]),
    TargetRule("Veteran Meets Homeless Criteria:", "EVIDENCE_OF_HOMELESSNESS", on_match=callbacks.parse_question_response_checkmark_right_yes),
    # If this one is not followed by 'Yes [X]', it will be removed and will allow
    # the shorter "CHRONICALLY Homeless" entity to match
    TargetRule("Veteran is CHRONICALLY Homeless:", "IGNORE", on_match=callbacks.parse_question_response_checkmark_right_not_yes),
    TargetRule("does not know where they will be staying", "EVIDENCE_OF_HOMELESSNESS",
             pattern=[
                 {"LOWER": "does"},
                 {"LOWER": "not"},
                 {"LOWER": "know"},
                 {"LOWER": "where"},
                 {"LOWER": {"IN": ["he", "she", "they"]}},
                 {"LOWER": "will"},
                 {"LOWER": "be", "OP": "?"},
                 {"LEMMA": "stay"}
             ]),
    TargetRule("Inadequate Housing", "EVIDENCE_OF_HOMELESSNESS",
               attributes={"is_historical": True}),
    TargetRule("Homeless: No", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "homeless"},
                   {"LOWER": ":"},
                   {"IS_SPACE": True, "OP": "*"},
                   {"LOWER": "no"}
               ],
               attributes={"is_negated": True}),
    TargetRule("need a place  to stay", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LEMMA": "need"},
                   {"LOWER": "a"},
                   {"LOWER": "place"},
                   {"LOWER": "to"},
                   {"LOWER": "stay"},
               ]
               ),
    TargetRule("Diagnosis: Homeless", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "diagnosis"}, {"TEXT": ":"}, {"LOWER": {"REGEX": "^homeless"}}
               ],
               attributes={"is_historical": True},
               ),
    TargetRule("live out of a <HOMELESS_LOCATION>", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LEMMA": "live"}, {"LOWER": "out"}, {"LOWER": "of"}, {"OP": "?"},
                   {"_": {"concept_tag": "HOMELESS_LOCATION"}, "OP": "+"}
               ]),
    TargetRule("live in <HOMELESS_LOCATION>", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LEMMA": "live"}, {"LOWER": "in"},
                   {"_": {"concept_tag": "HOMELESS_LOCATION"}, "OP": "+"}
               ]),
    # TargetRule("Veteran Meets Homeless Criteria: Yes [X]", "EVIDENCE_OF_HOMELESSNESS",
    #            # eteran, Meets, Homeless, Criteria, :, Yes, [X]
    #            pattern=[
    #                {"TEXT": "Veteran"},
    #                {"TEXT": "Meets"},
    #                {"TEXT": "Homeless"},
    #                {"TEXT": "Criteria"},
    #                {"TEXT": ":"},
    #                {"IS_SPACE": True, "OP": "*"},
    #                {"TEXT": "Yes"},
    #                {"TEXT": "[X]"},
    #            ]
    #            ),
    TargetRule("Homeless? Yes", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"TEXT": "Homeless"},
                   {"TEXT": "?"},
                   {"IS_SPACE": True, "OP": "*"},
                   {"TEXT": "Yes"}
               ]
    ),

    TargetRule("How long have you been homeless? <NUM> <TIME>", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "how"},
                   {"LOWER": "long"},
                   {"LOWER": "have"},
                   {"LOWER": "you"},
                   {"LOWER": "been"},
                   {"LOWER": "homeless"},
                   {"LOWER": "?"},
                   {"IS_SPACE": True, "OP": "*"},
                   {"LIKE_NUM": True, "OP": "+"},
                   {"LEMMA": {"IN": ["year", "day", "month", "week"]}}
               ]),

    TargetRule("<RESIDES> ... <HOMELESS_LOCATION>", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[{"_": {"concept_tag": "HOMELESS_LOCATION"}, "OP": "+"}],
               # TODO: Watch out for this
                # on_match=callbacks.stay_in_homeless_location,
               ),

    TargetRule("HOMELESS HISTORY", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"TEXT": {"REGEX": "HOMELESS"}},
                   {"TEXT": "HISTORY"},
               ],
               attributes={"is_historical": True}),
    TargetRule("HOMELESSNESS", "EVIDENCE_OF_HOMELESSNESS", # Numbered lists with 'HOMELESSNESS' are probably PMH
               pattern=[
                   {"LIKE_NUM": True},
                   {"LOWER": "."},
                   {"TEXT": "HOMELESSNESS"}]
               ,
              attributes={"is_historical": True},
               ),

    TargetRule("squatting", "EVIDENCE_OF_HOMELESSNESS", pattern=[{"LOWER": {"IN": ["squatting", "squatted"]}}]),
    TargetRule("was homeless", "EVIDENCE_OF_HOMELESSNESS",
               attributes={"is_historical": True}),

    TargetRule("section 8 voucher", "EVIDENCE_OF_HOMELESSNESS"),
    TargetRule("HUD-VASH voucher", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "hud", "OP": "?"},
                   {"LOWER": {"IN": ["/","-"]}, "OP": "?"},
                   {"LOWER": "vash"},
                   {"LOWER": "voucher"}
               ]),
    TargetRule("housing choice voucher", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "housing", "OP": "?"},
                   {"LOWER": "choice"},
                   {"LOWER": "voucher"}
               ]
               ),
    TargetRule("housing choice voucher", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": "housing"},
                   {"OP": "?"},
                   {"LOWER": "voucher"}
               ]
               ),
    TargetRule("admitted to hud-vash", "EVIDENCE_OF_HOMELESSNESS",
               pattern=[
                   {"LOWER": {"REGEX": r"(admit|admission)"}},
                   {"LOWER": "to"},
                   {"_": {"concept_tag": "HUD-VASH"}, "OP": "+"},
               ]),
    TargetRule("Is the Veteran entering a residential treatment program? Yes", "EVIDENCE_OF_HOMELESSNESS",
               pattern=r"Is the Veteran entering a residential treatment program\?[\s]+Yes"),
    TargetRule("<ADJ> homeless individuals", "IGNORE",
               pattern=[
                   {"POS": {"IN": ["ADJ", "ADV"]}, "OP": "*"},
                   {"LOWER": "homeless"},
                   {"LOWER": "individuals"}
               ]
               )
    ]