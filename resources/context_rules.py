from medspacy.context import ConTextRule
from src import constants
from . import callbacks


context_rules = [
    # Negation - these values modifiers can change "homeless" to "exit from homeless"
    ConTextRule("without", "NEGATED_EXISTENCE", direction="forward", max_scope=5),
    ConTextRule("overcame", "NEGATED_EXISTENCE", direction="forward", max_scope=5,
                pattern=[{"LOWER": {"REGEX": "overc[oa]me"}}]),
    ConTextRule("not currently", "NEGATED_EXISTENCE", direction="forward", max_scope=5),
    ConTextRule("not", "NEGATED_EXISTENCE", direction="forward", max_scope=5),
    ConTextRule("denies", "NEGATED_EXISTENCE", direction="forward", max_scope=5,
                pattern=[{"LOWER": {"IN": ["denied", "denies"]}}]),
    ConTextRule("denial", "NEGATED_EXISTENCE", direction="forward", max_scope=5),
    ConTextRule("denies risk", "NEGATED_EXISTENCE", direction="forward", max_scope=5,
                pattern=[{"LOWER": {"REGEX": r"denie[d|s]"}}, {"LOWER": "risk"}, {"LOWER": "of", "OP": "?"}]),
    ConTextRule(": denied", "NEGATED_EXISTENCE", direction="BACKWARD", max_scope=5,
                pattern=[{"LOWER": ":"}, {"LOWER": {"REGEX": r"denie[ds]"}}]),
    ConTextRule("declined", "NEGATED_EXISTENCE", direction="BIDIRECTIONAL",
                pattern=[{"LOWER": {"IN": ["decline", "declining"]}}],
                max_scope=5, allowed_types={"TEMPORARY_HOUSING", "EVIDENCE_OF_HOUSING"}),
    ConTextRule("has no", "NEGATED_EXISTENCE", direction="forward", max_scope=5),
    ConTextRule("resolved", "NEGATED_EXISTENCE", direction="backward", max_scope=5),
    ConTextRule("no", "NEGATED_EXISTENCE", direction="FORWARD", max_scope=5),
    ConTextRule("not have", "NEGATED_EXISTENCE", direction="FORWARD", max_scope=5, allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule(": no", "NEGATED_EXISTENCE", direction="BACKWARD", max_scope=5),

    ConTextRule("not eligible for", "NEGATED_EXISTENCE", direction="forward",
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("not interested in", "NEGATED_EXISTENCE", direction="forward"),
    ConTextRule("unable to", "NEGATED_EXISTENCE", direction="forward", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("not want", "NEGATED_EXISTENCE", direction="forward",
                excluded_types={"EVIDENCE_OF_HOMELESSNESS"}),
    ConTextRule("refuse", "NEGATED_EXISTENCE", direction="forward",
                pattern=[{"LEMMA": "refuse"}],
                allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),

    ConTextRule("until <THEY> have/find", "HYPOTHETICAL", direction="FORWARD",
                pattern=[
                    {"LOWER": "until"},
                    {"LOWER": {"IN": ["he", "she"]}},
                    {"LEMMA": {"IN": ["find", "have"]}}
                ],
                allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"},
                max_scope=4),
    ConTextRule("intent to pay", "HYPOTHETICAL"),
    ConTextRule("has chosen", "HYPOTHETICAL", on_modifies=callbacks.has_chosen),
    ConTextRule("waiting for", "HYPOTHETICAL", "FORWARD",
                pattern=[
                    {"LOWER": {"REGEX": "wait(ing)?$"}},
                    {"LOWER": {"IN": ["for", "on"]}}
                ]),
    ConTextRule("awaiting", "HYPOTHETICAL", direction="forward"),
    ConTextRule("prepare", "HYPOTHETICAL", direction="forward",
                pattern=[{"LEMMA": "prepare"}, {"LOWER": "to", "OP": "?"}]),
    ConTextRule("not pay", "NEGATED_EXISTENCE", direction="FORWARD",
                pattern=[{"LOWER": "not"}, {"LEMMA": "pay"}],
                allowed_types={"EVIDENCE_OF_HOUSING"}, on_modifies=callbacks.on_modifies_pay),
    ConTextRule("inability to pay", "NEGATED_EXISTENCE", direction="FORWARD",
                on_modifies=callbacks.on_modifies_pay, allowed_types={"EVIDENCE_OF_HOUSING",}),
    ConTextRule("fell through", "NEGATED_EXISTENCE", direction="BACKWARD",
                pattern=[
                    {"LEMMA": "fall"},
                    {"LOWER": "through"},
                ],
                allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("lacks", "NEGATED_EXISTENCE", "FORWARD", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),

    ConTextRule("[]", "NOT_RELEVANT", direction="forward", # Empty checkmark can mark the adjacent item to be ignored
                max_scope=None),
    ConTextRule("()", "NOT_RELEVANT", direction="forward", # Empty checkmark can mark the adjacent item to be ignored
                max_scope=None),
    ConTextRule("phone number", "NOT_RELEVANT", direction="BACKWARD", pattern=[{"LOWER": {"REGEX": "phone"}}, {"LOWER": {"IN": ["num", "no", "no.", "number"]}}]),
    ConTextRule(": Yes [ ]  No [X]", "NEGATED_EXISTENCE", direction="BACKWARD"),
    ConTextRule(": None", "NEGATED_EXISTENCE", direction="BACKWARD",
                pattern=[{"LOWER": {"IN": ["):"]}}, {"LOWER": "None"}]),
    ConTextRule("___", "NOT_RELEVANT", direction="FORWARD", max_scope=2),
    ConTextRule("not report", "NOT_RELEVANT", "FORWARD", max_scope=5), # "not report being homeless"
    ConTextRule("formerly", "HISTORICAL", direction="forward"),
    ConTextRule("previously", "HISTORICAL", direction="forward"),
    ConTextRule("prior to", "HISTORICAL", direction="forward"),
    ConTextRule("after", "HISTORICAL", direction="forward"),
    ConTextRule("resolved on", "HISTORICAL", direction="BACKWARD"),
    ConTextRule("move out", "HISTORICAL", direction="FORWARD", pattern=[{"LEMMA": "move"}, {"LOWER": "out"}]),
    ConTextRule("before this", "HISTORICAL", direction="forward",
                pattern=[{"LOWER": "before"},
                    {"LOWER": {"IN": ["this", "that"]}}]),
    ConTextRule("on and off", "HISTORICAL", direction="bidirectional"),
    ConTextRule("history of", "HISTORICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOMELESSNESS"},
                pattern=[{"LOWER": {"IN": ["history", "hx"]}}, {"LOWER": "of"}]),
    ConTextRule("past medical history of", "HISTORICAL", "FORWARD", allowed_types={"EVIDENCE_OF_HOMELESSNESS"},
                pattern=[
                    {"LOWER": "past"},
                    {"LOWER": "medical"},
                    {"LOWER": {"IN": ["history", "hx"]}},
                    {"LOWER": "of", 'OP': "?"}

                ]),
    ConTextRule("pmhx of", "HISTORICAL", "FORWARD", allowed_types={"EVIDENCE_OF_HOMELESSNESS"},
                pattern=[
                    {"LOWER": {"IN": ["pmh", "pmhx"]}},
                    {"LOWER": "of", 'OP': "?"}

                ]),
    ConTextRule("within the last N years", "HISTORICAL",
                pattern=[
                    {"LOWER": "within"},
                    {"LOWER": "the", "OP": "?"},
                    {"LOWER": "last"},
                    {"LIKE_NUM": True},
                    {"LOWER": "years"}
                ]),
    ConTextRule("for <TIME>", "HISTORICAL",
                pattern=[
                    {"LOWER": "for"},
                   {"OP": "?"},
                   {"LIKE_NUM": True, "OP": "+"},
                   {"LEMMA": {"IN": ["day", "week", "month", "year"]}}
                ],
                on_match=callbacks.preceded_by_was
                ),
    ConTextRule("within the last year", "HISTORICAL"),
    ConTextRule("in the past", "HISTORICAL", max_scope=5),
    ConTextRule("the last X months", "HISTORICAL", direction="BIDIRECTIONAL",
                pattern=[
                    {"LOWER": {"IN": ["last", "past"]}},
                    {"OP": "?"},
                    {"LEMMA": "month"}
                ]),
    ConTextRule("he left", "HISTORICAL", pattern=[{"LOWER": {"IN": ["he", "she"]}}, {"LOWER": "left"}],
                allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    # ConTextRule("was", "HISTORICAL", "FORWARD", max_scope=2, allowed_types={"EVIDENCE_OF_HOMELESSNESS", "TEMPORARY_HOUSING"}),
    ConTextRule("in the past N days", "CURRENT",
                pattern=[
                    {"LOWER": "in"},
                    {"LOWER": "the", "OP": "?"},
                    {"LOWER": "past"},
                    {"LIKE_NUM": True},
                    {"LOWER": "days"}
                ]
                ),
    ConTextRule("in the past few days", "CURRENT",
                pattern=[
                    {"LOWER": "in"},
                    {"LOWER": "the", "OP": "?"},
                    {"LOWER": "past"},
                    {"LOWER": "few"},
                    {"LOWER": "days"}
                ]
                ),

    ConTextRule("recently", "CURRENT"),
    ConTextRule("again", "CURRENT", max_scope=2),
    ConTextRule("currently", "CURRENT"),
    ConTextRule("maintain", "CURRENT", allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("current episode", "CURRENT", allowed_types={"EVIDENCE_OF_HOMELESSNESS"}, direction="FORWARD"),

    ConTextRule("worried about", "HYPOTHETICAL", direction="forward"),
    ConTextRule("avoid", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOMELESSNESS"}),
    ConTextRule("looking for", "HYPOTHETICAL", direction="forward",
                pattern=[{"LEMMA": "look"}, {"LOWER": {"IN": ["for", "at", "in"]}}],
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("lead on", "HYPOTHETICAL", direction="forward"),
    ConTextRule("options for", "HYPOTHETICAL", direction="forward", max_scope=5, allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("apply for", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"REGEX": "appl(y|ied|ication)"}}, {"LOWER": {"IN": ["for", "to", "into"]}}],
                allowed_types=["EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"]),
    ConTextRule("submitted application", "HYPOTHETICAL", direction="BIDIRECTIONAL",
                pattern=[{"LEMMA": "submit"}, {"OP": "?"}, {"LEMMA": "application"}]),
    ConTextRule("put in an application", "HYPOTHETICAL", direction="BIDIRECTIONAL",
                allowed_types=["EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"],
                pattern=[
                    {"LOWER": "put"},
                    {"LOWER": "in"},
                    {"OP": "?"},
                    {"LOWER": "application"}
                ]),
    ConTextRule("qualified", "HYPOTHETICAL", direction="BIDIRECTIONAL",
                allowed_types=["EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"],
                pattern=[
                    {"LOWER": {"REGEX": "qualif"}},
                    {"LOWER": "for"},
                ]),
    ConTextRule("eligible for", "HYPOTHETICAL", direction="forward", allowed_types=["EVIDENCE_OF_HOUSING", "HOMELESSNESS_HEALTHCARE_SERVICE"]),
    ConTextRule("in need of", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDNECE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("need", "HYPOTHETICAL", direction="forward", pattern=[{"LEMMA": "needs"}], allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("will be", "HYPOTHETICAL", direction="forward", excluded_types={"RISK_OF_HOMELESSNESS"}),
    ConTextRule("proposed", "HYPOTHETICAL", direction="forward"),
    ConTextRule("propose", "HYPOTHETICAL", direction="forward"),
    ConTextRule("become", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOMELESSNESS", "RISK_OF_HOMELESSNESS"},
                pattern=[{"LOWER": {"IN": ["become", "becomes"]}}],
                max_scope=5),
    ConTextRule("find", "HYPOTHETICAL", direction="forward", pattern=[{"LOWER": {"REGEX": "find"}}],
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("goal", "HYPOTHETICAL", direction="BIDIRECTIONAL", pattern=[{"LOWER": {"REGEX": "^goal"}}], allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("get", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"IN": ["get", "gets", "obtain", "obtains"]}}],
                allowed_types=["EVIDENCE_OF_HOUSING"],
                max_scope=3), # ie., "get his own apartment"
    ConTextRule("forms for", "HYPOTHETICAL", direction="forward"),
    ConTextRule("wants to move", "HYPOTHETICAL", direction="forward"),
    ConTextRule("affordable", "HYPOTHETICAL", direction="bidirectional",
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("request assistance", "HYPOTHETICAL", direction="forward"),
    ConTextRule("assisting with", "HYPOTHETICAL", direction="FORWARD", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"},
                pattern=[{"LEMMA": "assist"}, {"OP": "?"}, {"LOWER": "with"}]),
    ConTextRule("request", "HYPOTHETICAL", direction="forward", pattern=[{"LEMMA": "request"}]),
    ConTextRule("eventually get", "HYPOTHETICAL", direction="forward"),
    ConTextRule("future", "HYPOTHETICAL", direction="forward", max_scope=5),
    ConTextRule("in the future", "HYPOTHETICAL", direction="BIDIRECTIONAL",
                pattern=[
                    {"LOWER": "in"},
                    {"LOWER": "the"},
                    {"POS": "ADJ", "OP": "*"},
                    {"LOWER": "future"}
                ]
                ),
    ConTextRule("near future", "HYPOTHETICAL", direction="BACKWARD", max_scope=5,
                pattern=[
                    {"LOWER": "near"},
                    {"LOWER": "future"}
                ]
                ),
    ConTextRule("qualify for", "HYPOTHETICAL", direction="forward"),
    ConTextRule("able to", "HYPOTHETICAL", direction="forward", max_scope=5, allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("will provide", "HYPOTHETICAL", direction="forward"),
    ConTextRule("once he/she", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOUSING"},
                pattern=[{"LOWER": "once"}, {"LOWER": {"IN": ["he", "she"]}}]),
    ConTextRule("will provide transport", "PSEUDO", direction="PSEUDO",
                pattern=[
                    {"LOWER": "will"},
                    {"LOWER": "provide"},
                    {"LOWER": {"REGEX": "^transport"}}
                ]),
    ConTextRule("preference:", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": "preference"}, {"LOWER": {"IN": [":", "for"]}}],
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("would prefer", "HYPOTHETICAL", "FORWARD", allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("afford", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOUSING"},
                pattern=[{"LOWER": {"REGEX": "^afford"}, "POS": "VERB"}]),
    ConTextRule("suggest", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("will obtain", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOUSING"},
                pattern=[{"LEMMA": "will", "OP": "?"}, {"LOWER": "obtain"}]),
    ConTextRule("discuss", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"},
                pattern=[{"LEMMA": "discuss"}],
                max_scope=5),
    ConTextRule("seeking", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"REGEX": "seek"}}]
                , allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("searching for", "HYPOTHETICAL", direction="forward",
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("search", "HYPOTHETICAL", direction="BIDIRECTIONAL",
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("search options", "HYPOTHETICAL", direction="forward",
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    # ConTextRule("found", "HYPOTHETICAL", allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("look for", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"REGEX": "look"}}, {"LOWER": "for"}]
                , allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("hunt for", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"REGEX": "^hunt"}}, {"LOWER": "for"}]
                , allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("view a X", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"IN": ["view", "see"]}}, {"POS": "DET"}],
                max_scope=1,
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("locate", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"IN": ["locate", "located", "locating"]}}]
                , allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("secure", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"IN": ["secure", "secures", "securing"]}}]),
    ConTextRule("offered", "HYPOTHETICAL", direction="forward"),
    ConTextRule("show", "HYPOTHETICAL", direction="forward", pattern=[{"LEMMA": "show"}], max_scope=5),
    ConTextRule("pending", "HYPOTHETICAL", direction="BIDIRECTIONAL", max_scope=4),
    ConTextRule("eventually", "HYPOTHETICAL", direction="BIDIRECTIONAL", max_scope=6),
    ConTextRule("identified", "HYPOTHETICAL", direction="BIDIRECTIONAL", max_scope=4,
                allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("want", "HYPOTHETICAL", direction="forward",
                pattern=[{"LEMMA": "want"}, {"LOWER": "to", "OP": "?"}],
                allowed_types={"EVIDENCE_OF_HOUSING",}),
    ConTextRule("would like", "HYPOTHETICAL", direction="forward",
                allowed_types=constants.HOUSING_LABELS),
    ConTextRule("hopes", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"IN": ["hope", "hopes", "hopeful"]}}],
                on_modifies=callbacks.hopes_on_modifies,
                allowed_types=constants.HOUSING_LABELS),
    ConTextRule("consider", "HYPOTHETICAL", direction="forward", #max_scope=5,
                allowed_types=constants.HOUSING_LABELS,
                pattern=[{"LOWER": {"REGEX": "consider"}}]),
    ConTextRule("interested in", "HYPOTHETICAL", direction="forward", max_scope=5,
                allowed_types=constants.HOUSING_LABELS),
    ConTextRule("inquire", "HYPOTHETICAL", direction="forward", max_scope=5,
                allowed_types=constants.HOUSING_LABELS),
    ConTextRule("look into", "HYPOTHETICAL", direction="FORWARD", max_scope=5,
                pattern=[{"LOWER": {"REGEX": "look"}}, {"LOWER": "into"}]),
    ConTextRule("does not want to", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"IN": ["does", "do"]}},
                         {"LOWER": "not"},
                         {"LOWER": "want"},
                         {"LOWER": "to", "OP": "?"}]),
    ConTextRule("prevent", "HYPOTHETICAL", direction="forward",
                allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("planing", "HYPOTHETICAL", direction="forward",
                pattern=[{"LOWER": {"REGEX": "plan"}}, {"LOWER": "to", "OP": "?"}],
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("planning", "HYPOTHETICAL", "FORWARD",
                pattern=[{"LOWER": "has"}, {"LEMMA": "plan"}],
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("(housing) plan", "HYPOTHETICAL", direction="BACKWARD",
                pattern=[{"LOWER": "plan"}],
                allowed_types={"EVIDENCE_OF_HOUSING"},
                max_scope=1,
                on_modifies=callbacks.on_modifies_housing_plan),
    ConTextRule("to be", "HYPOTHETICAL", direction="forward", # ie., "to be homeless"
                max_scope=5),
    ConTextRule("desire to be", "HYPOTHETICAL", direction="forward", # ie., "to be homeless"
                max_scope=5),
    ConTextRule("information regarding", "HYPOTHETICAL", direction="forward"),
    ConTextRule("potential", "HYPOTHETICAL", direction="forward"),
    ConTextRule("available", "HYPOTHETICAL", direction="BACKWARD", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"},
                max_scope=2),
    ConTextRule("visit", "HYPOTHETICAL", direction="FORWARD", allowed_types={"EVIDENCE_OF_HOUSING",},
                pattern=[{"LOWER": {"IN": ["visit", "visited"]}}],
                on_match=callbacks.visit_on_match
                # TODO: maybe this should only match specific phrases
                ),
    ConTextRule("move forward", "HYPOTHETICAL", direction="FORWARD", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"},
                pattern=[{"LEMMA": "move"}, {"LOWER": "forward"}],),
    ConTextRule("screened for admission", "HYPOTHETICAL", "FORWARD", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"},
                pattern=[{"LOWER": "screened"}, {"LOWER": "for"}, {"POS": "ADJ", "OP": "?"}, {"LOWER": "admission"}]),
    ConTextRule("screening for", "HYPOTHETICAL", "FORWARD",
                allowed_types={"EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS", "TEMPORARY_HOUSING"},
                pattern=[
                    {"LOWER": {"IN": ["screen", "screened", "screening"]}},
                    {"LOWER": "interview", "OP": "?"},
                    {"LOWER": "for"}
                ]
                ),
    ConTextRule("contact with", "HYPOTHETICAL", "FORWARD", on_modifies=callbacks.contact_with),
    ConTextRule("should be approved", "HYPOTHETICAL", "FORWARD"),

    # TODO: Keep an eye on this, may be too aggressive
    ConTextRule("?", "NOT_RELEVANT", direction="BACKWARD", max_scope=None, on_match=callbacks.disambiguate_question_mark),
    ConTextRule("working definition", "NOT_RELEVANT", direction="BIDIRECTIONAL", max_scope=None), # " as defined by HUD's working definition:"
    ConTextRule("<NUMBERED_LIST>", "LIST", direction="BIDIRECTIONAL", pattern=r"\n *[\d]{1,2}\.\s+[A-Z]"),

    # Risk
    ConTextRule("vulnerable to", "AT_RISK", direction="forward",
                pattern=[{"LOWER": {"REGEX": "vulnerab"}}, {"LOWER": "to"}]),
    ConTextRule("at risk", "AT_RISK", direction="forward"),
    ConTextRule("will become", "HYPOTHETICAL", direction="forward", allowed_types={"EVIDENCE_OF_HOMELESSNESS"}),
    ConTextRule("cannot afford", "AT_RISK", direction="forward",
                pattern=r"can('t|not) (afford|pay)",
                allowed_types={"EVIDENCE_OF_HOUSING"}),
    ConTextRule("fail inspection", "AT_RISK", pattern=[{"LEMMA": "fail"}, {"OP": "?"}, {"LOWER": "inspection"}]),
    ConTextRule("not pass inspection", "AT_RISK"),
    ConTextRule("kicked out", "AT_RISK", direction="BIDIRECTIONAL",
                pattern=[{"LEMMA": "kick"}, {"OP": "?"}, {"LOWER": "out"}]),
    ConTextRule("need for", "AT_RISK", direction="FORWARD"),
    ConTextRule("not found", "AT_RISK", direction="FORWARD"),
    ConTextRule("in jeopardy", "AT_RISK", direction="BIDIRECTIONAL", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("late", "AT_RISK", direction="BIDIRECTIONAL",
                allowed_types={"EVIDENCE_OF_HOUSING"},
                on_modifies=callbacks.on_modifies_pay),
    ConTextRule("AXIS IV", "AT_RISK", "FORWARD"),
    ConTextRule("stressors", "AT_RISK", "FORWARD"),
    ConTextRule("loss of", "AT_RISK", "FORWARD"),
    ConTextRule("loss", "AT_RISK", "BACKWARD", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("lost", "AT_RISK", "BIDIRECTIONAL", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),
    ConTextRule("losing", "AT_RISK", "BIDIRECTIONAL", allowed_types={"EVIDENCE_OF_HOUSING", "TEMPORARY_HOUSING"}),


    # Terminate
    # TODO: I'm not sold on this one
    ConTextRule("as he", "TERMINATE", direction="TERMINATE", # 'not homeless as he has his own apartmentr
                pattern=[{"LOWER": "as"}, {"POS": "PRON"}]),
    ConTextRule("but", "CONJ", direction="TERMINATE"),

    # Ignore
    ConTextRule("plan:", "IGNORE", direction="TERMINATE"),

    # Other
    # ConTextRule("eligible for", "ELIGIBILITY", direction="FORWARD", allowed_types={"HOMELESSNESS_HEALTHCARE_SERVICE"},),
    ConTextRule("resides in", "RESIDES_IN", direction="FORWARD",
                pattern=[
                    {"LOWER": {"IN": ["lives", "living", "resides", "currently", ]}},
                    {"LOWER": "in"},
                ],
                allowed_types={"EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS",  "TEMPORARY_HOUSING", "VA_HOUSING"},
                on_modifies=callbacks.resides_in_on_modifies),
    ConTextRule("was residing in", "PSEUDO", direction="PSEUDO",
                pattern=[
                    {"LOWER": "was"},
                    {"LOWER": {"IN": ["residing", "living"]}},
                    {"LOWER": "in"},
                ],
                allowed_types={"EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS", "TEMPORARY_HOUSING", "VA_HOUSING"},
                ),
    ConTextRule("had been residing in", "PSEUDO", direction="PSEUDO",
                pattern=[
                    {"LOWER": "had"},
                    {"LOWER": {"IN": ["been"]}, "OP": "?"},
                    {"LOWER": {"IN": ["living", "residing", ]}},
                    {"LOWER": "in"},
                ],
                allowed_types={"EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS", "TEMPORARY_HOUSING", "VA_HOUSING"},
                ),
    ConTextRule("resides in", "RESIDES_IN", direction="FORWARD",
                pattern=[
                    {"_": {"concept_tag": "RESIDES"}, "OP": "+"},
                ],
                on_modifies=callbacks.resides_in_on_modifies,
                allowed_types={"EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS", "TEMPORARY_HOUSING", "VA_HOUSING"}),
    ConTextRule("continues to reside in", "RESIDES_IN", # This may be a high-precision modifier
                pattern=[
                    {"LOWER": "continues"},
                    {"LOWER": "to"},
                    {"LOWER": {"IN": ["reside", "live"]}},
                ]),
    ConTextRule("moving into", "RESIDES_IN", "FORWARD",
                pattern=[
                    {"LOWER": {"IN": ["moved", "moving", "transition", "transitioning"]}},
                    {"LOWER": {"IN": ["to", "into"]}}
                ],
                allowed_types={"EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS", "TEMPORARY_HOUSING", "VA_HOUSING"}),
    ConTextRule("sleep in", "SLEEPS_IN",
                pattern=[
                    {"LOWER": {"IN": ["sleep", "sleeps"]}},
                    {"LOWER": {"IN": ["in", "at"]}},

                ]
                ),

    # TODO: Careful that this doesn't mess up instances of living with his family
    # Meant to match "his mother is living in stable housing"
    ConTextRule("<PRON> <FAMILY>", "FAMILY", direction="FORWARD",
                pattern=[
        {"LOWER": {"IN": ["his", "her"]}},
        {"_": {"concept_tag": "FAMILY"}, "OP": "+"},
    ]),

    ConTextRule("was accepted", "ACCEPTED", pattern=[{"LOWER": {"IN": ["was", "been"]}, "OP": "?"}, {"LOWER": "accepted"}, {"LOWER": {"IN": ["to", "into"]}, "OP": "?"}]),
    ConTextRule("approved", "ACCEPTED", rule="FORWARD", pattern=[{"LOWER": "approved"}, {"LOWER": "for", "OP": "?"},]),
    ConTextRule("could be approved", "HYPOTHETICAL", rule="FORWARD"),

    ConTextRule("enrolled", "ENROLLMENT", "FORWARD",
                pattern=[
                    {"LOWER": {"IN": ["enroll", "enrolled"]}},
                    {"LOWER": {"IN": ["in", "into", "participant"]}, "OP": "?"}
                ]),

    ConTextRule("denies any concerns", "POSITIVE_HOUSING", direction="FORWARD",
                pattern=[
                    {"LEMMA": "deny"},
                    {"LOWER": "any"},
                    {"LOWER": {"IN": ["concerns", "issues", "problems"]}},
                ]),
    ConTextRule("is able to afford", "POSITIVE_HOUSING", rule="FORWARD",
                pattern=[
                    {"LEMMA": "be"},
                    {"LOWER": "able"},
                    {"LOWER": "to"},
                    {"LOWER": "afford"},
                ],
                allowed_types={"EVIDENCE_OF_HOUSING",}
                ),
    ConTextRule("no issues with", "POSITIVE_HOUSING", direction="FORWARD",
                pattern=[
                    {"LOWER": {"IN": ["no", "any"]}},
                    {"LOWER": "issues"},
                    {"LOWER": "with"},
                ]),

    ConTextRule("once he is able to afford", "HYPOTHETICAL", rule="FORWARD",
                pattern=[
                    {"LOWER": {"IN": ["once", "when"]}},
                    {"OP": "?"},
                    {"LEMMA": "be", "OP": "?"},
                    {"LOWER": "able"},
                    {"LOWER": "to"},
                    {"LOWER": "afford"},
                ],
                allowed_types={"EVIDENCE_OF_HOUSING",}
                ),

    ConTextRule("pay", "PAYMENT", pattern=[{"LOWER": {"IN": ["pay", "paid", "pays"]}}]),

    ConTextRule("not in danger", "PSEUDO", direction="PSEUDO"),
    ConTextRule("not provided", "PSEUDO", direction="PSEUDO"),



]