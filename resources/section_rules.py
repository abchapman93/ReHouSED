from medspacy.section_detection import SectionRule

section_rules = [
    SectionRule("Medical Problems:", "past_medical_history", pattern=r"medical problems:?\n"),
    SectionRule("DISCHARGE INSTRUCTIONS", "patient_instructions", pattern=r"DISCHARGE INSTRUCTIONS:?\n"),
    SectionRule("Social History", "social_history",
                pattern=[
                    {"LOWER": {"IN": ["social", "soc"]}},
                    {"LOWER": {"IN": ["hx", "history"]}}
                ]
                ),
    SectionRule("Active Problem", "problem_list", pattern=r"\nActive Problem\n"),
    SectionRule("Current housing situation:", "housing_status",
                pattern=[
                    {"LOWER": "current", "OP": "?"},
                    {"LOWER": "housing"},
                    {"LOWER": {"IN": ["situation", "status", "arrangements"]}, "OP": "?"},
                    {"LOWER": ":"},
                ]),
    SectionRule("Living Arrangements:", "housing_status",
        pattern=[
                    {"LOWER": "current", "OP": "?"},
                    {"LOWER": "living"},
                    {"LOWER": {"IN": ["situation", "status", "arrangements"]}, "OP": "?"},
                    {"LOWER": ":"},
                ]),
    SectionRule("Where are you currently living?", "KNOWN_QUESTIONNAIRE"),
    SectionRule("Patient Needs:", "patient_needs"),
    SectionRule("Diagnosis:", "diagnosis"),
    SectionRule("Goals:", "patient_goals"),
    SectionRule("Patient Needs:", "patient_needs"),
    SectionRule("Goals:", "patient_goals", pattern=r"Goals?:"),
    SectionRule("Strengths:", "patient_strengths"),
    SectionRule("Living Arrangements:", "housing_status"),
    SectionRule("Current Housing:", "housing_status"),
    SectionRule("Housing situation", "housing_status", pattern=[{"LOWER": "current", "OP": "?"}, {"LOWER": "living"}, {"LOWER": "situation"}, {"LOWER": ":"}]),
]