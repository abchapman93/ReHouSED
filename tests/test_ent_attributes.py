from ..utils import build_nlp

from .helpers import find_ents, _test_label_text, _test_label_texts

import warnings
warnings.filterwarnings("ignore")

nlp = build_nlp()

class TestConcepts:
    def test_historical(self):
        label_texts = {
            "EVIDENCE_OF_HOMELESSNESS": [
                "Lack of Housing", "Z59.0", "Diagnosis: Homelessness",
                "Homeless single person",
                "prior to that he was homeless",
            ]
        }

        _test_label_texts(nlp, label_texts, attrs={"is_historical": True, "is_ignored": False})


    def test_hypothetical(self):
        label_texts = {
            "EVIDENCE_OF_HOUSING": [
                "The patient is looking for an apartment.",
                "She would like an apartment.",
                "He has a goal of looking for housing",
                "obtain housing",
                "interested in housing",
            ],
            "EVIDENCE_OF_HOMELESSNESS": [
                "if he becomes homeless",
            ],

        }

        _test_label_texts(nlp, label_texts, attrs={"is_hypothetical": True, "is_ignored": False})

    def test_negated(self):
        label_texts = {
            "EVIDENCE_OF_HOMELESSNESS": [
                "Homeless: No",
                "Not currently homeless.",
                "not chronically homeless",
            ]
        }

        _test_label_texts(nlp, label_texts, attrs={"is_negated": True, "is_ignored": False})

    def test_ignored(self):
        label_texts = {
            "EVIDENCE_OF_HOMELESSNESS": [
                "() Homeless", # Ignore empty checkmarks
            ],
            "EVIDENCE_OF_HOUSING": [
                "house",
                "home",
                "apartment",
                "Do you live in an apartment?", # Question marks should be ignored
                "landlord", # need more context

            ],
        }

        _test_label_texts(nlp, label_texts, attrs={"is_ignored": True})


    def test_asserted(self):
        label_texts = {
            "EVIDENCE_OF_HOMELESSNESS": [
                "Homeless",
                "chronically homeless",

            ],
            "EVIDENCE_OF_HOUSING": [
                "lives in a house",
                "her apartment",
                "her own apartment",
                "home visit",
                "his landlord",
                "paid security deposit",
                "paid in full the security deposit",

            ],
            "RISK_OF_HOMELESSNESS": [
                "housing need",
            ],

        }
        _test_label_texts(nlp, label_texts, attrs={"is_asserted": True})
