from medspacy.ner import TargetRule
from .. import callbacks

doubling_up_rules = [
    TargetRule("doubling up", "DOUBLING_UP", pattern=[{"LEMMA": "double"}, {"LOWER": "up"}]),
    TargetRule("X's apartment", "DOUBLING_UP",
             pattern=[{"_": {"concept_tag": "FAMILY"}, "OP": "+"}, # TODO: Add other similar semtypes
                      {"LOWER": "'", "OP": "?"},
                      {"LOWER": "s", "OP": "?"},
                      {"LOWER": {"IN": ["apartment", "house", "home"]}}]),
    TargetRule("staying with their <FAMILY>", "DOUBLING_UP",
             pattern=[
                 {"LEMMA": {"IN": ["stay", "sleep", "crash"]}},
                 # {"_": {"concept_tag": "RESIDES"}, "OP": "+"},
                      {"LOWER": "with"},
                      {"OP": "?"},
                      {"_": {"concept_tag": "FAMILY"}, "OP": "+"},
                      ]
               ),
    TargetRule("living with <PRON>", "DOUBLING_UP",
               pattern=[
                   {"LEMMA": {"IN": ["stay", "sleep", "crash"]}},
                   #      {"_": {"concept_tag": "RESIDES"}, "OP": "+"},
                        {"LOWER": "with"},
                        {"OP": "?"},
                        {"POS": "PRON"},
                        ],
               on_match=callbacks.resolve_family_coreference_true,
               ),
    TargetRule("crashing at", "DOUBLING_UP",
               pattern=[
                   {"LOWER": "crashing"},
                   {"LOWER": {"IN": ["at", "with"]}},
                    {"_": {"concept_tag": "FAMILY"}, "OP": "*"},
               ]),
    TargetRule("at <FAMILY> <RESIDENCE>", "DOUBLING_UP",
               pattern=[
                   {"LOWER": "at", "OP": "?"},
                   {"_": {"concept_tag": "FAMILY"}, "OP": "+"},
                   {"LOWER": "'s"},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
               ]),
    TargetRule("<PATIENT> <FAMILY> <RESIDENCE>", "DOUBLING_UP",
               pattern=[
                   {"_": {"concept_tag": "PATIENT"}, "OP": "+"},
                   {"_": {"concept_tag": "FAMILY"}, "OP": "+"},
                   {"LOWER": "'s", "OP": "?"},
                   {"_": {"concept_tag": "RESIDENCE"}, "OP": "+"},
               ]),
    TargetRule("sleeping on the couch", "DOUBLING_UP",
               pattern=[
                   {"LEMMA": "sleep"},
                   {"LOWER": "on"},
                   {"POS": "DET"},
                   {"LOWER": "couch"}
               ],
            ),
    TargetRule("couch surfing", "DOUBLING_UP"),
]