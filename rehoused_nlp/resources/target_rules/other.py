from medspacy.ner import TargetRule
from .. import callbacks

other_rules = [
# Healthcare Service
    TargetRule("housing program", "HOMELESSNESS_HEALTHCARE_SERVICE"),
    TargetRule("homelessness prevention", "HOMELESSNESS_HEALTHCARE_SERVICE",
             pattern=[{"LOWER": {"REGEX": "^homeless"}}, {"LOWER": "prevention"}]),
    TargetRule("rapid re-housing", "HOMELESSNESS_HEALTHCARE_SERVICE"),
    TargetRule("rapid rehousing", "HOMELESSNESS_HEALTHCARE_SERVICE"),
    TargetRule("homeless hotline", "HOMELESSNESS_HEALTHCARE_SERVICE"),
    TargetRule("homeless resources", "HOMELESSNESS_HEALTHCARE_SERVICE",
             pattern=[{"LOWER": {"REGEX": "homeless"}}, {"LEMMA": "resource"}]),
    TargetRule("homeless clinic", "HOMELESSNESS_HEALTHCARE_SERVICE"),


# Ignore

    TargetRule("resources for the homeless", "IGNORE"),
    TargetRule("apartment manager", "IGNORE"),
    TargetRule("apartment management", "IGNORE"),
    TargetRule("apartment costs", "IGNORE"),
    TargetRule("housing authority", "IGNORE"),
    TargetRule("housing assistant", "IGNORE"),
    TargetRule("housing specialist", "IGNORE"),
    TargetRule("housing team", "IGNORE"),
    TargetRule("housing plans", "IGNORE"),
    TargetRule("housing process", "IGNORE"),
    TargetRule("homeless program", "IGNORE", pattern=[{"LOWER": {"REGEX": "^homeless"}}, {"LOWER": {"IN": ["program", "programs"]}}]),
    TargetRule("homeless outreach", "IGNORE"),
    TargetRule("homeless team", "IGNORE"),
    TargetRule("homeless staff", "IGNORE"),
    TargetRule("homeless sud worker", "IGNORE"),
    TargetRule("homeless veterans", "IGNORE", pattern=[{"LOWER": "homeless"}, {"LOWER": "veterans"}]),
    TargetRule("homeless women", "IGNORE"),
    TargetRule("homeless people", "IGNORE"),
    TargetRule("homeless call center", "IGNORE"),
    TargetRule("re housing", "IGNORE"),
    TargetRule("affordable housing", "IGNORE"),
    TargetRule("sustainable housing", "IGNORE"),
    TargetRule("housing stability", "IGNORE"), # Often vague or conceptual
    TargetRule("housing access", "IGNORE"), # Often vague or conceptual
    TargetRule("housing arrangement", "IGNORE"), # Not informative
    TargetRule("housing needs", "IGNORE"), # Not informative
    TargetRule("housing choice", "IGNORE", pattern=[{"LOWER": "housing"}, {"LEMMA": "choice"}]), # Not informative
    TargetRule("housing status", "IGNORE"), # Not informative
    TargetRule("housing resources", "IGNORE"), # Not informative
    TargetRule("housing clinic", "IGNORE"), # Not informative
    TargetRule("housing outreach", "IGNORE"),
    TargetRule("housing group", "IGNORE"),
    TargetRule("group home", "IGNORE"),
    TargetRule("discharge to home", "IGNORE", pattern=[{"LOWER": {"IN": ["discharge", "discharged"]}}, {"LOWER": "to"}, {"LOWER": "home"}]),
    TargetRule("homeless case management", "IGNORE"),
    TargetRule("housing authority", "IGNORE"),
    TargetRule("<PRON> housing voucher", "IGNORE",
               pattern=[{"LOWER": {'IN': ["his", "my", "a", "her"]}},
                        {"LOWER": "housing"},
                        {"LOWER": "voucher"}]), # Not informative
    TargetRule("housing voucher", "IGNORE"), # Not informative
    TargetRule("homeless assessment", "IGNORE"), # Not informative
    TargetRule("services for the homeless", "IGNORE"),
    TargetRule("housing situation", "IGNORE"), # Not informative
    TargetRule("<DET> housing situation", "IGNORE",
               pattern=[
                   {"POS": "DET"},
                   {"LOWER": "housing"},
                   {"LOWER": "situation"},
               ]), # Not informative
    TargetRule("Veteran's housing arrangement", "IGNORE"), # Not informative
    TargetRule("housing opportunity", "IGNORE"), # Not informative
    TargetRule("home phone number", "IGNORE",
               pattern=[
                   {"_": {"concept_tag": "PATIENT"}, "OP": "*"},
                   {"LOWER": "home"},
                   {"LOWER": "phone"},
                   {"LOWER": "number", "OP": "?"}
               ]),
    TargetRule("URL", "IGNORE", pattern=[{"LIKE_URL": True}]),

    TargetRule("homeless population", "IGNORE"),


    TargetRule("housing case manager", "IGNORE"),
    TargetRule("pay your rent", "IGNORE"),
    TargetRule("Home Address", "IGNORE"),
    TargetRule("the apartment complex", "IGNORE"),
    TargetRule("homeless veteran team", "IGNORE"),
    TargetRule("house staff", "IGNORE"),
    TargetRule("in-house", "IGNORE", pattern=[{"LOWER": "in"}, {"LOWER": "-", "OP": "?"}, {"LOWER": "house"}]),

    TargetRule("house sitting", "IGNORE", pattern=[
        {"LOWER": {"IN": ["house", "home"]}},
        {"LOWER": "-", "OP": "?"},
        {"LOWER": "sitting"},
    ]),

    # Ignore any tokens with a token._.ignore = True
    TargetRule("IGNORE", "IGNORE", pattern=[{"_": {"ignore": True}, "OP": "+"}]),

]