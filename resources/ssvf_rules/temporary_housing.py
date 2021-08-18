from medspacy.ner import TargetRule
from .. import callbacks

temporary_housing_rules = [

    TargetRule("shelter", "TEMPORARY_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["homeless", "community"]}, "OP": "?"},
                   {"LOWER": "shelter"},

               ]),
    TargetRule("shelter staff", "IGNORE",
               pattern=[
                   {"LOWER": {"IN": ["homeless", "community"]}, "OP": "?"},
                   {"LOWER": "shelter"},
                    {"LOWER": {"REGEX": "staff"}}
               ]),
    TargetRule("Xxx Shelter", "TEMPORARY_HOUSING",
             pattern=[{"IS_TITLE": True, "OP": "+"}, {"TEXT": "Shelter"}, {"LOWER": "staff", "OP": "!"}]),
    TargetRule("bed space", "TEMPORARY_HOUSING"),
    TargetRule("the Domiciliary", "TEMPORARY_HOUSING"),
    TargetRule("temporary housing", "TEMPORARY_HOUSING",
               pattern=[{"LOWER": {"REGEX": "^temp"}},
                        {"LOWER": {"IN": ["residence", "housing"]}}
                        ]),
    TargetRule("transitional housing", "TEMPORARY_HOUSING", pattern=[{"LOWER": {"REGEX": r"tran?sitional"}}, {"LOWER": {"IN": ["housing", "house", "home"]}}]),
    TargetRule("transitional housing", "TEMPORARY_HOUSING",
               pattern=[
                   {"_": {"concept_tag": "RESIDES"}, "OP": "+"},
                   {"LOWER": {"REGEX": r"tran?sitional"}},
                   {"POS": {"IN": ["NOUN", "ADJ", "PRON"]}, "OP": "+"}
               ]),
    TargetRule("<RESIDES> transitional <NOUN>", "TEMPORARY_HOUSING",
               pattern=[
                   {"LOWER": "transitional"},
                   {"LOWER": "housing"}
               ]
               ),
    TargetRule("T-housing", "TEMPORARY_HOUSING",
               pattern=[
                   {"LOWER": "t"},
                   {"LOWER": "-"},
                   {"LOWER": {"REGEX": "hous(e|ing)"}},
               ]),

    TargetRule("recovery home", "TEMPORARY_HOUSING"),
    TargetRule("halfway house", "TEMPORARY_HOUSING"),
    TargetRule("salvation army", "TEMPORARY_HOUSING"),
    TargetRule("volunteers of america", "TEMPORARY_HOUSING"),
    TargetRule("volunteers of america", "TEMPORARY_HOUSING", pattern=[{"LOWER": "voa"}]),
    TargetRule("shelter for the homeless", "TEMPORARY_HOUSING"),
    TargetRule("house meetings", "TEMPORARY_HOUSING",
               pattern=[{"LOWER": "house"}, {"LOWER": {"REGEX": "^meeting"}}]),
    TargetRule("staying at the Xxxx", "TEMPORARY_HOUSING",
             pattern=[{"LEMMA": "stay"}, {"LOWER": "at"}, {"LOWER": "the", "OP": "?"}, {"IS_TITLE": True, "OP": "+"}]),
    TargetRule("at the <NOUN> mission", "TEMPORARY_HOUSING",
             pattern=[{"LOWER": {"IN": ["at", "in"]}}, {"LOWER": "the", "OP": "?"},
                      {"POS": {"IN": ["PROPN", "NOUN", "ADJ"]}, "OP": "*"}, {"LOWER": "mission"}]),

    TargetRule("living at X", "TEMPORARY_HOUSING",
             pattern=[{"LOWER": "living"}, {"LOWER": "at"}, {"LOWER": "the", "OP": "?"}, {"POS": {"IN": ["NOUN", "ADJ", "PROPN"]}, "OP": "+", "IS_TITLE": True}]),
    TargetRule("living in the <TEMPORARY_HOUSING>", "TEMPORARY_HOUSING",
               pattern=[
                   {"LEMMA": {"IN": ["reside", "live"]}},
                   {"LOWER": {"IN": ["in", "at"]}},
                   {"LOWER": "the", "OP": "?"},
                   {"_": {"concept_tag": "TEMPORARY_HOUSING"}, "OP": "+"}
               ]),

    # Patterns for "Xxxx House" seem to not be annotated as temporary housing, so we'll exclude these rules for now
    TargetRule("Xxxx's House", "TEMPORARY_HOUSING",
             pattern=[{"IS_TITLE": True, "OP": "+"},
                      {"TEXT": "'"},
                      {"TEXT": "s"},
                      {"TEXT": "House"}]),
    TargetRule("Xxxx's House", "TEMPORARY_HOUSING",
             pattern=[{"IS_TITLE": True, "OP": "+"},
                      {"TEXT": "'"},
                      {"TEXT": "s"},
                      {"TEXT": "Home"}]),
    TargetRule("Xxxx House", "TEMPORARY_HOUSING",
             pattern=[{"IS_TITLE": True, "OP": "+", "POS": {"NOT_IN": ["VERB"]}}, {"TEXT": {"IN": ["House", "house", "Home"]}},
                      {"IS_TITLE": True, "OP": "?"}, ]),
    TargetRule("House Xxxx", "TEMPORARY_HOUSING", # Maybe this will get patterns like "Odyssey House"
             pattern=[{"IS_TITLE": True, "OP": "?"}, {"TEXT": {"IN": ["House", "house"]}},
                      {"IS_TITLE": True, "OP": "+"}, ]),
    TargetRule("community housing", "TEMPORARY_HOUSING"),
    TargetRule("Domiciliary patient", "TEMPORARY_HOUSING"),
    TargetRule("Domiciliary", "TEMPORARY_HOUSING",
               pattern=[
                   {"LOWER": "domiciliary", "IS_UPPER": False},
               ]),
    TargetRule("Housing Status: <TEMPORARY_HOUSING>", "TEMPORARY_HOUSING",
               pattern=[
                   {"LOWER": "housing"},
                   {"LOWER": "status"},
                   {"LOWER": ":"},
                   {"_": {"concept_tag": "TEMPORARY_HOUSING"}, "OP": "+"}
               ]),
    TargetRule("<RESIDES> <TEMPORARY_HOUSING>", "TEMPORARY_HOUSING",
               pattern=[
                   {"_": {"concept_tag": "RESIDES"}, "OP": "+"},
                   {"_": {"concept_tag": "TEMPORARY_HOUSING"}, "OP": "+"},
               ]),
    TargetRule("at <TEMPORARY_HOUSING>", "TEMPORARY_HOUSING",
               pattern=[
                   {"LOWER": {"IN": ["in", "at"]}},
                   {"_": {"concept_tag": "TEMPORARY_HOUSING"}, "OP": "+"}
               ]),

    TargetRule("emergency housing", "TEMPORARY_HOUSING"),
    TargetRule("room and board", "TEMPORARY_HOUSING"),
    TargetRule("residential facility", "TEMPORARY_HOUSING"),
    TargetRule("shared residence", "TEMPORARY_HOUSING"),

    TargetRule("hotel", "TEMPORARY_HOUSING"),
    TargetRule("rent a hotel", "TEMPORARY_HOUSING"),
    TargetRule("veterans haven", "TEMPORARY_HOUSING",
               pattern=[{"LOWER": {"IN": ["vet", "vets", "veteran"]}}, {"LOWER": "'s", "OP": "?"}, {"LOWER": "haven"}]),

]